import json

def lambda_handler(event, context):
    """
    Simple PDF processing Lambda
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    # Process the PDF here
    # For now, just return a success response
    
    return {
        'statusCode': 200,
        'body': {
            'message': 'PDF processed successfully',
            'event': event
        }
    }