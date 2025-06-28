"""
Core functionality for Odoo integration.
"""

from .client import OdooClient
from .query_processor import execute_odoo_query

__all__ = [
    "OdooClient", 
    "execute_odoo_query"
] 