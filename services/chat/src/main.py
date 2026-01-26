"""
Chat API Service for Advanced Todo Application
Handles user requests via chat interface and communicates with other services
"""
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import asyncio

# Initialize FastAPI app
app = FastAPI(title="Chat API Service", version="1.0.0")

# Models
class ChatRequest(BaseModel):
    user_id: str
    message: str
    timestamp: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    task_id: Optional[int] = None
    success: bool = True

class TaskRequest(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    tags: Optional[list] = []
    due_date: Optional[str] = None
    is_recurring: Optional[bool] = False

# Configuration
TASK_SERVICE_URL = os.getenv("TASK_SERVICE_URL", "http://task-service:8000")

@app.get("/")
async def root():
    return {"message": "Chat API Service - Advanced Todo Application"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    """
    Main chat endpoint that processes user messages and performs actions
    """
    user_message = chat_request.message.lower()
    user_id = chat_request.user_id

    # Simple rule-based processing - in a real app, this would use NLP/ML
    if "create task" in user_message or "add task" in user_message:
        # Extract task details from message
        title = extract_task_title(user_message)

        # Create task via Task Service
        task_data = {
            "user_id": user_id,
            "title": title,
            "description": f"Created from chat: {chat_request.message}"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{TASK_SERVICE_URL}/api/{user_id}/tasks", json=task_data)

                if response.status_code == 201:
                    task_result = response.json()
                    return ChatResponse(
                        response=f"Task '{title}' created successfully!",
                        task_id=task_result['id'],
                        success=True
                    )
                else:
                    return ChatResponse(
                        response="Failed to create task",
                        success=False
                    )
        except Exception as e:
            return ChatResponse(
                response=f"Error creating task: {str(e)}",
                success=False
            )

    elif "list tasks" in user_message or "show tasks" in user_message:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{TASK_SERVICE_URL}/api/{user_id}/tasks")

                if response.status_code == 200:
                    tasks = response.json()
                    task_list = [f"- {task['title']} ({task['status']})" for task in tasks[:5]]  # Show first 5 tasks
                    task_str = "\n".join(task_list) if task_list else "No tasks found"

                    return ChatResponse(
                        response=f"Your tasks:\n{task_str}",
                        success=True
                    )
                else:
                    return ChatResponse(
                        response="Failed to retrieve tasks",
                        success=False
                    )
        except Exception as e:
            return ChatResponse(
                response=f"Error retrieving tasks: {str(e)}",
                success=False
            )

    else:
        # Default response for unrecognized commands
        return ChatResponse(
            response="I can help you create tasks, list tasks, or mark tasks as complete. Try saying 'create a task to buy groceries'",
            success=True
        )

def extract_task_title(message: str) -> str:
    """
    Simple function to extract task title from user message
    In a real implementation, this would use NLP
    """
    # Remove common phrases
    message = message.replace("create task", "").replace("add task", "").strip()

    # Extract title (everything after common phrases)
    if "to " in message:
        title = message.split("to ", 1)[1]
    elif "that " in message:
        title = message.split("that ", 1)[1]
    else:
        title = message

    # Clean up the title
    title = title.strip().capitalize()

    # If title is still too generic, use the original message
    if len(title) < 3:
        title = message.strip().capitalize()

    return title or "Untitled Task"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)