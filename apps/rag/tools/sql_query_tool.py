"""
SQL Query Tool for the agent with safety checks.
"""

from django.db import connection


def sql_query_tool(query):
    """
    Execute a read-only SQL query safely.
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        dict: Query results or error
    """
    # Safety checks
    query_lower = query.lower().strip()
    
    # Only allow SELECT queries
    if not query_lower.startswith('select'):
        return {
            'success': False,
            'error': 'Only SELECT queries are allowed',
            'results': []
        }
    
    # Block dangerous keywords
    dangerous_keywords = ['drop', 'delete', 'update', 'insert', 'alter', 'create', 'truncate']
    for keyword in dangerous_keywords:
        if keyword in query_lower:
            return {
                'success': False,
                'error': f'Dangerous keyword detected: {keyword}',
                'results': []
            }
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
        
        return {
            'success': True,
            'results': results,
            'count': len(results)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'results': []
        }


# Tool metadata
TOOL_METADATA = {
    'name': 'sql_query',
    'description': 'Execute read-only SQL queries on the database (SELECT only)',
    'parameters': {
        'query': {
            'type': 'string',
            'description': 'The SQL SELECT query to execute',
            'required': True
        }
    }
}
