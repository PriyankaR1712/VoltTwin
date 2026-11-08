
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.streaming.stream_processor import StreamProcessor


router = APIRouter()

DEFAULT_INTERVAL = 1.0
MIN_INTERVAL = 0.1
MAX_INTERVAL = 10.0


@router.websocket("/ws/stream")
async def stream_battery(websocket: WebSocket):
    await websocket.accept()

    processor = None
    interval = DEFAULT_INTERVAL

    try:
        # Read initial battery selection from connection parameters.
        batch_number = int(
            websocket.query_params.get("batch_number", 1)
        )
        sheet_name = websocket.query_params.get("sheet_name", "Sheet1")
        battery_id = websocket.query_params.get("battery_id")

        processor = StreamProcessor(
            batch_number=batch_number,
            sheet_name=sheet_name,
            battery_id=battery_id,
        )

        await websocket.send_json({
            "type": "connected",
            "message": "Battery streaming connection established.",
            "battery_id": processor.battery_id,
            "interval": interval,
            "status": processor.get_status(),
        })

        while True:
            try:
                # While running, wait for a command or the next
                # observation interval.
                if processor.get_status()["status"] == "running":
                    command = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=interval,
                    )
                else:
                    command = await websocket.receive_json()

            except asyncio.TimeoutError:
                # No command arrived: send the next observation.
                result = processor.process_next()

                if result is None:
                    await websocket.send_json({
                        "type": "completed",
                        "status": processor.get_status(),
                        "message": "All observations have been streamed.",
                    })
                    continue

                await websocket.send_json({
                    "type": "observation",
                    "data": result,
                })

                if result["stream_status"]["status"] == "completed":
                    await websocket.send_json({
                        "type": "completed",
                        "status": processor.get_status(),
                        "message": "All observations have been streamed.",
                    })

                continue

            if not isinstance(command, dict):
                await websocket.send_json({
                    "type": "error",
                    "message": "Commands must be JSON objects.",
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

            elif action == "set_interval":
                new_interval = command.get("interval")

                if (
                    isinstance(new_interval, bool)
                    or not isinstance(new_interval, (int, float))
                    or not MIN_INTERVAL <= new_interval <= MAX_INTERVAL
                ):
                    await websocket.send_json({
                        "type": "error",
                        "message": (
                            f"Interval must be between "
                            f"{MIN_INTERVAL} and {MAX_INTERVAL} seconds."
                        ),
                    })
                    continue

                interval = float(new_interval)
                response = {
                    "status": "success",
                    "message": "Streaming interval updated.",
                    "interval": interval,
                }

            elif action == "select_battery":
                if processor.get_status()["status"] == "running":
                    await websocket.send_json({
                        "type": "error",
                        "message": "Pause the stream before selecting another battery.",
                    })
                    continue

                new_batch = command.get("batch_number", 1)
                new_sheet = command.get("sheet_name", "Sheet1")
                new_battery_id = command.get("battery_id")

                try:
                    new_processor = StreamProcessor(
                        batch_number=int(new_batch),
                        sheet_name=new_sheet,
                        battery_id=new_battery_id,
                    )
                    processor = new_processor

                    response = {
                        "status": "success",
                        "message": "Battery selection updated.",
                        "battery_id": processor.battery_id,
                    }

                except (ValueError, FileNotFoundError, IndexError) as exc:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(exc),
                    })
                    continue

            elif action == "status":
                response = processor.get_status()

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action: {action}",
                })
                continue

            await websocket.send_json({
                "type": "command_response",
                "action": action,
                "data": response,
            })

    except WebSocketDisconnect:
        print("Battery streaming client disconnected.")

    except Exception as exc:
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(exc),
            })
        except Exception:
            pass

        print(f"Streaming error: {exc}")

