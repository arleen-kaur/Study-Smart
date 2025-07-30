from models import TaskLog
from database import SessionLocal
from datetime import datetime

def log_action_db(user_id, task, action, extended_by=None):
    db = SessionLocal()

    actual_duration = task['duration']
    if extended_by:
        actual_duration += extended_by

    log = TaskLog(
        user_id=user_id,
        task_id=task.get('task_id'),  # Save task_id for traceability
        task_description=task['description'],
        task_type=task.get('task_type', 'Unknown'),
        scheduled_duration=task['duration'],
        actual_duration=actual_duration,
        action=action,
        timestamp=datetime.utcnow()
    )

    db.add(log)
    db.commit()
    db.close()
