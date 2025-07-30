from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import joblib
from openai import OpenAI
from auth import router as auth_router, get_current_user
from personalization import (
    get_user_logs,
    preprocess_user_logs,
    compute_task_priority_scores,
    normalize_task_type,
)
from scheduler import schedule_tasks_cognitive
from database import Base, engine, SessionLocal
from models import TaskLog
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
import json
from dotenv import load_dotenv
import subprocess

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_PATH = "multioutput_model.pkl"
FEATURES_PATH = "model_feature_names.pkl"
model = joblib.load(MODEL_PATH)
MODEL_FEATURES = joblib.load(FEATURES_PATH)

class TaskInput(BaseModel):
    available_time_minutes: int
    raw_tasks_text: str
    must_do_tasks: list[str] = []

class TaskActionInput(BaseModel):
    user_id: int
    task: dict
    action: str
    extended_by: int | None = None

def call_gpt_parse_tasks(raw_text: str, must_do_tasks: list[str]):
    system_message = {
        "role": "system",
        "content": (
            "You are a task parser that breaks down academic tasks into JSON format. "
            "Each task must include: description, subject, task_type, and estimated_duration_minutes. "
            "The task_type must be one of the following predefined categories: "
            '["homework", "writing", "problem_solving", "project", "reading", "video_watching", '
            '"break", "coding", "essay", "assignment"]. '
            "Estimate durations based on the task type and count, even if not explicitly stated."
        ),
    }
    user_message = {"role": "user", "content": f"Tasks: {raw_text}"}

    response = client.chat.completions.create(
        model="gpt-4", messages=[system_message, user_message], temperature=0.3
    )

    parsed_tasks = json.loads(response.choices[0].message.content)
    for task in parsed_tasks:
        task["task_id"] = str(uuid.uuid4())
        task["task_type"] = normalize_task_type(task.get("task_type", ""))
        task["must_do"] = any(md.lower() in task["description"].lower() for md in must_do_tasks)
    return parsed_tasks

@app.post("/personalized-schedule")
async def personalized_schedule(task_input: TaskInput, current_user=Depends(get_current_user)):
    try:
        parsed_tasks = call_gpt_parse_tasks(task_input.raw_tasks_text, task_input.must_do_tasks)
        df_logs = get_user_logs(current_user.id)

        if df_logs.empty:
            schedule = schedule_tasks_cognitive(parsed_tasks, task_input.available_time_minutes)
        else:
            df_logs["task_type"] = df_logs["task_type"].apply(normalize_task_type)
            X_user, recency_weights = preprocess_user_logs(df_logs)
            priority_scores = compute_task_priority_scores(X_user, recency_weights)

            df_logs = df_logs.reset_index(drop=True)
            df_logs["priority_score"] = priority_scores.values
            df_logs["recency_weight"] = recency_weights.values

            avg_durations = df_logs.groupby("task_type")["actual_duration"].mean().to_dict()
            avg_scores_by_type = df_logs.groupby("task_type")["priority_score"].mean().to_dict()

            for task in parsed_tasks:
                task["estimated_duration_minutes"] = avg_durations.get(
                    task["task_type"], task["estimated_duration_minutes"]
                )

                matching_logs = df_logs[
                    df_logs["task_description"].str.contains(task["description"], case=False, na=False)
                ]

                if not matching_logs.empty:
                    weighted_score = (
                        (matching_logs["priority_score"] * matching_logs["recency_weight"]).sum()
                        / matching_logs["recency_weight"].sum()
                    )
                    task["priority_score"] = weighted_score
                else:
                    task["priority_score"] = avg_scores_by_type.get(task["task_type"], 0)

                if task.get("must_do", False):
                    task["priority_score"] += 0.5

            parsed_tasks.sort(key=lambda t: (t.get("must_do", False), t["priority_score"]), reverse=True)
            schedule = schedule_tasks_cognitive(parsed_tasks, task_input.available_time_minutes)

        return {
            "available_time_minutes": task_input.available_time_minutes,
            "parsed_tasks": parsed_tasks,
            "schedule": schedule,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling error: {e}")

def run_personalization_pipeline():
    print("📈 Running export_logs.py and train_model.py...")
    subprocess.run(["python", "export_logs.py"])
    subprocess.run(["python", "train_model.py"])

def is_last_task(user_id, task_id):
    return True

@app.post("/log-task")
def log_task(input: TaskActionInput, background_tasks: BackgroundTasks, current_user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        task = input.task
        log = TaskLog(
            user_id=input.user_id,
            task_id=task.get("task_id"),
            task_description=task["description"],
            task_type=task.get("task_type", "unknown"),
            scheduled_duration=task["duration"],
            actual_duration=task["duration"] + (input.extended_by or 0) if input.action == "e" else task["duration"],
            action=input.action,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()

        if input.action == "c" and is_last_task(input.user_id, task["task_id"]):
            background_tasks.add_task(run_personalization_pipeline)

        return {"msg": "Task logged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log: {e}")
    finally:
        db.close()

Base.metadata.create_all(bind=engine)


