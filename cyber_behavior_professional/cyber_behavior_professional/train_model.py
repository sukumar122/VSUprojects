
import pandas as pd, numpy as np, joblib, os
from sklearn.ensemble import IsolationForest

os.makedirs("model",exist_ok=True)

np.random.seed(42)
data=pd.DataFrame({
    "login_hour":np.random.randint(8,20,500),
    "session_duration":np.random.randint(5,60,500),
    "failed_attempts":np.random.randint(0,3,500)
})

model=IsolationForest(contamination=0.1)
model.fit(data)

joblib.dump(model,"model/cyber_model.pkl")
print("Professional model trained and saved.")
