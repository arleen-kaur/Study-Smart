from dotenv import load_dotenv
import os
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
from database import Base, engine

import json

import scheduler
from scheduler import schedule_tasks_cognitive
from auth import router as auth_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

    return response.choices[0].message.content

@app.post("/parse-tasks")
async def parse_tasks(task_input: TaskInput):
    parsed_tasks_json = call_gpt_parse_tasks(task_input.raw_tasks_text)
    try:
        parsed_tasks = json.loads(parsed_tasks_json)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse tasks JSON from GPT.",
            "raw_response": parsed_tasks_json
        }

    schedule = schedule_tasks_cognitive(parsed_tasks, task_input.available_time_minutes)
    return {
        "available_time_minutes": task_input.available_time_minutes,
        "parsed_tasks": parsed_tasks,
        "schedule": schedule
    }
