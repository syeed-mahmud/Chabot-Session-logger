# Odoo Chatbot

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A professional AI-powered natural language interface for Odoo ERP systems. Generate and execute Python code for Odoo XML-RPC queries based on natural language questions.

## ✨ Features

- **Natural Language Processing**: Ask questions in plain English about your Odoo data
- **AI-Powered Code Generation**: Uses OpenRouter API to generate Python XML-RPC code
- **Direct Execution**: Executes generated code against your Odoo instance
- **Multiple Interfaces**: FastAPI REST API and Streamlit web interface
- **Professional Package Structure**: Well-organized modular structure
- **Type Hints**: Full type annotations for better development experience

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/odoo-chatbot.git
cd odoo-chatbot

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```bash
ODOO_URL=https://your-odoo-instance.odoo.com/
ODOO_DB=your_database_name
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Basic Usage

#### Direct Python Usage

```python
from odoo_chatbot import execute_odoo_query

# Execute a query
result = execute_odoo_query("Show me all partners from USA")

if result['success']:
    print("Generated Code:", result['code'])
    print("Result:", result['text_response'])
    print("Data:", result['data'])
else:
    print("Error:", result['error'])
```

## 📁 Project Structure

```
odoo-chatbot/
├── odoo_chatbot/           # Main package
│   ├── __init__.py         # Package initialization
│   ├── core/               # Core functionality
│   │   ├── __init__.py
│   │   ├── client.py       # Odoo XML-RPC client
│   │   └── query_processor.py  # Query processing logic
│   ├── api/                # FastAPI web API
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI application
│   │   ├── models.py       # Pydantic models
│   │   └── database.py     # Database connection
│   └── web/                # Streamlit web interface
│       ├── __init__.py
│       └── streamlit_app.py
├── examples/               # Usage examples
│   ├── __init__.py
│   └── example_usage.py
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── LICENSE              # MIT license
├── MANIFEST.in          # Package manifest
└── README.md           # This file
```

## 🔧 API Endpoints

When running the FastAPI server:

- `GET /`: Health check
- `POST /new-session`: Create a new chat session
- `POST /chat`: Send a message and get AI response
- `GET /session/{session_id}/history`: Get chat history

## 💡 Example Questions

- "Show me all partners"
- "Get sales orders from this month"
- "Find products with price greater than 100"
- "List all invoices created this year"
- "Show me recent purchase orders"
- "Get partners from USA with email addresses"

## 🏗️ Usage

### Running Components

```bash
# Run simple usage example
python simple_usage.py

# Run advanced example
python examples/example_usage.py

# Start FastAPI server
uvicorn odoo_chatbot.api.main:app --host 0.0.0.0 --port 8001 --reload

# Start Streamlit web interface
streamlit run odoo_chatbot/web/streamlit_app.py
```

## 📦 Dependencies

### Core Dependencies
- `openai` - AI model integration
- `python-dotenv` - Environment variable management
- `pandas` - Data manipulation
- `xmlrpc` - Odoo XML-RPC communication

### Optional Dependencies
- **API**: `fastapi`, `uvicorn`, `pymysql`, `cryptography`
- **Web**: `streamlit`, `requests`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Create an issue for bug reports or feature requests
- Check the examples directory for usage patterns

## ⚠️ Security Notes

- Never commit your `.env` file with real credentials
- Use environment variables or secure secret management in production
- Validate and sanitize all user inputs
- Review generated code before execution in production environments 