"""Lambda handler for creating a new site (admin only)."""

import json
import logging
from typing import Dict, Any, List, Optional

from src.common import (
    success_response,
    error_response,
    parse_event,
    put_item,
    generate_id,
    get_current_timestamp,
    format_site_for_dynamo,
    SiteData
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_site(name: str, location: str) -> Dict[str, Any]:
    """Create a new site.
    
    Args:
        name: Site name
        location: Site location
        
    Returns:
        Created site data
    """
    # Generate site ID
    site_id = generate_id("site-")
    
    # Create site data
    site_data: SiteData = {
        'site_id': site_id,
        'name': name,
        'location': location,
        'created_at': get_current_timestamp()
    }
    
    # Format for DynamoDB
    site_item = format_site_for_dynamo(site_data)
    
    # Write to DynamoDB
    put_item(site_item)
    
    return site_data


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for POST /api/sites.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    logger.info(f"Processing event: {json.dumps(event)}")
    
    try:
        # Parse event
        parsed_event = parse_event(event)
        body = parsed_event['body']
        
        # Validate request body
        if not body:
            return error_response("Request body is required", 400)
        
        # Extract site data
        name = body.get('name')
        location = body.get('location')
        
        # Validate required fields
        if not name:
            return error_response("name is required", 400)
        
        if not location:
            return error_response("location is required", 400)
        
        # Create site
        site = create_site(name, location)
        
        return success_response(site, 201)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return error_response(f"Error creating site: {str(e)}", 500)


if __name__ == "__main__":
    # For local testing
    test_event = {
        "body": json.dumps({
            "name": "Headquarters",
            "location": "San Francisco, CA"
        })
    }
    print(handler(test_event, None))