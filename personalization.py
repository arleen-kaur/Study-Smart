import pandas as pd
import numpy as np
import joblib
from database import SessionLocal
from models import TaskLog
from datetime import datetime

MODEL_FEATURES = joblib.load("model_feature_names.pkl")
model = joblib.load("multioutput_model.pkl")

TASK_TYPE_MAP = {
    "essay": "writing",
    "essay_writing": "writing",
    "project_work": "project",
    "video": "video_watching",
    "video watching": "video_watching",
    "coding": "problem_solving",
    "problem solving": "problem_solving",
    "hw": "homework",
    "leetcode": "problem_solving"
}

def normalize_task_type(task_type: str) -> str:
    key = task_type.strip().lower().replace(" ", "_")
    return TASK_TYPE_MAP.get(key, key)

def get_user_logs(user_id: int) -> pd.DataFrame:
    db = SessionLocal()
    logs = db.query(TaskLog).filter(TaskLog.user_id == user_id).order_by(TaskLog.timestamp.desc()).all()
    db.close()

    if not logs:
        return pd.DataFrame()

    logs_data = [{
        "task_id": log.task_id,
        "task_description": log.task_description,
        "task_type": normalize_task_type(log.task_type or "unknown"),
        "scheduled_duration": log.scheduled_duration,
        "actual_duration": log.actual_duration or 0,
        "action": log.action,
        "timestamp": log.timestamp
    } for log in logs]

    return pd.DataFrame(logs_data)

def preprocess_user_logs(df: pd.DataFrame):
    df["task_type"] = df["task_type"].apply(normalize_task_type)
    df["actual_duration"] = df["actual_duration"].fillna(df["scheduled_duration"]).fillna(0)

    now = datetime.utcnow()
    df["days_ago"] = (now - df["timestamp"]).dt.days
    df["recency_weight"] = np.exp(-0.1 * df["days_ago"])

    task_type_dummies = pd.get_dummies(df["task_type"], prefix="task_type")
    df_features = pd.concat([df[["scheduled_duration", "actual_duration"]], task_type_dummies], axis=1)

    for col in MODEL_FEATURES:
        if col not in df_features.columns:
            df_features[col] = 0

    df_features = df_features[MODEL_FEATURES]

    return df_features, df["recency_weight"]

def compute_task_priority_scores(features_df: pd.DataFrame, recency_weights: pd.Series) -> pd.Series:
    global model

    prob_scores = []
    for estimator in model.estimators_:
        if hasattr(estimator, "predict_proba"):
            proba = estimator.predict_proba(features_df)
            scores = proba[:, 1]
        else:
            scores = estimator.predict(features_df)
        prob_scores.append(scores)

    df_scores = pd.DataFrame(prob_scores).T

    combined_score = (
        df_scores.iloc[:, 0]          
        - 0.5 * df_scores.iloc[:, 2]  
        - 0.3 * df_scores.iloc[:, 1]  
        - 0.1 * df_scores.iloc[:, 3]   
    )

    combined_score *= recency_weights.values

    return combined_score
