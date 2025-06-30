import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./study_smart.db"

def load_task_logs():
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql_table("task_logs", con=engine)
    return df

def preprocess_and_feature_engineer(df):
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Fill missing values if any
    df.fillna({'actual_duration': 0, 'task_type': 'Unknown'}, inplace=True)

    # Create 'completed' target: mark 'c' action as completed=1, else 0
    df['completed'] = (df['action'] == 'c').astype(int)

    # One-hot encode task_type
    task_type_dummies = pd.get_dummies(df['task_type'], prefix='task_type')
    df = pd.concat([df, task_type_dummies], axis=1)

    # Group by user_id and action to count how many times each action occurred per user
    action_counts = df.groupby(['user_id', 'action']).size().unstack(fill_value=0)
    action_counts.columns = [f'action_count_{col}' for col in action_counts.columns]

    # Average actual_duration per user and per task_type
    avg_duration = df.groupby(['user_id', 'task_type'])['actual_duration'].mean().unstack(fill_value=0)
    avg_duration.columns = [f'avg_duration_{col}' for col in avg_duration.columns]

    # Total number of tasks per user
    total_tasks = df.groupby('user_id').size().rename('total_tasks')

    # Combine all features into one DataFrame keyed by user_id
    features = action_counts.join(avg_duration, how='outer').join(total_tasks, how='outer')
    features.fillna(0, inplace=True)

    return features

def main():
    print("Loading task logs from database...")
    df_logs = load_task_logs()
    print(f"Loaded {len(df_logs)} rows.")

    print("Performing feature engineering...")
    features = preprocess_and_feature_engineer(df_logs)
    print("Feature engineering done. Sample:")
    print(features.head())

    features.to_csv("processed_task_features.csv")
    print("Saved processed features to 'processed_task_features.csv'")

if __name__ == "__main__":
    main()
