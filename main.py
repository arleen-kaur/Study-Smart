from dotenv import load_dotenv
import os
import uuid
import json
import joblib
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
from database import Base, engine
from scheduler import schedule_tasks_cognitive
from auth import router as auth_router, get_current_user
from personalization import get_user_logs, preprocess_user_logs

load_dotenv()

app = FastAPI()
app.include_router(auth_router, prefix="/auth")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load ML model once on startup
model = joblib.load("rf_model.joblib")

class TaskInput(BaseModel):
    available_time_minutes: int
    raw_tasks_text: str

def call_gpt_parse_tasks(raw_text: str) -> str:
    system_message = {
        "role": "system",
        "content": (
            "You are a task parser that breaks down academic tasks into JSON format. "
            "Each task must include: description, subject, task_type, and estimated_duration_minutes. "
            "Estimate times based on task type and count even if not explicitly stated."
        )
    }
    user_message = {"role": "user", "content": f"Tasks: {raw_text}"}

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[system_message, user_message],
        temperature=0.3
    )

    parsed_tasks = json.loads(response.choices[0].message.content)

    for task in parsed_tasks:
        task["task_id"] = str(uuid.uuid4())

    return parsed_tasks  # return as object now

@app.post("/parse-tasks")
async def parse_tasks(task_input: TaskInput):
    parsed_tasks = call_gpt_parse_tasks(task_input.raw_tasks_text)
    schedule = schedule_tasks_cognitive(parsed_tasks, task_input.available_time_minutes)
    return {
        "available_time_minutes": task_input.available_time_minutes,
        "parsed_tasks": parsed_tasks,
        "schedule": schedule
    }

@app.post("/personalized-schedule")
async def personalized_schedule(
    task_input: TaskInput,
    current_user = Depends(get_current_user)
):
    parsed_tasks = call_gpt_parse_tasks(task_input.raw_tasks_text)

    # Get user's historical logs as DataFrame
    df_logs = get_user_logs(current_user.id)

    if df_logs.empty:
        # Cold start fallback
        schedule = schedule_tasks_cognitive(parsed_tasks, task_input.available_time_minutes)
    else:
        X_user = preprocess_user_logs(df_logs)

        # Predict completion probabilities
        preds = model.predict_proba(X_user)[:, 1]

        # Map predictions to tasks by matching 'task_type' or description heuristics
        # For demo, sort parsed_tasks by max predicted completion of matching task_type from logs
        # (You may want a more precise matching in practice)

        # Aggregate preds by task_type in logs
        pred_df = df_logs.copy()
        pred_df['pred'] = preds
        pred_by_type = pred_df.groupby('task_type')['pred'].mean().to_dict()

        # Sort tasks: tasks with higher predicted completion rates come first
        parsed_tasks.sort(key=lambda t: pred_by_type.get(t['task_type'], 0), reverse=True)

        schedule = schedule_tasks_cognitive(parsed_tasks, task_input.available_time_minutes)

    return {
        "available_time_minutes": task_input.available_time_minutes,
        "parsed_tasks": parsed_tasks,
        "schedule": schedule
    }

Base.metadata.create_all(bind=engine)
