import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os
import urllib.request

# ── Dataset setup ────────────────────────────────────────────────────────────
DATA_PATH = "data/raw/ENB2012_data.xlsx"
DATA_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "00242/ENB2012_data.xlsx"
)

os.makedirs("data/raw", exist_ok=True)

if not os.path.exists(DATA_PATH):
    print("Dataset not found. Downloading from UCI repository...")
    urllib.request.urlretrieve(DATA_URL, DATA_PATH)
    print(f"Downloaded to {DATA_PATH}")
else:
    print(f"Dataset found at {DATA_PATH}")

# ── Load & prepare data ───────────────────────────────────────────────────────
data = pd.read_excel(DATA_PATH)

# Drop any fully empty rows/columns the Excel file may contain
data.dropna(how="all", inplace=True)
data = data.loc[:, data.notna().any()]

X = data.iloc[:, :-2]   # 8 input features
# Use the last column (Cooling Load) for classification; bins=3 → 3 classes
y = pd.cut(data.iloc[:, -1], bins=3, labels=[0, 1, 2]).astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Scale & train ─────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

print(f"Test accuracy: {model.score(X_test_scaled, y_test):.4f}")

# ── Save models ───────────────────────────────────────────────────────────────
os.makedirs("backend/models", exist_ok=True)
joblib.dump(model,  "backend/models/model.pkl")
joblib.dump(scaler, "backend/models/scaler.pkl")
print("Model and scaler saved to backend/models/")
