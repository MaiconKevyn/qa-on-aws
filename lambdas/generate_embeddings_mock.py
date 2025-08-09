import json
import boto3
from typing import List, Dict
from datetime import datetime, timezone
import random

s3_client = boto3.client('s3', region_name='sa-east-1')

def lambda_handler(event, context):
    """
    Lambda 2: Generate MOCK embeddings (for testing without Bedrock access)
    """
    
    print(f"Generate Embeddings Lambda (MOCK) - Processing document: {event.get('document_id')}")
    
    try:
        # Get data from previous step
        document_id = event.get('document_id')
        bucket = event.get('bucket')
        extracted_file_key = event.get('extracted_file_key')
        
        if not document_id:
            raise ValueError('Missing document_id')
        
        # Read extracted text from S3 JSON file
        if extracted_file_key:
            print(f"Reading extracted data from: s3://{bucket}/{extracted_file_key}")
            response = s3_client.get_object(Bucket=bucket, Key=extracted_file_key)
            extracted_data = json.loads(response['Body'].read().decode('utf-8'))
            chunks = extracted_data['chunks']
        else:
            # Fallback to chunks passed directly (for backward compatibility)
            chunks = event.get('chunks', [])
        
        if not chunks:
            raise ValueError('No chunks to process')
        
        print(f"Processing {len(chunks)} chunks for MOCK embeddings")
        
        # Generate MOCK embeddings for all chunks
        embeddings_data = generate_mock_embeddings(chunks)
        
        # Save embeddings to S3 as JSON
        embeddings_file_key = f"embeddings/{document_id}.json"
        embeddings_json = {
            'document_id': document_id,
            'source_bucket': bucket,
            'source_key': event.get('key'),
            'extracted_file_key': extracted_file_key,
            'embeddings_data': embeddings_data,
            'embeddings_count': len(embeddings_data),
            'embedding_model': 'MOCK-amazon.titan-embed-text-v1',
            'embeddings_timestamp': datetime.now(timezone.utc).isoformat(),
            'pipeline_stage': 'embeddings_generation',
            'note': 'MOCK embeddings for testing - replace with real Bedrock when access is granted'
        }
        
        s3_client.put_object(
            Bucket=bucket,
            Key=embeddings_file_key,
            Body=json.dumps(embeddings_json, indent=2),
            ContentType='application/json'
        )
        
        print(f"Successfully generated MOCK embeddings for {len(embeddings_data)} chunks")
        print(f"Saved embeddings data to: s3://{bucket}/{embeddings_file_key}")
        
        return {
            'statusCode': 200,
            'bucket': bucket,
            'key': event.get('key'),
            'document_id': document_id,
            'total_pages': event.get('total_pages'),
            'metadata': event.get('metadata'),
            'extracted_file_key': extracted_file_key,
            'embeddings_file_key': embeddings_file_key,
            'embeddings_data': embeddings_data,
            'embeddings_count': len(embeddings_data),
            'processing_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"Error generating MOCK embeddings: {str(e)}")
        raise Exception(f'Embeddings generation failed: {str(e)}')

def generate_mock_embeddings(chunks: List[Dict]) -> List[Dict]:
    """
    Generate MOCK embeddings (random vectors) for testing
    Real Titan embeddings are 1536 dimensions
    """
    
    embeddings_data = []
    
    for chunk in chunks:
        try:
            # Generate MOCK embedding (1536 random values between -1 and 1)
            mock_embedding = [random.uniform(-1, 1) for _ in range(1536)]
            
            embeddings_data.append({
                'chunk_id': chunk['chunk_id'],
                'text': chunk['text'],
                'page': chunk['page'],
                'embedding': mock_embedding,
                'char_count': chunk['char_count'],
                'embedding_model': 'MOCK-titan-embed-text-v1'
            })
            
            print(f"Generated MOCK embedding for chunk: {chunk['chunk_id']}")
            
        except Exception as e:
            print(f"Error generating MOCK embedding for chunk {chunk['chunk_id']}: {str(e)}")
            continue
    
    return embeddings_data