from fastapi import FastAPI # to build web server
from pydantic import BaseModel # define shape of data expected from user and auomatically validates
from typing import Optional # in case a value can be none
from pydantic import BaseModel
from openai import OpenAI  # gpt-4
import os # to get OpenAI API key

app = FastAPI() # creates app to handle web routes and server logic

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # secret key

class TaskInput(BaseModel):
    available_time_minutes: int
    raw_tasks_text: str
    
def call_gpt_parse_tasks(raw_text: str) -> str:
    system_message = {
        "role": "system",
        "content": (
            "You are a task parser that breaks down academic tasks into JSON format. "
            "Each task must include: description, subject, task_type, and estimated_duration_minutes. "
            "If no duration is given, estimate based on task type. Estimate the time required for each "
            "task based on typical effort and complexity. If the number of items is mentioned "
            "(e.g., '10 problems'), consider how long such tasks usually take, and provide a realistic "
            "total duration — even if the time isn’t explicitly stated."
        )
    }
    user_message = {
        "role": "user",
        "content": f"Tasks: {raw_text}"
    }

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[system_message, user_message],
        temperature=0.3
    )

    return response.choices[0].message.content


@app.post("/parse-tasks")
async def parse_tasks(task_input: TaskInput): # function run by FastAPI and receives user input already validated
    parsed_tasks_json = call_gpt_parse_tasks(task_input.raw_tasks_text) # call GPT function to process task list
    return { # send back json response with time and structured tasks
        "available_time_minutes": task_input.available_time_minutes,
        "parsed_tasks": parsed_tasks_json
    }

'''
1. Gets OpenAI key
2. Declares shape of user input and validates with FastAPI
3. Defines function to talk to GPT-4
4. Creates API route that receives user's time + todo list, passes to GPT-4, and returns user's time + GPT parsed list
'''