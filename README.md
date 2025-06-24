# Simple Chatbot API with FastAPI

A simple chatbot REST API built with FastAPI backend and MySQL database. Test with Postman or any HTTP client.

## Features

- 🆕 Generate random session IDs for new chat sessions
- 💾 Store chat questions and answers in MySQL database
- 🤖 Static "Working" response from chatbot
- 🔗 REST API endpoints for easy integration
- 📊 Chat history functionality

## Prerequisites

- Python 3.7+
- XAMPP with MySQL running
- phpMyAdmin accessible at localhost:8080

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start XAMPP MySQL**
   - Make sure XAMPP is running
   - MySQL service should be active
   - phpMyAdmin should be accessible at http://localhost:8080

3. **Run FastAPI Backend**
   ```bash
   python main.py
   ```
   - API will be available at http://localhost:8001
   - API documentation at http://localhost:8001/docs

4. **Test with Postman or HTTP Client**
   - Import the API endpoints below into Postman
   - Use the interactive API docs at http://localhost:8001/docs

## API Endpoints

### 1. Create New Session
- **POST** `/new-session`
- Generates a random session ID and stores it in database
- Returns: `{"session_id": "uuid", "message": "New session created successfully"}`

### 2. Chat with Bot
- **POST** `/chat`
- Body: `{"session_id": "uuid", "question": "your question"}`
- Stores question and returns static "Working" response
- Returns: `{"session_id": "uuid", "question": "your question", "answer": "Working"}`

### 3. Get Chat History
- **GET** `/session/{session_id}/history`
- Returns all chat messages for a session

## Database Schema

The application creates two tables:

1. **chat_sessions**
   - id (Primary Key)
   - session_id (Unique)
   - created_at (Timestamp)

2. **chat_messages**
   - id (Primary Key)
   - session_id (Foreign Key)
   - question (Text)
   - answer (Text)
   - created_at (Timestamp)

## Postman Usage

1. **Create New Session**:
   - Method: POST
   - URL: `http://localhost:8001/new-session`
   - Copy the `session_id` from response

2. **Send Chat Message**:
   - Method: POST
   - URL: `http://localhost:8001/chat`
   - Body (JSON): `{"session_id": "your-session-id", "question": "Hello"}`

3. **Get Chat History**:
   - Method: GET
   - URL: `http://localhost:8001/session/{session_id}/history`

## Technologies Used

- **Backend**: FastAPI, Python
- **Database**: MySQL (via XAMPP)
- **Database Driver**: PyMySQL
- **API Testing**: Postman, FastAPI Swagger UI

---

# 🤖 Technical Documentation

## API Connections

### **FastAPI Backend** (`http://localhost:8001`)

#### **1. Create New Session**
```http
POST /new-session
```
**Response**:
```json
{
    "session_id": "uuid-generated",
    "message": "New session created successfully"
}
```

#### **2. Send Chat Message**
```http
POST /chat
Content-Type: application/json

{
    "session_id": "uuid-here",
    "question": "Your question"
}
```
**Response**:
```json
{
    "session_id": "uuid-here",
    "question": "Your question",
    "answer": "Working"
}
```

#### **3. Get Chat History**
```http
GET /session/{session_id}/history
```

### **Postman Collection Examples**

#### **Environment Variables**:
- `base_url`: `http://localhost:8001`
- `session_id`: (save from new-session response)

#### **Test Sequence**:
1. **POST** `{{base_url}}/new-session` → Save `session_id`
2. **POST** `{{base_url}}/chat` with body: `{"session_id": "{{session_id}}", "question": "Hello"}`
3. **GET** `{{base_url}}/session/{{session_id}}/history`

---

## Database Handling

### **Connection Setup** (`database.py`)
```python
import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '', 
    'database': 'chatbot_db',
    'charset': 'utf8mb4'
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)
```

### **Database Schema**
```sql
-- Database: chatbot_db

-- Sessions table
CREATE TABLE chat_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
);
```

### **Database Operations** (`main.py`)

#### **Create Session**:
```python
session_id = str(uuid.uuid4())
cursor.execute("INSERT INTO chat_sessions (session_id) VALUES (%s)", (session_id,))
```

#### **Store Message**:
```python
cursor.execute(
    "INSERT INTO chat_messages (session_id, question, answer) VALUES (%s, %s, %s)",
    (session_id, question, "Working")
)
```

#### **Get History**:
```python
cursor.execute(
    "SELECT question, answer, created_at FROM chat_messages WHERE session_id = %s ORDER BY created_at",
    (session_id,)
)
```

### **Auto Database Setup**
```python
# Runs automatically on FastAPI startup
def init_database():
    # Creates database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS chatbot_db")
    # Creates tables if not exist
    cursor.execute("CREATE TABLE IF NOT EXISTS chat_sessions...")
```

---

## Key Technical Points

1. **Session Management**: UUID-based unique sessions
2. **Database**: MySQL with PyMySQL driver
3. **API**: FastAPI with CORS enabled for cross-origin requests
4. **Testing**: Postman-ready REST API endpoints
5. **Auto Setup**: Database/tables created automatically
6. **Static Response**: Always returns "Working"
7. **Documentation**: Interactive API docs at `/docs` endpoint 