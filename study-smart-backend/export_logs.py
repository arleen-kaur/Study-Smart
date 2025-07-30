import sqlite3
import pandas as pd

def export_and_process_logs(db_path='study_smart.db'):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM task_logs", conn)

    print("Unique task types before cleanup:", df['task_type'].unique())

    df['task_type'] = df['task_type'].fillna('unknown').str.lower().str.replace(' ', '_')

    print("Unique task types after cleanup:", df['task_type'].unique())

    task_type_dummies = pd.get_dummies(df['task_type'], prefix='task_type')

    print("Task type dummy columns:", task_type_dummies.columns.tolist())

    df['action_completed'] = (df['action'] == 'c').astype(int)
    df['action_deferred'] = (df['action'] == 'd').astype(int)
    df['action_skipped'] = (df['action'] == 's').astype(int)
    df['action_extended'] = (df['action'] == 'e').astype(int)

    df['actual_duration'] = df['actual_duration'].fillna(df['scheduled_duration']).fillna(0)

    features = ['scheduled_duration', 'actual_duration']

    df_final = pd.concat([df[features], task_type_dummies,
                          df[['action_completed', 'action_deferred', 'action_skipped', 'action_extended']]], axis=1)

    print("Columns in final DataFrame:", df_final.columns.tolist())

    df_final.to_csv('task_logs_processed.csv', index=False)
    print("Exported cleaned processed logs to task_logs_processed.csv")

if __name__ == "__main__":
    export_and_process_logs()
