"""API utility functions for leaderboard application."""

import json
from typing import Any, Dict, List, Optional, Union


def build_response(
    status_code: int,
    body: Union[Dict[str, Any], List[Any], str],
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Build a standardized API response.
    
    Args:
        status_code: HTTP status code
        body: Response body (dict, list, or string)
        headers: Optional additional headers
        
    Returns:
        API Gateway response object
    """
    # Default headers with CORS support
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': (
            'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        ),
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    # Merge default headers with provided headers
    all_headers = {**default_headers, **(headers or {})}
    
    # Convert body to JSON string if it's a dict or list
    if isinstance(body, (dict, list)):
        body = json.dumps(body)
    
    return {
        'statusCode': status_code,
        'headers': all_headers,
        'body': body
    }


def success_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Build a successful API response.
    
    Args:
        data: Response data
        status_code: HTTP status code (default 200)
        
    Returns:
        API Gateway response object
    """
    return build_response(status_code, data)


def error_response(
    message: str, 
    status_code: int = 400,
    error_code: Optional[str] = None
) -> Dict[str, Any]:
    """Build an error API response.
    
    Args:
        message: Error message
        status_code: HTTP status code (default 400)
        error_code: Optional error code
        
    Returns:
        API Gateway response object
    """
    error_body = {
        'message': message
    }
    
    if error_code:
        error_body['error_code'] = error_code
        
    return build_response(status_code, error_body)


def parse_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse and normalize API Gateway event.
    
    Args:
        event: API Gateway event
        
    Returns:
        Parsed event with normalized properties
    """
    result = {
        'path_parameters': event.get('pathParameters') or {},
        'query_parameters': event.get('queryStringParameters') or {},
        'headers': event.get('headers') or {},
        'body': None,
        'user': {}
    }
    
    # Parse JSON body if present
    if 'body' in event and event['body']:
        try:
            result['body'] = json.loads(event['body'])
        except json.JSONDecodeError:
            result['body'] = event['body']
    
    # Extract user information from authorizer context
    if 'requestContext' in event and 'authorizer' in event['requestContext']:
        authorizer = event['requestContext']['authorizer']
        claims = authorizer.get('claims', {})
        
        # Extract standard Cognito claims
        result['user'] = {
            'user_id': claims.get('sub'),
            'email': claims.get('email'),
            'name': claims.get('name'),
            'username': claims.get('cognito:username'),
            'picture': claims.get('picture')
        }
    
    return result