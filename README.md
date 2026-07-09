/ai-crm-hcp
│
├── /backend            # All FastAPI, LangGraph, and models code
│   ├── /app
│   │   ├── main.py
│   │   └── models.py
│   ├── .env            # Do not upload this to GitHub (use .gitignore)
│   ├── requirements.txt
│   └── ...
├── /frontend           # React UI code
│   ├── /src
│   └── package.json
└── README.md

# AI-First CRM HCP Module

An AI-powered CRM system designed for healthcare field representatives to log and manage interactions with Healthcare Professionals (HCPs) efficiently.

## Core Features
- **Conversational Logging:** Log interactions using natural language.
- **Incremental Updates:** AI agent incrementally updates form fields based on conversation flow.
- **Dynamic State Management:** Real-time synchronization between chat and the form UI.
- **Database Integration:** Persistent storage using SQLAlchemy (PostgreSQL/MySQL ready).

## Tech Stack
- **Backend:** FastAPI, Python, LangGraph, LangChain, Groq API.
- **Frontend:** React, Axios.
- **Database:** SQLite (Default), compatible with PostgreSQL/MySQL.

## How to Run

### Backend
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Start the server: `python -m uvicorn app.main:app --reload`

### Frontend
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the application: `npm run dev`

## LangGraph Tools
1. **Log Interaction:** Captures and extracts entity data from text.
2. **Edit Interaction:** Allows manual overrides of logged fields.
3. **Check Analytics:** Computes interaction engagement metrics.
4. **Inspect History:** Retrieves previous interaction logs.
5. **Schedule Reminder:** Triggers follow-up notifications.
