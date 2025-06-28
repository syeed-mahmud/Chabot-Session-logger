"""
Odoo XML-RPC client for database connectivity and query execution.
"""

import xmlrpc.client
import os
import sys
import io
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)


class OdooClient:
    """
    A client for connecting to and interacting with Odoo via XML-RPC.
    
    This class handles authentication and provides methods for querying
    Odoo data using the XML-RPC protocol.
    """
    
    def __init__(self, url: Optional[str] = None, db: Optional[str] = None, 
                 username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the Odoo client with credentials.
        
        Args:
            url: Odoo instance URL (defaults to ODOO_URL env var)
            db: Database name (defaults to ODOO_DB env var)
            username: Username (defaults to ODOO_USERNAME env var)
            password: Password (defaults to ODOO_PASSWORD env var)
            
        Raises:
            Exception: If any required credentials are missing
        """
        # Use environment variables if not provided
        self.url = url or os.getenv('ODOO_URL')
        self.db = db or os.getenv('ODOO_DB')
        self.username = username or os.getenv('ODOO_USERNAME')
        self.password = password or os.getenv('ODOO_PASSWORD')
        
        if not all([self.url, self.db, self.username, self.password]):
            raise Exception("Missing Odoo credentials. Please check your .env file.")
        
        self.uid = None
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        self.authenticate()

    def authenticate(self) -> None:
        """
        Authenticate with the Odoo server.
        
        Raises:
            Exception: If authentication fails
        """
        self.uid = self.common.authenticate(self.db, self.username, self.password, {})
        if not self.uid:
            raise Exception("Authentication failed!")

    def search_read(self, model: str, domain: Optional[List] = None, 
                   fields: Optional[List[str]] = None, limit: int = 0) -> List[Dict[str, Any]]:
        """
        Execute a search_read operation on an Odoo model.
        
        Args:
            model: The Odoo model name (e.g., 'res.partner')
            domain: Search domain filters
            fields: List of fields to retrieve
            limit: Maximum number of records to return (0 = no limit)
            
        Returns:
            List of dictionaries containing the retrieved records
        """
        domain = domain or []
        fields = fields or []
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'search_read',
            [domain],
            {'fields': fields, 'limit': limit}
        )

    def execute_code(self, code_to_execute: str) -> Dict[str, Any]:
        """
        Execute dynamically generated Python code with access to the Odoo client.
        
        Args:
            code_to_execute: Python code string to execute
            
        Returns:
            Dictionary containing execution results:
            - text_output: Captured print statements
            - data: Any data assigned to 'result_data' variable
            - error: Error message if execution failed
        """
        # Create a local namespace with the odoo client available
        local_namespace = {
            'odoo': self,
            'datetime': datetime,
            'timedelta': timedelta,
            'pd': pd
        }
        
        # Capture stdout to get any print statements
        stdout_capture = io.StringIO()
        original_stdout = sys.stdout
        
        sys.stdout = stdout_capture
        
        result = {
            'text_output': '',
            'data': None,
            'error': None
        }
        
        try:
            # Execute the code in the local namespace
            exec(code_to_execute, globals(), local_namespace)
            
            # Capture any return value assigned to 'result_data'
            if 'result_data' in local_namespace:
                result['data'] = local_namespace['result_data']
            
            # Get any printed output
            result['text_output'] = stdout_capture.getvalue()
            
        except Exception as e:
            result['error'] = str(e)
            
        finally:
            # Restore stdout
            sys.stdout = original_stdout
            
        return result


def get_odoo_client() -> OdooClient:
    """
    Factory function to create OdooClient with credentials from environment.
    
    Returns:
        Configured OdooClient instance
    """
    return OdooClient() 