import asyncio
import math
from threading import Lock

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.streaming.stream_processor import StreamProcessor


router = APIRouter()

DEFAULT_INTERVAL = 1.0
MIN_INTERVAL = 0.1
MAX_INTERVAL = 10.0

# Prevent two WebSocket connections from streaming the same battery.
_active_batteries = set()
_active_lock = Lock()


def claim_battery(battery_id):
    with _active_lock:
        if battery_id in _active_batteries:
            return False

        _active_batteries.add(battery_id)
        return True


def release_battery(battery_id):
    with _active_lock:
        _active_batteries.discard(battery_id)


def get_battery_id(batch_number, sheet_name, battery_id=None):
    return battery_id or f"XJTU-B{batch_number}-{sheet_name}"


@router.websocket("/ws/stream")
async def stream_battery(websocket: WebSocket):
    await websocket.accept()

    processor = None
    claimed_battery_id = None
    interval = DEFAULT_INTERVAL

    try:
        batch_number = int(
            websocket.query_params.get("batch_number", 1)
        )
        sheet_name = websocket.query_params.get(
            "sheet_name", "Sheet1"
        )
        battery_id = get_battery_id(
            batch_number,
            sheet_name,
            websocket.query_params.get("battery_id"),
        )

        if batch_number < 1:
            raise ValueError("Batch number must be positive.")

        if not claim_battery(battery_id):
            await websocket.send_json({
                "event": "error",
                "message": (
                    f"Battery '{battery_id}' already has an active "
                    "stream connection."
                ),
            })
            await websocket.close(code=4409)
            return

        claimed_battery_id = battery_id

        # Workbook loading happens outside the async event loop.
        processor = await asyncio.to_thread(
            StreamProcessor,
            batch_number=batch_number,
            sheet_name=sheet_name,
            battery_id=battery_id,
        )

        await websocket.send_json({
            "event": "connected",
            "battery_id": battery_id,
            "message": "Connected to battery stream.",
            "status": processor.get_status(),
        })

        while True:
            if processor.get_status()["status"] == "running":
                try:
                    command = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=interval,
                    )

                except asyncio.TimeoutError:
                    # CNN inference and TwinManager processing happen
                    # outside the async event loop.
                    result = await asyncio.to_thread(
                        processor.process_next
                    )

                    if result is None:
                        await websocket.send_json({
                            "event": "completed",
                            "status": processor.get_status(),
                        })
                        continue

                    await websocket.send_json({
                        "event": "observation",
                        "data": result,
                    })

                    if result["stream_status"]["status"] == "completed":
                        await websocket.send_json({
                            "event": "completed",
                            "status": result["stream_status"],
                        })

                    continue

            else:
                command = await websocket.receive_json()

            if not isinstance(command, dict):
                await websocket.send_json({
                    "event": "error",
                    "message": "Command must be a JSON object.",
                })
                continue

            action = command.get("action")

            if action == "start":
                response = processor.start()

            elif action == "pause":
                response = processor.pause()

            elif action == "resume":
                response = processor.resume()

            elif action == "reset":
                response = processor.reset()

            elif action == "status":
                response = processor.get_status()

            elif action == "set_interval":
                try:
                    new_interval = float(command.get("interval"))

                    if (
                        isinstance(command.get("interval"), bool)
                        or not math.isfinite(new_interval)
                        or not MIN_INTERVAL <= new_interval <= MAX_INTERVAL
                    ):
                        raise ValueError

                    interval = new_interval
                    response = {
                        "status": "success",
                        "interval": interval,
                        "message": "Stream interval updated.",
                    }

                except (TypeError, ValueError):
                    response = {
                        "status": "error",
                        "message": (
                            f"Interval must be between "
                            f"{MIN_INTERVAL} and {MAX_INTERVAL} seconds."
                        ),
                    }

            elif action == "select_battery":
                if processor.get_status()["status"] == "running":
                    response = {
                        "status": "error",
                        "message": (
                            "Pause or stop the stream before "
                            "selecting another battery."
                        ),
                    }

                else:
                    new_batch = int(
                        command.get("batch_number", batch_number)
                    )
                    new_sheet = command.get("sheet_name", sheet_name)

                    new_battery_id = get_battery_id(
                        new_batch,
                        new_sheet,
                        command.get("battery_id"),
                    )

                    if new_batch < 1:
                        response = {
                            "status": "error",
                            "message": "Batch number must be positive.",
                        }

                    elif new_battery_id == claimed_battery_id:
                        response = {
                            "status": "error",
                            "message": (
                                "This battery is already selected. "
                                "Use a newly registered battery ID "
                                "for a fresh replay."
                            ),
                        }

                    elif not claim_battery(new_battery_id):
                        response = {
                            "status": "error",
                            "message": (
                                f"Battery '{new_battery_id}' already "
                                "has an active stream connection."
                            ),
                        }

                    else:
                        try:
                            # Build the new processor before releasing
                            # ownership of the currently selected battery.
                            new_processor = await asyncio.to_thread(
                                StreamProcessor,
                                batch_number=new_batch,
                                sheet_name=new_sheet,
                                battery_id=new_battery_id,
                            )

                            old_battery_id = claimed_battery_id

                            processor = new_processor
                            batch_number = new_batch
                            sheet_name = new_sheet
                            battery_id = new_battery_id
                            claimed_battery_id = new_battery_id

                            release_battery(old_battery_id)

                            response = {
                                "status": "success",
                                "battery_id": battery_id,
                                "message": "Battery selected.",
                            }

                        except Exception as exc:
                            release_battery(new_battery_id)

                            response = {
                                "status": "error",
                                "message": str(exc),
                            }

            else:
                response = {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                }

            await websocket.send_json({
                "event": "command_response",
                "action": action,
                "data": response,
            })

    except WebSocketDisconnect:
        print("Battery streaming client disconnected.")

    except Exception as exc:
        try:
            await websocket.send_json({
                "event": "error",
                "message": str(exc),
            })
        except Exception:
            pass

        print(f"Battery streaming error: {exc}")

    finally:
        if claimed_battery_id is not None:
            release_battery(claimed_battery_id)