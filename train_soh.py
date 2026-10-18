
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

from preprocessing.feature_scaler import FeatureScaler
from models.soh_predictor import SOHTrainingModel


# --------------------------------------------------
# Configuration
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent
DATA_FILE = (
    ROOT
    / "reference"
    / "SOHbenchmark"
    / "data"
    / "XJTU"
    / "handcraft_features"
    / "batch-1_features.xlsx"
)

MODEL_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results" / "clean_xjtu_batch1"

TEST_BATTERY_ID = 1
RANDOM_SEED = 2023
BATCH_SIZE = 64
EPOCHS = 100
LEARNING_RATE = 0.002
WEIGHT_DECAY = 5e-4
PATIENCE = 15
MAX_CAPACITY = 2.0

DEVICE = torch.device("cpu")


# --------------------------------------------------
# Reproducibility
# --------------------------------------------------

np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

def load_batteries():
    if not DATA_FILE.is_file():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    sheets = pd.read_excel(DATA_FILE, sheet_name=None)
    batteries = []

    expected_columns = list(next(iter(sheets.values())).columns)

    for battery_id, (_, df) in enumerate(sheets.items(), start=1):
        if list(df.columns) != expected_columns:
            raise ValueError(
                f"Battery {battery_id} has inconsistent columns."
            )

        X = df.iloc[:, :-1].to_numpy(dtype=np.float32)
        capacity = df["label"].to_numpy(dtype=np.float32)

        if not np.isfinite(X).all() or not np.isfinite(capacity).all():
            raise ValueError(
                f"Battery {battery_id} contains invalid values."
            )

        y = capacity / MAX_CAPACITY
        batteries.append((battery_id, X, y))

    return batteries


# --------------------------------------------------
# Prepare training, validation, and test data
# --------------------------------------------------

def prepare_data(batteries):
    train_X_parts = []
    train_y_parts = []
    test_X = None
    test_y = None

    for battery_id, X, y in batteries:
        if battery_id == TEST_BATTERY_ID:
            test_X = X
            test_y = y
        else:
            train_X_parts.append(X)
            train_y_parts.append(y)

    if test_X is None:
        raise ValueError("Requested test battery was not found.")

    X_remaining = np.concatenate(train_X_parts, axis=0)
    y_remaining = np.concatenate(train_y_parts, axis=0)

    # Split by samples, reproducing the reference experiment's
    # sample-level validation approach among the remaining batteries.
    indices = np.arange(len(y_remaining))
    train_indices, valid_indices = train_test_split(
        indices,
        test_size=0.2,
        random_state=RANDOM_SEED,
        shuffle=True,
    )

    X_train = X_remaining[train_indices]
    y_train = y_remaining[train_indices]

    X_valid = X_remaining[valid_indices]
    y_valid = y_remaining[valid_indices]

    # Fit only on training samples. Never fit on validation or test data.
    scaler = FeatureScaler()
    X_train = scaler.fit_transform(X_train)
    X_valid = scaler.transform(X_valid)
    X_test = scaler.transform(test_X)

    return (
        X_train, y_train,
        X_valid, y_valid,
        X_test, test_y,
        scaler,
    )


# --------------------------------------------------
# Training and evaluation
# --------------------------------------------------

def make_loader(X, y, shuffle=False):
    dataset = TensorDataset(
        torch.from_numpy(np.asarray(X, dtype=np.float32)),
        torch.from_numpy(np.asarray(y, dtype=np.float32).reshape(-1, 1)),
    )
    return DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=shuffle,
    )


def evaluate(model, loader, criterion):
    model.eval()
    total_loss = 0.0
    predictions = []
    actual = []

    with torch.no_grad():
        for X, y in loader:
            pred = model(X)
            loss = criterion(pred, y)

            total_loss += loss.item() * len(y)
            predictions.append(pred.numpy())
            actual.append(y.numpy())

    predictions = np.concatenate(predictions).reshape(-1)
    actual = np.concatenate(actual).reshape(-1)

    return total_loss / len(actual), actual, predictions


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    batteries = load_batteries()

    (
        X_train, y_train,
        X_valid, y_valid,
        X_test, y_test,
        scaler,
    ) = prepare_data(batteries)

    print("Dataset:", DATA_FILE.name)
    print("Held-out battery:", TEST_BATTERY_ID)
    print("Training samples:", len(y_train))
    print("Validation samples:", len(y_valid))
    print("Test samples:", len(y_test))
    print("Feature count:", X_train.shape[1])

    train_loader = make_loader(X_train, y_train, shuffle=True)
    valid_loader = make_loader(X_valid, y_valid)
    test_loader = make_loader(X_test, y_test)

    model = SOHTrainingModel().to(DEVICE)
    
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    best_valid_loss = float("inf")
    best_state = None
    best_epoch = 0
    epochs_without_improvement = 0
    history = []

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_train_loss = 0.0

        for X, y in train_loader:
            optimizer.zero_grad()
            pred = model(X)
            loss = criterion(pred, y)
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item() * len(y)

        train_loss = total_train_loss / len(y_train)
        valid_loss, _, _ = evaluate(model, valid_loader, criterion)

        history.append({
            "epoch": epoch,
            "train_mse": train_loss,
            "valid_mse": valid_loss,
        })

        print(
            f"Epoch {epoch:03d}/{EPOCHS} | "
            f"Train MSE: {train_loss:.6f} | "
            f"Validation MSE: {valid_loss:.6f}"
        )

        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            best_state = {
                key: value.detach().cpu().clone()
                for key, value in model.state_dict().items()
            }
            best_epoch = epoch
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= PATIENCE:
            print("Early stopping.")
            break

    if best_state is None:
        raise RuntimeError("Training did not produce a valid checkpoint.")

    model.load_state_dict(best_state)

    # Evaluate the held-out battery only after training is complete.
    _, y_true, y_pred = evaluate(model, test_loader, criterion)

    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mse = float(np.mean((y_true - y_pred) ** 2))

    checkpoint_path = MODEL_DIR / "soh_cnn_xjtu_batch1_clean.pt"

    torch.save(
        {
            "pre_net": model.pre_net.state_dict(),
            "backbone": model.backbone.state_dict(),
            "feature_min": scaler.min_,
            "feature_max": scaler.max_,
            "test_battery_id": TEST_BATTERY_ID,
            "best_epoch": best_epoch,
            "validation_mse": best_valid_loss,
        },
        checkpoint_path,
    )

    pd.DataFrame(history).to_csv(
        RESULTS_DIR / "training_history.csv",
        index=False,
    )

    np.savez(
        RESULTS_DIR / "test_predictions.npz",
        y_true=y_true,
        y_pred=y_pred,
        mae=mae,
        mse=mse,
        rmse=rmse,
    )

    summary = (
        f"Test battery: {TEST_BATTERY_ID}\n"
        f"Training samples: {len(y_train)}\n"
        f"Validation samples: {len(y_valid)}\n"
        f"Test samples: {len(y_test)}\n"
        f"Best epoch: {best_epoch}\n"
        f"Best validation MSE: {best_valid_loss:.6f}\n"
        f"Test MAE: {mae:.6f}\n"
        f"Test MSE: {mse:.6f}\n"
        f"Test RMSE: {rmse:.6f}\n"
    )

    (RESULTS_DIR / "summary.txt").write_text(
        summary,
        encoding="utf-8",
    )

    print("\n", summary)
    print("Checkpoint saved to:", checkpoint_path)
    print("Results saved to:", RESULTS_DIR)


if __name__ == "__main__":
    main()
