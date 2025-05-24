from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from datetime import datetime
from os.path import exists
from typing import List, Dict, Any, Optional

app = FastAPI()

# Enable CORS for your React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    conversation_id: str


# Store active conversations
conversations = {}

# LM Studio API settings
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_ID = "meta-llama-3.1-8b-instruct"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer lm-studio"  # Dummy API key
}


# Generate a unique conversation ID
def generate_conversation_id():
    return datetime.now().strftime("%Y%m%d%H%M%S") + str(hash(datetime.now()))[:4]


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    conversation_id = request.conversation_id

    # Create new conversation if none exists
    if not conversation_id or conversation_id not in conversations:
        conversation_id = generate_conversation_id()
        conversations[conversation_id] = [
            {"role": "system", "content": "You are a helpful programming tutor."}
        ]

    # Get current conversation
    messages = conversations[conversation_id]

    # Add user message
    messages.append({"role": "user", "content": request.message})

    # Create payload for LM Studio
    payload = {
        "model": MODEL_ID,
        "messages": messages,
        "temperature": 0.7
    }

    try:
        # Send request to LM Studio API
        response = requests.post(LM_STUDIO_URL, headers=HEADERS, json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()
            answer = data['choices'][0]['message']['content'].strip()

            # Add assistant message to conversation history
            messages.append({"role": "assistant", "content": answer})

            # Save updated conversation
            conversations[conversation_id] = messages

            return {"answer": answer, "conversation_id": conversation_id}
        else:
            raise HTTPException(status_code=500, detail=f"LM Studio API error: {response.text}")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e)}")


@app.get("/api/conversations/{conversation_id}", response_model=List[ChatMessage])
async def get_conversation(conversation_id: str):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversations[conversation_id]


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    if conversation_id in conversations:
        del conversations[conversation_id]
    return {"status": "success"}


# Save conversations periodically or when server shuts down
@app.on_event("shutdown")
def save_conversations():
    history_file = "chat-history.json"

    # Load existing history if it exists
    if exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            full_history = json.load(f)
            if not isinstance(full_history, list):
                full_history = [full_history]
    else:
        full_history = []

    # Add all active conversations
    for conv_id, messages in conversations.items():
        full_history.append({
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conv_id,
            "conversation": messages
        })

    # Save to file
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(full_history, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)