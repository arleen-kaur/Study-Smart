import pandas as pd
from sklearn.multioutput import MultiOutputClassifier
from sklearn.linear_model import LogisticRegression
import joblib

df = pd.read_csv('task_logs_processed.csv')

X = df.drop(columns=['action_completed', 'action_deferred', 'action_skipped', 'action_extended'])
y = df[['action_completed', 'action_deferred', 'action_skipped', 'action_extended']]

model = MultiOutputClassifier(LogisticRegression(max_iter=1000))

model.fit(X, y)

joblib.dump(model, "multioutput_model.pkl")
print("Model trained and saved successfully.")

feature_names = list(X.columns)
joblib.dump(feature_names, 'model_feature_names.pkl')
