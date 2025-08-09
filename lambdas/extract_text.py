import json
import boto3
import fitz  # PyMuPDF
import os
from typing import List, Dict
from datetime import datetime, timezone

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Lambda 1: Extract text from PDF using PyMuPDF
    """
    
    print(f"Extract Text Lambda - Received event: {json.dumps(event)}")
    
    try:
        # Parse input from Step Function or S3 event
        if 'Records' in event and event['Records']:
            # S3 Event format (initial trigger)
            s3_record = event['Records'][0]['s3']
            bucket = s3_record['bucket']['name']
            key = s3_record['object']['key']
        else:
            # Step Function format
            bucket = event.get('bucket') or os.environ.get('BUCKET_NAME')
            key = event.get('key') or event.get('s3_key')
        
        if not bucket or not key:
            raise ValueError('Missing bucket or key in event')
        
        print(f"Extracting text from: s3://{bucket}/{key}")
        
        # Download PDF from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        pdf_content = response['Body'].read()
        
        # Extract text using PyMuPDF
        extracted_data = extract_text_from_pdf(pdf_content, key)
        
        # Save extracted text to S3 as JSON
        extracted_file_key = f"extracted/{extracted_data['document_id']}.json"
        extracted_json = {
            'document_id': extracted_data['document_id'],
            'source_bucket': bucket,
            'source_key': key,
            'total_pages': extracted_data['total_pages'],
            'chunks': extracted_data['chunks'],
            'metadata': extracted_data['metadata'],
            'extraction_timestamp': datetime.now(timezone.utc).isoformat(),
            'pipeline_stage': 'text_extraction'
        }
        
        s3_client.put_object(
            Bucket=bucket,
            Key=extracted_file_key,
            Body=json.dumps(extracted_json, indent=2),
            ContentType='application/json'
        )
        
        print(f"Successfully extracted {len(extracted_data['chunks'])} text chunks")
        print(f"Saved extracted data to: s3://{bucket}/{extracted_file_key}")
        
        return {
            'statusCode': 200,
            'bucket': bucket,
            'key': key,
            'document_id': extracted_data['document_id'],
            'total_pages': extracted_data['total_pages'],
            'chunks': extracted_data['chunks'],
            'metadata': extracted_data['metadata'],
            'extracted_file_key': extracted_file_key,
            'processing_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f'Text extraction failed: {str(e)}')

def extract_text_from_pdf(pdf_content: bytes, document_id: str) -> Dict:
    """
    Extract text from PDF using PyMuPDF with chunking for better retrieval
    """
    
    # Open PDF from memory
    pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
    
    document_data = {
        'document_id': document_id,
        'total_pages': len(pdf_document),
        'chunks': [],
        'metadata': {}
    }
    
    # Extract text page by page
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text = page.get_text()
        
        if text.strip():  # Only process pages with text
            # Split into smaller chunks for better retrieval
            chunks = chunk_text(text, chunk_size=1000, overlap=100)
            
            for i, chunk in enumerate(chunks):
                document_data['chunks'].append({
                    'page': page_num + 1,
                    'chunk_id': f"page_{page_num + 1}_chunk_{i + 1}",
                    'text': chunk.strip(),
                    'char_count': len(chunk)
                })
    
    # Extract metadata
    metadata = pdf_document.metadata
    document_data['metadata'] = {
        'title': metadata.get('title', ''),
        'author': metadata.get('author', ''),
        'subject': metadata.get('subject', ''),
        'creator': metadata.get('creator', ''),
        'producer': metadata.get('producer', ''),
        'creation_date': metadata.get('creationDate', ''),
        'modification_date': metadata.get('modDate', '')
    }
    
    pdf_document.close()
    
    return document_data

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks for better context preservation
    """
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence end
        if end < len(text):
            # Look for sentence endings near the chunk boundary
            sentence_end = text.rfind('.', start, end)
            if sentence_end > start + chunk_size // 2:
                end = sentence_end + 1
        
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks