
from pathlib import Path

import torch
import torch.nn as nn


# Residual block from the SOHbenchmark CNN architecture
class ResBlock(nn.Module):
    def __init__(self, input_channel, output_channel, stride):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv1d(
                input_channel, output_channel,
                kernel_size=3, stride=stride, padding=1
            ),
            nn.BatchNorm1d(output_channel),
            nn.ReLU(),
            nn.Conv1d(
                output_channel, output_channel,
                kernel_size=3, stride=1, padding=1
            ),
            nn.BatchNorm1d(output_channel),
        )

        self.skip_connection = nn.Sequential()

        if output_channel != input_channel:
            self.skip_connection = nn.Sequential(
                nn.Conv1d(
                    input_channel, output_channel,
                    kernel_size=1, stride=stride
                ),
                nn.BatchNorm1d(output_channel),
            )

        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.conv(x)
        out = self.skip_connection(x) + out
        return self.relu(out)


# CNN architecture matching the reference checkpoint
class CNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.layer1 = ResBlock(4, 16, 1)
        self.layer2 = ResBlock(16, 32, 2)
        self.layer3 = ResBlock(32, 64, 2)
        self.layer4 = ResBlock(64, 96, 2)
        self.layer5 = ResBlock(96, 128, 2)

        self.predictor = nn.Sequential(
            nn.Linear(128 * 8, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5(x)
        return self.predictor(x.reshape(x.size(0), -1))


class SOHTrainingModel(nn.Module):
    """CNN model used to train a new SOH checkpoint."""

    def __init__(self):
        super().__init__()
        self.pre_net = nn.Linear(67, 128 * 4)
        self.backbone = CNN()

    def forward(self, features):
        if features.ndim != 2 or features.shape[1] != 67:
            raise ValueError(
                "Expected input shape (number_of_samples, 67)."
            )

        x = self.pre_net(features)
        x = x.reshape(-1, 4, 128)
        return self.backbone(x)


  
class SOHPredictor(nn.Module):
    """Predict SOH using a trained CNN checkpoint."""

    def __init__(self, checkpoint_path=None):
        super().__init__()

        self.pre_net = nn.Linear(67, 128 * 4)
        self.backbone = CNN()

        if checkpoint_path is None:
            checkpoint_path = (
                Path(__file__).resolve().parent
                / "soh_cnn_xjtu_batch1_clean.pt"
            )

        checkpoint_path = Path(checkpoint_path)

        if not checkpoint_path.is_file():
            raise FileNotFoundError(
                f"Model checkpoint not found: {checkpoint_path}"
            )

        checkpoint = torch.load(
            checkpoint_path,
            map_location="cpu",
            weights_only=False,
        )

        self.pre_net.load_state_dict(checkpoint["pre_net"])
        self.backbone.load_state_dict(checkpoint["backbone"])

        # The clean checkpoint includes training-only scaler parameters.
        self.feature_min = checkpoint.get("feature_min")
        self.feature_max = checkpoint.get("feature_max")

        if self.feature_min is not None:
            self.feature_min = torch.as_tensor(
                self.feature_min, dtype=torch.float32
            )
            self.feature_max = torch.as_tensor(
                self.feature_max, dtype=torch.float32
            )

        self.eval()

    def forward(self, features):
        if features.ndim != 2 or features.shape[1] != 67:
            raise ValueError(
                "Expected input shape (number_of_samples, 67)."
            )

        x = self.pre_net(features)
        x = x.reshape(-1, 4, 128)
        return self.backbone(x)

    def normalize_features(self, features):
        """Apply the scaler parameters saved with the clean checkpoint."""
        if self.feature_min is None or self.feature_max is None:
            raise RuntimeError(
                "This checkpoint has no saved scaler parameters."
            )

        if not isinstance(features, torch.Tensor):
            features = torch.as_tensor(
                features, dtype=torch.float32
            )

        if features.ndim != 2 or features.shape[1] != 67:
            raise ValueError(
                "Expected input shape (number_of_samples, 67)."
            )

        if not torch.isfinite(features).all():
            raise ValueError("Features contain NaN or infinite values.")

        denominator = self.feature_max - self.feature_min
        denominator = torch.where(
            denominator == 0,
            torch.ones_like(denominator),
            denominator,
        )

        return (
            2.0 * (features - self.feature_min) / denominator - 1.0
        )

    
    @torch.no_grad()
    def predict(self, features):
        """Predict SOH from raw 67-feature inputs."""
        self.eval()

        normalized = self.normalize_features(features)
        predictions = self.forward(normalized)

        return predictions.squeeze(-1)



    def forward(self, features):
        if features.ndim != 2 or features.shape[1] != 67:
            raise ValueError(
                "Expected input shape (number_of_samples, 67)."
            )

        x = self.pre_net(features)
        x = x.reshape(-1, 4, 128)
        return self.backbone(x)

    