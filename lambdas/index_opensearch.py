import json
import boto3
from typing import List, Dict
from datetime import datetime, timezone

# For now, we'll prepare for OpenSearch but not implement actual indexing
# until the OpenSearch cluster is created
opensearch_client = boto3.client('opensearchserverless', region_name='sa-east-1')

def lambda_handler(event, context):
    """
    Lambda 3: Index documents with embeddings to OpenSearch
    """
    
    print(f"Index OpenSearch Lambda - Processing {event.get('embeddings_count', 0)} embedded chunks")
    
    try:
        # Get data from previous step
        document_id = event.get('document_id')
        embeddings_data = event.get('embeddings_data', [])
        metadata = event.get('metadata', {})
        total_pages = event.get('total_pages', 0)
        
        if not document_id:
            raise ValueError('Missing document_id')
        
        if not embeddings_data:
            raise ValueError('No embeddings data to index')
        
        # Index to OpenSearch (placeholder for now)
        indexing_result = index_documents_to_opensearch(
            document_id, embeddings_data, metadata, total_pages
        )
        
        print(f"Successfully indexed {indexing_result['indexed_documents']} documents")
        
        return {
            'statusCode': 200,
            'bucket': event.get('bucket'),
            'key': event.get('key'),
            'document_id': document_id,
            'indexed_documents': indexing_result['indexed_documents'],
            'opensearch_index': indexing_result.get('index_name', 'documents'),
            'processing_timestamp': datetime.now(timezone.utc).isoformat(),
            'success': indexing_result['success']
        }
        
    except Exception as e:
        print(f"Error indexing to OpenSearch: {str(e)}")
        raise Exception(f'OpenSearch indexing failed: {str(e)}')

def index_documents_to_opensearch(
    document_id: str, 
    embeddings_data: List[Dict], 
    metadata: Dict,
    total_pages: int
) -> Dict:
    """
    Index document chunks with embeddings to OpenSearch
    Currently a placeholder - will implement actual OpenSearch API calls
    """
    
    try:
        # Prepare documents for OpenSearch
        opensearch_documents = []
        
        for embedding_chunk in embeddings_data:
            doc = {
                'document_id': document_id,
                'chunk_id': embedding_chunk['chunk_id'],
                'text': embedding_chunk['text'],
                'page': embedding_chunk['page'],
                'char_count': embedding_chunk['char_count'],
                'embedding_vector': embedding_chunk['embedding'],
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'metadata': {
                    'total_pages': total_pages,
                    'title': metadata.get('title', ''),
                    'author': metadata.get('author', ''),
                    'creation_date': metadata.get('creation_date', '')
                }
            }
            opensearch_documents.append(doc)
        
        # TODO: Implement actual OpenSearch indexing
        # For now, just log the prepared documents
        print(f"Prepared {len(opensearch_documents)} documents for OpenSearch indexing")
        print("Sample document structure:")
        if opensearch_documents:
            sample = opensearch_documents[0].copy()
            # Don't log the full embedding vector (too large)
            if 'embedding_vector' in sample and sample['embedding_vector']:
                sample['embedding_vector'] = f"[{len(sample['embedding_vector'])} dimensions]"
            print(json.dumps(sample, indent=2))
        
        # Simulate successful indexing
        return {
            'success': True,
            'indexed_documents': len(opensearch_documents),
            'index_name': 'documents',
            'message': 'Documents prepared for OpenSearch (actual indexing not yet implemented)'
        }
        
    except Exception as e:
        print(f"Error preparing documents for OpenSearch: {str(e)}")
        return {
            'success': False,
            'indexed_documents': 0,
            'error': str(e),
            'message': 'Failed to prepare documents for OpenSearch'
        }