import requests
import json
import os

def log_action(log_data):
    LOG_FILE = "scheduler_log.json"
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            existing_logs = json.load(f)
    else:
        existing_logs = []

    existing_logs.append(log_data)
    with open(LOG_FILE, "w") as f:
        json.dump(existing_logs, f, indent=2)

def run_interactive_scheduler(schedule):
    print("\n Your Study Schedule:\n")
    for i, task in enumerate(schedule):
        print(f"{i+1}. {task['description']} ({task['duration']} mins)")
    print("\nLet's start! Type your action when prompted.\n")

    i = 0
    while i < len(schedule):
        task = schedule[i]
        print(f"\nCurrent task ({i+1}/{len(schedule)}): {task['description']} ({task['duration']} mins)")
        action = input("Choose action: [c]omplete, [s]kip, [d]efer, [e]xtend: ").strip().lower()

        if action not in ['c', 's', 'd', 'e']:
            print("Invalid input. Please enter c, s, d, or e.")
            continue

        log_entry = {
            "task_index": i,
            "task_description": task['description'],
            "task_duration": task['duration'],
            "action": action
        }

        if action == 'c':
            print(f"Completed task: {task['description']}")
            log_action(log_entry)
            i += 1
        elif action == 's':
            print(f"Skipped task: {task['description']}")
            log_action(log_entry)
            i += 1
        elif action == 'd':
            print(f"Deferred task: {task['description']}")
            log_action(log_entry)
            schedule.append(schedule.pop(i))
        elif action == 'e':
            try:
                extra = int(input("How many extra minutes to add? "))
                if extra < 0:
                    print("Extra minutes must be positive.")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                continue
            task['duration'] += extra
            print(f"Extended task to {task['duration']} minutes.")
            log_entry['extended_by'] = extra
            log_action(log_entry)

    print("\n All tasks handled! Your session is complete.")
    print("Your session logs have been saved.")

def get_schedule_from_backend(raw_tasks_text, available_time_minutes=120):
    url = "http://127.0.0.1:8000/parse-tasks"
    payload = {
        "raw_tasks_text": raw_tasks_text,
        "available_time_minutes": available_time_minutes
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()['schedule']

if __name__ == "__main__":
    print("Welcome to the Interactive Study Scheduler!")
    raw_tasks = input("Enter your tasks (e.g., 'do 2 homework assignments, watch a video'): ")
    available_time = input("Enter your available time in minutes (default 120): ").strip()
    available_time = int(available_time) if available_time.isdigit() else 120

    try:
        schedule = get_schedule_from_backend(raw_tasks, available_time)
        run_interactive_scheduler(schedule)
    except Exception as e:
        print("Error:", e)
