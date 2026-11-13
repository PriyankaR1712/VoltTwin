from scipy.io import loadmat
import pandas as pd
import numpy as np

d = loadmat(
    r"reference\SOHbenchmark\data\XJTU\charge\batch-1.mat",
    squeeze_me=True,
    struct_as_record=False
)

raw = d["battery"][0].cycles

f = pd.read_excel(
    r"reference\SOHbenchmark\data\XJTU\handcraft_features\batch-1_features.xlsx",
    sheet_name=0
)

errors = []

for i, c in enumerate(raw):
    ix = np.where(
        (c.voltage_V >= 4.19) & (c.current_A < 3.99)
    )[0][0]

    t = c.relative_time_min[:ix+1]
    v = c.voltage_V[:ix+1]
    current = c.current_A[:ix+1]

    energy = np.trapezoid(v * current, t) / 60

    errors.append(abs(energy - f.iloc[i].CC_energy))

print("Direct raw CC_energy MAE:", np.mean(errors))
print("Maximum error:", np.max(errors))