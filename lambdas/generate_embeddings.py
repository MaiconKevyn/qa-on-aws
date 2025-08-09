import json
import boto3
from typing import List, Dict

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    """
    Lambda 2: Generate embeddings using Amazon Bedrock
    """
    
    print(f"Generate Embeddings Lambda - Processing {len(event.get('chunks', []))} chunks")
    
    try:
        # Get chunks from previous step
        chunks = event.get('chunks', [])
        document_id = event.get('document_id')
        
        if not chunks:
            raise ValueError('No chunks to process')
        
        if not document_id:
            raise ValueError('Missing document_id')
        
        # Generate embeddings for all chunks
        embeddings_data = generate_embeddings_bedrock(chunks)
        
        print(f"Successfully generated embeddings for {len(embeddings_data)} chunks")
        
        return {
            'statusCode': 200,
            'bucket': event.get('bucket'),
            'key': event.get('key'),
            'document_id': document_id,
            'total_pages': event.get('total_pages'),
            'metadata': event.get('metadata'),
            'timestamp': event.get('timestamp'),
            'embeddings_data': embeddings_data,
            'embeddings_count': len(embeddings_data)
        }
        
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        raise Exception(f'Embeddings generation failed: {str(e)}')

def generate_embeddings_bedrock(chunks: List[Dict]) -> List[Dict]:
    """
    Generate embeddings using Amazon Bedrock Titan Embeddings
    """
    
    embeddings_data = []
    
    for chunk in chunks:
        try:
            # Prepare request for Bedrock Titan Embeddings
            body = json.dumps({
                "inputText": chunk['text']
            })
            
            # Call Bedrock
            response = bedrock_runtime.invoke_model(
                body=body,
                modelId="amazon.titan-embed-text-v1",
                accept="application/json",
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response.get('body').read())
            embedding = response_body.get('embedding')
            
            embeddings_data.append({
                'chunk_id': chunk['chunk_id'],
                'text': chunk['text'],
                'page': chunk['page'],
                'embedding': embedding,
                'char_count': chunk['char_count']
            })
            
            print(f"Generated embedding for chunk: {chunk['chunk_id']}")
            
        except Exception as e:
            print(f"Error generating embedding for chunk {chunk['chunk_id']}: {str(e)}")
            # Continue with other chunks instead of failing completely
            continue
    
    return embeddings_data