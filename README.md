# Study Smart  
**AI-Powered Personalized Study Planner**

## Overview  
Study Smart is a full-stack web application that converts free-form academic to-do lists into personalized, optimized study schedules using GPT-4 and machine learning. It applies cognitive science principles like Pomodoro and interleaved learning to help users focus, retain more, and complete tasks efficiently.

## Features  
- Natural language task input  
- GPT-4 powered task parsing  
- Personalized duration estimates with machine learning  
- Pomodoro-style scheduling with smart breaks  
- Subject rotation to promote interleaved learning  
- Study session tracking and adaptive learning (in progress)

## User Flow  
1. User enters task descriptions and available study time  
2. GPT-4 extracts structured task data  
3. ML model adjusts time estimates based on past performance  
4. Scheduler builds a personalized, Pomodoro-style plan  
5. User follows the schedule in real time and logs progress  
6. Logged data feeds back into the model to improve personalization

## Tech Stack  

| Layer       | Technology            |
|------------|------------------------|
| Frontend   | React.js (Vite + Tailwind CSS) |
| Backend    | FastAPI (Python)       |
| NLP        | OpenAI GPT-4 API       |
| ML Model   | scikit-learn           |
| Scheduler  | Custom logic (Python)  |
| Database   | SQLite (MVP)           |
| Deployment | Vercel (frontend), Render (backend) |

## Live Demo  
Frontend (public): [https://study-smart-2ra9-hz9xkuxcv-arleen-kaurs-projects.vercel.app](https://study-smart-2ra9-hz9xkuxcv-arleen-kaurs-projects.vercel.app)  
Backend: Hosted privately on Render and not publicly accessible

---

