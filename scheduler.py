from collections import deque

def chunk_task(task, max_chunk_length=25):
    priority = task.get("priority_score", 0)

    chunk_length = max(10, min(max_chunk_length, int(priority * max_chunk_length)))
    
    if task.get("must_do", False):
        chunk_length = min(chunk_length, 15)

    total_time = task['estimated_duration_minutes']
    chunks = []
    remaining_time = total_time
    part = 1

    while remaining_time > 0:
        chunk_duration = min(chunk_length, remaining_time)
        chunks.append({
            "task_id": task["task_id"],
            "description": f"{task['description']} (Part {part})",
            "subject": task['subject'],
            "task_type": task['task_type'],
            "duration": chunk_duration,
            "priority_score": priority,
            "must_do": task.get("must_do", False)
        })
        remaining_time -= chunk_duration
        part += 1

    return chunks


def schedule_tasks_cognitive(parsed_tasks, available_time_minutes):
    parsed_tasks = sorted(
        parsed_tasks,
        key=lambda t: (t.get("must_do", False), t.get("priority_score", 0)),
        reverse=True
    )

    chunk_queues = []
    for task in parsed_tasks:
        chunks = chunk_task(task)
        chunk_queues.append(deque(chunks))

    schedule = []
    time_used = 0
    break_duration = 5
    work_since_last_break = 0

    while chunk_queues and time_used < available_time_minutes:
        for queue in list(chunk_queues):  
            if not queue:
                chunk_queues.remove(queue)
                continue

            chunk = queue.popleft()

            if time_used + chunk['duration'] > available_time_minutes:
                return schedule

            schedule.append(chunk)
            time_used += chunk['duration']
            work_since_last_break += chunk['duration']

            if work_since_last_break >= 25 and time_used + break_duration <= available_time_minutes:
                schedule.append({
                    "description": "Take a short break",
                    "subject": None,
                    "task_type": "break",
                    "duration": break_duration
                })
                time_used += break_duration
                work_since_last_break = 0

    return schedule
