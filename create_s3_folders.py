#!/usr/bin/env python3
"""
Script para criar estrutura de pastas S3 para data lineage
Executa: python create_s3_folders.py
"""

import boto3
import json

def create_s3_folder_structure():
    """
    Cria estrutura de pastas no S3 para data lineage do RAG pipeline
    """
    
    # Configurações
    bucket_name = 'source-pdf-qa-aws'
    region = 'sa-east-1'
    
    # Estrutura de pastas para data lineage
    folders = [
        'uploads/',          # PDFs originais
        'extracted/',        # Texto extraído em JSON
        'embeddings/',       # Embeddings gerados em JSON
        'indexed/',          # Resultados da indexação em JSON
        'summaries/',        # Resumos finais do processamento
    ]
    
    try:
        s3_client = boto3.client('s3', region_name=region)
        
        print(f"📁 Criando estrutura de pastas em: {bucket_name}")
        
        for folder in folders:
            # Criar "pasta" no S3 usando um placeholder file
            placeholder_key = f"{folder}.gitkeep"
            
            s3_client.put_object(
                Bucket=bucket_name,
                Key=placeholder_key,
                Body="# Placeholder file to maintain folder structure\n",
                ContentType='text/plain'
            )
            
            print(f"   ✅ {folder}")
        
        # Criar um arquivo de documentação da estrutura
        documentation = {
            "data_lineage_structure": {
                "description": "S3 folder structure for RAG pipeline data lineage",
                "folders": {
                    "uploads/": "Original PDF files uploaded by users",
                    "extracted/": "Extracted text data in JSON format from PyMuPDF",
                    "embeddings/": "Generated embeddings in JSON format from Amazon Bedrock",
                    "indexed/": "OpenSearch indexing results and metadata in JSON",
                    "summaries/": "Final processing summaries and pipeline status"
                },
                "benefits": [
                    "Complete audit trail of document processing",
                    "Easy debugging and troubleshooting",
                    "Ability to reprocess from any stage",
                    "Data lake architecture for analytics",
                    "Cost-effective intermediate storage"
                ]
            },
            "created": "2024-01-01T00:00:00Z",
            "version": "1.0"
        }
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key='data-lineage-structure.json',
            Body=json.dumps(documentation, indent=2),
            ContentType='application/json'
        )
        
        print("✅ data-lineage-structure.json")
        print(f"\n🎯 Estrutura S3 criada com sucesso!")
        print(f"   Bucket: s3://{bucket_name}")
        print("   Estrutura:")
        for folder in folders:
            print(f"     • {folder}")
        
        print(f"\n📋 Documentação salva em: s3://{bucket_name}/data-lineage-structure.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar estrutura S3: {str(e)}")
        return False

if __name__ == "__main__":
    print("🏗️  Criando estrutura de pastas S3...")
    success = create_s3_folder_structure()
    exit(0 if success else 1)