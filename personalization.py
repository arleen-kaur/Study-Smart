import pandas as pd
from database import SessionLocal
from models import TaskLog

def get_user_logs(user_id: int) -> pd.DataFrame:
    db = SessionLocal()
    logs = db.query(TaskLog).filter(TaskLog.user_id == user_id).all()
    db.close()
    if not logs:
        return pd.DataFrame()  # empty DataFrame

    logs_data = []
    for log in logs:
        logs_data.append({
            "task_id": log.task_id,
            "task_description": log.task_description,
            "task_type": log.task_type,
            "scheduled_duration": log.scheduled_duration,
            "actual_duration": log.actual_duration if log.actual_duration is not None else 0,
            "action": log.action
        })

    df = pd.DataFrame(logs_data)
    return df

def preprocess_user_logs(df: pd.DataFrame) -> pd.DataFrame:
    # Create target completed = 1 if action == 'c' else 0
    df['completed'] = (df['action'] == 'c').astype(int)

    # Fill missing task_type
    df['task_type'] = df['task_type'].fillna('Unknown')

    # One-hot encode task_type
    df = pd.get_dummies(df, columns=['task_type'], prefix='task_type')

    # Features for model
    feature_cols = ['scheduled_duration', 'actual_duration'] + [col for col in df.columns if col.startswith('task_type_')]

    X = df[feature_cols]
    # Ensure string column names
    X.columns = X.columns.astype(str)
    return X
