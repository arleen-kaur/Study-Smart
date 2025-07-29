import requests
from log_utils import log_action_db 

BASE_URL = "http://127.0.0.1:8000"

def signup(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    if response.status_code == 400:
        print("⚠️ User already exists, continuing to login.")
    elif response.status_code == 201:
        print("✅ User registered successfully.")
    else:
        response.raise_for_status()

def login(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/auth/login", data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_user_info(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/userinfo", headers=headers)
    response.raise_for_status()
    return response.json()

def get_schedule_from_backend(token, raw_tasks_text, available_time_minutes=120):
    url = f"{BASE_URL}/personalized-schedule"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "raw_tasks_text": raw_tasks_text,
        "available_time_minutes": available_time_minutes
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()['schedule']

def run_interactive_scheduler(schedule, user_id):
    print("\nYour Study Schedule:\n")
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

        extended_by = None
        if action == 'e':
            try:
                extra = int(input("How many extra minutes to add? "))
                if extra < 0:
                    print("Extra minutes must be positive.")
                    continue
                extended_by = extra
                task['duration'] += extra
                print(f"Extended task to {task['duration']} minutes.")
            except ValueError:
                print("Please enter a valid number.")
                continue

        try:
            print(f"Logging action for user_id={user_id}, task_id={task.get('task_id')}, task='{task['description']}', action='{action}'")
            log_action_db(user_id=user_id, task=task, action=action, extended_by=extended_by)
            print("Log saved successfully.")
        except Exception as e:
            print(f"Logging failed: {e}")

        if action in ['c', 's']:
            i += 1
        elif action == 'd':
            print(f"Deferred task: {task['description']}")
            schedule.append(schedule.pop(i))

    print("\nAll tasks handled! Your session is complete.")

if __name__ == "__main__":
    print("Welcome to the Interactive Study Scheduler!")
    username = input("Username: ")
    password = input("Password: ")

    try:
        signup(username, password)
        token = login(username, password)
        user_info = get_user_info(token)
        user_id = user_info["id"]
        print(f"Logged in as {user_info['username']} (ID: {user_id})")

        raw_tasks = input("Enter your tasks (e.g., 'do 2 homework assignments, watch a video'): ")
        available_time = input("Enter your available time in minutes (default 120): ").strip()
        available_time = int(available_time) if available_time.isdigit() else 120

        schedule = get_schedule_from_backend(token, raw_tasks, available_time)
        run_interactive_scheduler(schedule, user_id)

    except Exception as e:
        print("Error:", e)
