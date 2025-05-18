"""Lambda authorizer for admin-only endpoints."""

import os
import json
import logging
from typing import Dict, Any, List

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for admin authorization.
    
    Args:
        event: API Gateway event with Cognito authorizer
        context: Lambda context
        
    Returns:
        API Gateway custom authorizer response
    """
    logger.info(f"Processing event: {json.dumps(event)}")
    
    try:
        # Extract user claims from Cognito
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        
        # Get user email
        user_email = claims.get('email')
        if not user_email:
            logger.warning("No email found in claims")
            return generate_deny_response("Unauthorized")
        
        # Get list of admin emails from environment variable
        admin_emails_str = os.environ.get('ADMIN_EMAILS', '')
        admin_emails = [email.strip() for email in admin_emails_str.split(',')]
        
        # Check if user email is in admin list
        if user_email in admin_emails:
            return generate_allow_response(user_email)
        else:
            logger.warning(f"User {user_email} is not an admin")
            return generate_deny_response("Forbidden")
    
    except Exception as e:
        logger.error(f"Error processing authorization: {str(e)}", exc_info=True)
        return generate_deny_response("Server Error")


def generate_allow_response(user_email: str) -> Dict[str, Any]:
    """Generate an allow response for API Gateway custom authorizer.
    
    Args:
        user_email: User email
        
    Returns:
        API Gateway custom authorizer response
    """
    return {
        'principalId': user_email,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': 'Allow',
                    'Resource': '*'
                }
            ]
        },
        'context': {
            'isAdmin': 'true'
        }
    }


def generate_deny_response(message: str) -> Dict[str, Any]:
    """Generate a deny response for API Gateway custom authorizer.
    
    Args:
        message: Error message
        
    Returns:
        API Gateway custom authorizer response
    """
    return {
        'principalId': 'user',
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': 'Deny',
                    'Resource': '*'
                }
            ]
        },
        'context': {
            'error': message
        }
    }