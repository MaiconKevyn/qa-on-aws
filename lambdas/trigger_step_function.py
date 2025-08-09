import json
import boto3
import os

stepfunctions = boto3.client('stepfunctions', region_name='sa-east-1')

def lambda_handler(event, context):
    """
    Trigger Lambda: Start Step Function execution when PDF is uploaded
    """
    
    print(f"S3 Trigger Lambda - Received event: {json.dumps(event)}")
    
    try:
        # Parse S3 event
        if 'Records' in event and event['Records']:
            s3_record = event['Records'][0]['s3']
            bucket = s3_record['bucket']['name']
            key = s3_record['object']['key']
            
            # Start Step Function execution
            step_function_arn = os.environ.get('STEP_FUNCTION_ARN')
            
            if not step_function_arn:
                raise ValueError('Missing STEP_FUNCTION_ARN environment variable')
            
            execution_name = f"pdf-processing-{key.replace('/', '-').replace('.', '-')}-{context.aws_request_id[:8]}"
            
            execution_input = {
                'bucket': bucket,
                'key': key
            }
            
            response = stepfunctions.start_execution(
                stateMachineArn=step_function_arn,
                name=execution_name,
                input=json.dumps(execution_input)
            )
            
            print(f"Started Step Function execution: {response['executionArn']}")
            
            return {
                'statusCode': 200,
                'body': {
                    'message': 'Step Function execution started successfully',
                    'executionArn': response['executionArn'],
                    'bucket': bucket,
                    'key': key
                }
            }
            
        else:
            raise ValueError('Invalid S3 event format')
            
    except Exception as e:
        print(f"Error starting Step Function: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': f'Failed to start Step Function: {str(e)}'}
        }