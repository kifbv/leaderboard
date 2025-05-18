"""DynamoDB utility functions for leaderboard application."""

import os
import boto3
from typing import Any, Dict, List, Optional
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'leaderboard-dev'))


def get_item(pk: str, sk: str) -> Optional[Dict[str, Any]]:
    """Get a single item from DynamoDB.
    
    Args:
        pk: Partition key
        sk: Sort key
        
    Returns:
        Item dict or None if not found
    """
    response = table.get_item(Key={'PK': pk, 'SK': sk})
    return response.get('Item', None)


def query_items(pk: str, sk_begins_with: Optional[str] = None, 
                limit: int = 20) -> List[Dict[str, Any]]:
    """Query items by partition key with optional sort key prefix.
    
    Args:
        pk: Partition key
        sk_begins_with: Optional sort key prefix
        limit: Maximum number of items to return
        
    Returns:
        List of item dicts
    """
    key_condition = Key('PK').eq(pk)
    if sk_begins_with:
        key_condition = key_condition & Key('SK').begins_with(sk_begins_with)
        
    response = table.query(
        KeyConditionExpression=key_condition,
        Limit=limit
    )
    
    return response.get('Items', [])


def query_gsi1(sk: str, pk_begins_with: Optional[str] = None, 
              limit: int = 20) -> List[Dict[str, Any]]:
    """Query GSI1 (inverted index) by SK with optional PK prefix.
    
    Args:
        sk: Sort key (GSI1 partition key)
        pk_begins_with: Optional partition key prefix (GSI1 sort key)
        limit: Maximum number of items to return
        
    Returns:
        List of item dicts
    """
    key_condition = Key('SK').eq(sk)
    if pk_begins_with:
        key_condition = key_condition & Key('PK').begins_with(pk_begins_with)
        
    response = table.query(
        IndexName='GSI1',
        KeyConditionExpression=key_condition,
        Limit=limit
    )
    
    return response.get('Items', [])


def query_gsi2(type_value: str, limit: int = 20,
               elo_score_gt: Optional[int] = None) -> List[Dict[str, Any]]:
    """Query GSI2 (Type, EloScore) to get top players.
    
    Args:
        type_value: The Type value ('PLAYER', 'GAME', etc.)
        limit: Maximum number of items to return
        elo_score_gt: Optional minimum ELO score
        
    Returns:
        List of item dicts
    """
    key_condition = Key('Type').eq(type_value)
    if elo_score_gt is not None:
        key_condition = key_condition & Key('EloScore').gt(elo_score_gt)
        
    response = table.query(
        IndexName='GSI2',
        KeyConditionExpression=key_condition,
        ScanIndexForward=False,  # Sort descending
        Limit=limit
    )
    
    return response.get('Items', [])


def query_gsi3(site_id: str, type_value: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Query GSI3 (SiteId, Type) to get site-specific data.
    
    Args:
        site_id: Site ID
        type_value: The Type value ('PLAYER', 'GAME', etc.)
        limit: Maximum number of items to return
        
    Returns:
        List of item dicts
    """
    key_condition = Key('SiteId').eq(site_id) & Key('Type').eq(type_value)
        
    response = table.query(
        IndexName='GSI3',
        KeyConditionExpression=key_condition,
        Limit=limit
    )
    
    return response.get('Items', [])


def put_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Put an item into DynamoDB.
    
    Args:
        item: Item dict with PK and SK
        
    Returns:
        Response from DynamoDB
    """
    return table.put_item(Item=item)


def update_item(pk: str, sk: str, update_expression: str, 
                expression_values: Dict[str, Any],
                condition_expression: Optional[str] = None) -> Dict[str, Any]:
    """Update an item in DynamoDB.
    
    Args:
        pk: Partition key
        sk: Sort key
        update_expression: Update expression
        expression_values: Expression attribute values
        condition_expression: Optional condition expression
        
    Returns:
        Response from DynamoDB
    """
    update_args = {
        'Key': {'PK': pk, 'SK': sk},
        'UpdateExpression': update_expression,
        'ExpressionAttributeValues': expression_values,
        'ReturnValues': 'ALL_NEW'
    }
    
    if condition_expression:
        update_args['ConditionExpression'] = condition_expression
        
    return table.update_item(**update_args)


def batch_write_items(items: List[Dict[str, Any]]) -> None:
    """Write multiple items to DynamoDB in a batch.
    
    Args:
        items: List of item dicts with PK and SK
    """
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)