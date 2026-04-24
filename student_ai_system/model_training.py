import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error

# Load dataset
data = pd.read_csv("data/student_data.csv")
print("Features:", data.columns.tolist())

# Features and Targets
X = data.drop(["dropout", "gpa"], axis=1)
y_dropout = data["dropout"]
y_gpa = data["gpa"]

# Train-test split
X_train, X_test, y_train_dropout, y_test_dropout = train_test_split(
    X, y_dropout, test_size=0.2, random_state=42
)

_, _, y_train_gpa, y_test_gpa = train_test_split(
    X, y_gpa, test_size=0.2, random_state=42
)

# Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Models
clf = RandomForestClassifier(n_estimators=100, random_state=42)
reg = RandomForestRegressor(n_estimators=100, random_state=42)

# Train models
clf.fit(X_train_scaled, y_train_dropout)
reg.fit(X_train_scaled, y_train_gpa)

# Predictions
dropout_pred = clf.predict(X_test_scaled)
gpa_pred = reg.predict(X_test_scaled)

print("Dropout Accuracy:", accuracy_score(y_test_dropout, dropout_pred))
print("GPA MSE:", mean_squared_error(y_test_gpa, gpa_pred))

# Save models
joblib.dump(clf, "dropout_model.pkl")
joblib.dump(reg, "gpa_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Models saved successfully!")
