"""
Natural language query processing for Odoo data.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from .client import OdooClient

# Load environment variables
load_dotenv(override=True)


def get_system_message() -> str:
    """
    Get the system message for the LLM to generate Odoo code.
    
    Returns:
        System message string with instructions for code generation
    """
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


def get_ai_response(question: str) -> str:
    """
    Get response from OpenRouter AI model.
    
    Args:
        question: Natural language question about Odoo data
        
    Returns:
        Generated Python code string
    """
    try:
        # Initialize OpenRouter client
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://localhost:8001",
                "X-Title": "Odoo Chatbot",
            },
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
        return f"Error generating code: {str(e)}"


def clean_generated_code(code: str) -> str:
    """
    Clean markdown formatting from generated code.
    
    Args:
        code: Raw code string that may contain markdown
        
    Returns:
        Cleaned Python code string
    """
    # Remove Markdown code blocks if present
    if code.startswith('```python'):
        code = code[len('```python'):].strip()
    if code.startswith('```'):
        code = code[3:].strip()
    if code.endswith('```'):
        code = code[:-3].strip()
    
    return code


def execute_odoo_query(question: str) -> Dict[str, Any]:
    """
    Main function to generate and execute Odoo query code based on natural language question.
    
    Args:
        question: Natural language question about Odoo data
        
    Returns:
        Dictionary containing:
        - success: Boolean indicating if operation was successful
        - question: Original question
        - code: Generated Python code
        - text_response: Human-readable output from code execution
        - data: Structured data returned from the query
        - error: Error message if any
    """
    try:
        if not question or not question.strip():
            return {
                'success': False,
                'error': 'Question cannot be empty',
                'question': question,
                'code': None,
                'text_response': None,
                'data': None
            }

        # Generate code using LLM
        generated_code = get_ai_response(question)
        cleaned_code = clean_generated_code(generated_code)

        # Create Odoo client
        try:
            odoo = OdooClient()
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to connect to Odoo: {str(e)}',
                'question': question,
                'code': cleaned_code,
                'text_response': None,
                'data': None
            }

        # Execute the generated code
        try:
            result = odoo.execute_code(cleaned_code)
        except Exception as e:
            return {
                'success': False,
                'error': f'Error executing code: {str(e)}',
                'question': question,
                'code': cleaned_code,
                'text_response': None,
                'data': None
            }

        # Prepare the response
        response = {
            'success': True,
            'question': question,
            'code': cleaned_code,
            'text_response': result['text_output'],
            'data': result['data'],
            'error': result.get('error')
        }
        
        return response
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'question': question,
            'code': None,
            'text_response': None,
            'data': None
        } 