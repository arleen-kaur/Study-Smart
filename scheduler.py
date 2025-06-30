from collections import deque

def chunk_task(task, max_chunk_length=25):
    total_time = task['estimated_duration_minutes']
    chunks = []
    remaining_time = total_time
    part = 1

    while remaining_time > 0:
        chunk_duration = min(max_chunk_length, remaining_time)
        chunks.append({
            "task_id": task["task_id"],  # ✅ Preserve task_id
            "description": f"{task['description']} (Part {part})",
            "subject": task['subject'],
            "task_type": task['task_type'],
            "duration": chunk_duration
        })
        remaining_time -= chunk_duration
        part += 1

    return chunks

def schedule_tasks_cognitive(parsed_tasks, available_time_minutes):
    chunk_queues = []
    for task in parsed_tasks:
        chunks = chunk_task(task)
        chunk_queues.append(deque(chunks))

    schedule = []
    time_used = 0

    while chunk_queues and time_used < available_time_minutes:
        for queue in list(chunk_queues):
            if not queue:
                chunk_queues.remove(queue)
                continue

            chunk = queue.popleft()

            if time_used + chunk['duration'] > available_time_minutes:
                print("⏳ Reached available time limit. Stopping schedule.")
                return schedule

            schedule.append(chunk)
            time_used += chunk['duration']

            if time_used + 5 <= available_time_minutes:
                schedule.append({
                    "description": "Take a short break",
                    "subject": None,
                    "task_type": "Break",
                    "duration": 5
                })
                time_used += 5

    return schedule
