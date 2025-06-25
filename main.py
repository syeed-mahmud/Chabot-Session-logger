from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
import pymysql
import os
from dotenv import load_dotenv
from openai import OpenAI
from database import get_db_connection, init_database
from models import ChatMessage, ChatResponse, SessionResponse

# Load environment variables
load_dotenv()

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

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

def get_system_message():
    return """
    You are an expert at generating Odoo XML-RPC query code based on natural language questions.
    Given a question, create Python code that queries an Odoo database using XML-RPC to answer it.
    
    CONTEXT:
    You have access to an OdooClient class with XML-RPC connectivity:
    - odoo.search_read(model, domain, fields, limit) - Primary method for querying
    - Pre-imported libraries: datetime, timedelta, pandas (as pd)
    
    EXECUTION PATTERN:
    Your code executes in a namespace with:
    - 'odoo' object (authenticated OdooClient instance)
    - datetime, timedelta, pd libraries available
    - Code runs via exec() in execute_code method
    
    REQUIREMENTS:
    1. Store main result as 'result_data' variable
    2. Print user-friendly summary using print() statements
    3. Use parameter names 'fields' and 'limit' in search_read calls
    4. Use pandas for data manipulation when needed
    5. Provide plain text summaries, not pandas/complex formats
    6. Answer only the specific question asked
    
    ODOO MODEL PATTERNS:
    - Partners: 'res.partner'
    - Sales Orders: 'sale.order'
    - Invoices: 'account.move'
    - Products: 'product.product'
    - Purchase Orders: 'purchase.order'
    
    DOMAIN SYNTAX:
    - [('field', 'operator', 'value')]
    - Operators: '=', '!=', '>', '<', '>=', '<=', 'like', 'ilike', 'in', 'not in'
    - Combine with '&' (AND), '|' (OR)
    
    Return only executable Python code without explanations or markdown formatting.
    """

async def get_ai_response(question: str) -> str:
    """Get response from OpenRouter AI model"""
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://localhost:8001",  # Optional
                "X-Title": "Chatbot API",  # Optional
            },
            extra_body={},
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {
                    "role": "system",
                    "content": get_system_message()
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Fallback response if API fails
        return f"I'm sorry, I encountered an error: {str(e)}"

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
    """Store chat question and return AI response"""
    try:
        # Get AI response
        ai_answer = await get_ai_response(chat_message.question)
        
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
            (chat_message.session_id, chat_message.question, ai_answer)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return ChatResponse(
            session_id=chat_message.session_id,
            question=chat_message.question,
            answer=ai_answer
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