import json
import boto3
from typing import Dict
from datetime import datetime, timezone

s3_client = boto3.client('s3', region_name='sa-east-1')

def lambda_handler(event, context):
    """
    Lambda 4: Save processing summary to S3
    """
    
    print(f"Update Metadata Lambda - Processing document: {event.get('document_id')}")
    
    try:
        # Get data from previous step
        document_id = event.get('document_id')
        bucket = event.get('bucket')
        key = event.get('key')
        indexed_documents = event.get('indexed_documents', 0)
        opensearch_index = event.get('opensearch_index')
        processing_timestamp = event.get('processing_timestamp')
        
        if not document_id:
            raise ValueError('Missing document_id')
        
        # Create processing summary and save to S3
        summary = create_processing_summary(
            document_id=document_id,
            bucket=bucket,
            key=key,
            indexed_documents=indexed_documents,
            opensearch_index=opensearch_index,
            processing_timestamp=processing_timestamp
        )
        
        # Save summary to S3
        summary_file_key = f"summaries/{document_id}.json"
        s3_client.put_object(
            Bucket=bucket,
            Key=summary_file_key,
            Body=json.dumps(summary, indent=2),
            ContentType='application/json'
        )
        
        print(f"Processing summary created for document: {document_id}")
        print(f"Summary saved to: s3://{bucket}/{summary_file_key}")
        
        return {
            'statusCode': 200,
            'document_id': document_id,
            'processing_status': 'completed',
            'indexed_documents': indexed_documents,
            'summary_file_key': summary_file_key,
            'completion_timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': summary
        }
        
    except Exception as e:
        print(f"Error creating processing summary: {str(e)}")
        raise Exception(f'Metadata update failed: {str(e)}')

def create_processing_summary(
    document_id: str,
    bucket: str,
    key: str,
    indexed_documents: int,
    opensearch_index: str,
    processing_timestamp: str
) -> Dict:
    """
    Create processing summary (placeholder for S3 JSON approach)
    """
    
    summary = {
        'document_id': document_id,
        'source': {
            'bucket': bucket,
            'key': key,
            's3_location': f"s3://{bucket}/{key}"
        },
        'processing': {
            'status': 'completed',
            'indexed_documents': indexed_documents,
            'opensearch_index': opensearch_index or 'pending',
            'processing_timestamp': processing_timestamp,
            'completion_timestamp': datetime.now(timezone.utc).isoformat()
        },
        'pipeline_version': '1.0'
    }
    
    print("Processing summary created (ready for S3 JSON approach):")
    print(json.dumps(summary, indent=2))
    
    return summary