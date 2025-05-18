"""Lambda handler for getting all sites."""

import json
import logging
from typing import Dict, Any, List

from src.common import (
    success_response,
    error_response,
    query_gsi2,
    format_site_from_dynamo
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_all_sites() -> List[Dict[str, Any]]:
    """Get all sites.
    
    Returns:
        List of site objects
    """
    # Query GSI2 (Type) to get all sites
    items = query_gsi2(type_value='SITE', limit=100)
    
    # Format response
    return [format_site_from_dynamo(item) for item in items]


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /api/sites.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    logger.info(f"Processing event: {json.dumps(event)}")
    
    try:
        # Get all sites
        sites = get_all_sites()
        
        return success_response(sites)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return error_response(f"Error retrieving sites: {str(e)}", 500)


if __name__ == "__main__":
    # For local testing
    test_event: Dict[str, Any] = {}
    print(handler(test_event, None))