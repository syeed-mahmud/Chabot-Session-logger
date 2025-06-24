from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
import pymysql
from database import get_db_connection, init_database
from models import ChatMessage, ChatResponse, SessionResponse

# Initialize database on startup using lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_database()
    yield
    # Shutdown (if needed)

# Initialize FastAPI app with lifespan
app = FastAPI(title="Chatbot API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware to allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Chatbot API is running!"}

@app.post("/new-session", response_model=SessionResponse)
async def create_new_session():
    """Generate a new random session ID and store it in database"""
    try:
        # Generate random session ID
        session_id = str(uuid.uuid4())
        
        # Store in database
        connection = get_db_connection()
        if not connection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO chat_sessions (session_id) VALUES (%s)",
            (session_id,)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return SessionResponse(
            session_id=session_id,
            message="New session created successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(chat_message: ChatMessage):
    """Store chat question and return static response"""
    try:
        # Static response
        static_answer = "Working"
        
        # Store in database
        connection = get_db_connection()
        if not connection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor()
        
        # Check if session exists
        cursor.execute(
            "SELECT session_id FROM chat_sessions WHERE session_id = %s",
            (chat_message.session_id,)
        )
        session_exists = cursor.fetchone()
        
        if not session_exists:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Store chat message and response
        cursor.execute(
            "INSERT INTO chat_messages (session_id, question, answer) VALUES (%s, %s, %s)",
            (chat_message.session_id, chat_message.question, static_answer)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return ChatResponse(
            session_id=chat_message.session_id,
            question=chat_message.question,
            answer=static_answer
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/session/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        connection = get_db_connection()
        if not connection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "SELECT question, answer, created_at FROM chat_messages WHERE session_id = %s ORDER BY created_at",
            (session_id,)
        )
        history = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return {"session_id": session_id, "history": history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chat history: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 