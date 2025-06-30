import sqlite3
import pandas as pd

def export_and_process_logs(db_path='study_smart.db'):  # Update with your DB filename
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM task_logs", conn)

    # Create 'completed' target: 'c' means completed
    df['completed'] = (df['action'] == 'c').astype(int)

    # One-hot encode 'task_type'
    df = pd.get_dummies(df, columns=['task_type'], prefix='task_type')

    # Fill NaNs in actual_duration with scheduled_duration or 0
    df['actual_duration'] = df['actual_duration'].fillna(df['scheduled_duration']).fillna(0)

    # Select columns for model training
    cols = ['scheduled_duration', 'actual_duration', 'completed'] + \
           [col for col in df.columns if col.startswith('task_type_')]

    df_final = df[cols]

    df_final.to_csv('task_logs_processed.csv', index=False)
    print("Exported processed logs to task_logs_processed.csv")

if __name__ == "__main__":
    export_and_process_logs()
