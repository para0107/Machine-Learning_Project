# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal
import uvicorn

app = FastAPI()

# 🔒 Change this to your deployed Vercel front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-app.vercel.app"],  # UPDATE THIS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Models ------------------

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage]

class ChatResponse(BaseModel):
    answer: str
    history: List[ChatMessage]

# ----------------- Dummy Logic (for now) ------------------

def qa_chain(query_dict):
    # TODO: Replace this with your real chain logic
    return {"result": f"Echo: {query_dict['query']}"}

def save_history(messages_dict):
    # TODO: Replace with DB/cloud-safe storage logic
    print("💾 Saving history... (stubbed)")
    return

# ---------------- Endpoint ------------------

@app.post("/rag_chat", response_model=ChatResponse)
async def rag_chat_endpoint(req: ChatRequest):
    messages = req.history if req.history else []

    if not any(msg.role == "user" and msg.content == req.message for msg in messages):
        messages.append(ChatMessage(role="user", content=req.message))

    try:
        result = qa_chain({"query": req.message})
        answer = result["result"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    messages.append(ChatMessage(role="assistant", content=answer))

    messages_dict = [msg.dict() for msg in messages]
    save_history(messages_dict)

    return ChatResponse(answer=answer, history=messages)
