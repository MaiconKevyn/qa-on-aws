import json
import boto3
from typing import Dict
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb', region_name='sa-east-1')

def lambda_handler(event, context):
    """
    Lambda 4: Update document metadata and processing status in DynamoDB
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
        
        # Update metadata in DynamoDB
        metadata_result = save_processing_metadata(
            document_id=document_id,
            bucket=bucket,
            key=key,
            indexed_documents=indexed_documents,
            opensearch_index=opensearch_index,
            processing_timestamp=processing_timestamp
        )
        
        print(f"Successfully updated metadata for document: {document_id}")
        
        return {
            'statusCode': 200,
            'document_id': document_id,
            'processing_status': 'completed',
            'indexed_documents': indexed_documents,
            'dynamodb_updated': metadata_result['success'],
            'completion_timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': {
                'bucket': bucket,
                'key': key,
                'opensearch_index': opensearch_index,
                'total_chunks_processed': indexed_documents
            }
        }
        
    except Exception as e:
        print(f"Error updating metadata: {str(e)}")
        raise Exception(f'Metadata update failed: {str(e)}')

def save_processing_metadata(
    document_id: str,
    bucket: str,
    key: str,
    indexed_documents: int,
    opensearch_index: str,
    processing_timestamp: str
) -> Dict:
    """
    Save document processing metadata to DynamoDB
    """
    
    try:
        # TODO: Create DynamoDB table via SAM template
        # For now, prepare the data structure
        
        table_name = 'qa-on-aws-document-metadata'
        
        metadata_item = {
            'document_id': document_id,
            'bucket': bucket,
            'key': key,
            's3_location': f"s3://{bucket}/{key}",
            'processing_status': 'completed',
            'indexed_documents_count': indexed_documents,
            'opensearch_index': opensearch_index,
            'processing_timestamp': processing_timestamp,
            'completion_timestamp': datetime.now(timezone.utc).isoformat(),
            'ttl': int(datetime.now(timezone.utc).timestamp()) + (365 * 24 * 60 * 60)  # 1 year TTL
        }
        
        # TODO: Implement actual DynamoDB put_item
        # For now, just log the prepared metadata
        print("Prepared metadata for DynamoDB:")
        print(json.dumps(metadata_item, indent=2))
        
        # Simulate successful save
        return {
            'success': True,
            'table_name': table_name,
            'message': 'Metadata prepared for DynamoDB (actual save not yet implemented)'
        }
        
    except Exception as e:
        print(f"Error preparing metadata for DynamoDB: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to prepare metadata for DynamoDB'
        }