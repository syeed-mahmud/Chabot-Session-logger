# Simple Chatbot with FastAPI and Streamlit

A simple chatbot application with FastAPI backend, MySQL database, and Streamlit frontend.

## Features

- 🆕 Generate random session IDs for new chat sessions
- 💾 Store chat questions and answers in MySQL database
- 🤖 Static "Working" response from chatbot
- 🖥️ Simple Streamlit web interface
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

4. **Run Streamlit Frontend**
   ```bash
   streamlit run streamlit_app.py
   ```
   - Web interface will be available at http://localhost:8501

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

## Usage

1. Start a new session using the sidebar button
2. Type your questions in the chat interface
3. Receive "Working" response from the bot
4. View chat history within the session
5. Load previous chat history using the sidebar button

## Technologies Used

- **Backend**: FastAPI, Python
- **Database**: MySQL (via XAMPP)
- **Frontend**: Streamlit
- **Database Driver**: PyMySQL

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

### **Frontend Connection** (Streamlit)
```python
# API calls from streamlit_app.py
API_BASE_URL = "http://localhost:8001"

# Create session
response = requests.post(f"{API_BASE_URL}/new-session")

# Send message
payload = {"session_id": session_id, "question": question}
response = requests.post(f"{API_BASE_URL}/chat", json=payload)

# Get history
response = requests.get(f"{API_BASE_URL}/session/{session_id}/history")
```

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
3. **API**: FastAPI with CORS enabled
4. **Frontend**: Streamlit with requests library
5. **Auto Setup**: Database/tables created automatically
6. **Static Response**: Always returns "Working" 