#!/usr/bin/env python3
"""
Script para testar o pipeline RAG completo
Simula o fluxo: Upload PDF → Step Function → Lambdas → S3 JSON files
"""

import boto3
import json
import sys
import time
from pathlib import Path

def test_pipeline():
    """
    Testa o pipeline RAG completo
    """
    
    try:
        # Configurações
        bucket_name = 'source-pdf-qa-aws'
        region = 'sa-east-1'
        
        print("🧪 Testando Pipeline RAG...")
        
        # Verificar se AWS CLI está configurado
        try:
            sts = boto3.client('sts', region_name=region)
            identity = sts.get_caller_identity()
            print(f"✅ AWS configurado - Account: {identity['Account']}")
        except Exception as e:
            print(f"❌ AWS CLI não configurado: {e}")
            return False
        
        # Verificar se o bucket existe
        s3_client = boto3.client('s3', region_name=region)
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket existe: {bucket_name}")
        except Exception as e:
            print(f"❌ Bucket não encontrado: {e}")
            print("💡 Execute: aws s3 mb s3://source-pdf-qa-aws --region sa-east-1")
            return False
        
        # Verificar se o stack do CloudFormation existe
        cf = boto3.client('cloudformation', region_name=region)
        try:
            stacks = cf.describe_stacks(StackName='qa-on-aws-dev')
            stack = stacks['Stacks'][0]
            print(f"✅ Stack CloudFormation: {stack['StackStatus']}")
            
            # Extrair ARNs das Lambdas
            outputs = {output['OutputKey']: output['OutputValue'] 
                      for output in stack.get('Outputs', [])}
            
            if 'TriggerLambdaArn' in outputs:
                print(f"✅ Trigger Lambda: {outputs['TriggerLambdaArn']}")
            if 'RAGStateMachineArn' in outputs:
                print(f"✅ Step Function: {outputs['RAGStateMachineArn']}")
                
        except Exception as e:
            print(f"❌ Stack não encontrado: {e}")
            print("💡 Execute: sam deploy")
            return False
        
        # Verificar estrutura de pastas no S3
        print(f"\n📁 Verificando estrutura S3...")
        folders = ['uploads/', 'extracted/', 'embeddings/', 'indexed/', 'summaries/']
        
        for folder in folders:
            try:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=folder,
                    MaxKeys=1
                )
                if 'Contents' in response:
                    print(f"✅ {folder}")
                else:
                    print(f"⚠️  {folder} (vazia)")
            except Exception as e:
                print(f"❌ {folder}: {e}")
        
        # Verificar se existe algum PDF de teste
        try:
            test_pdfs = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix='uploads/',
                MaxKeys=10
            )
            
            if 'Contents' in test_pdfs:
                pdfs = [obj['Key'] for obj in test_pdfs['Contents'] if obj['Key'].endswith('.pdf')]
                if pdfs:
                    print(f"\n📄 PDFs encontrados: {len(pdfs)}")
                    for pdf in pdfs[:3]:  # Mostrar só os 3 primeiros
                        print(f"   • {pdf}")
                        
                        # Verificar se existe arquivo extraído correspondente
                        doc_id = pdf.replace('uploads/', '').replace('.pdf', '')
                        extracted_key = f"extracted/{doc_id}.json"
                        
                        try:
                            s3_client.head_object(Bucket=bucket_name, Key=extracted_key)
                            print(f"     ✅ Extraído: {extracted_key}")
                        except:
                            print(f"     ❌ Não extraído ainda: {extracted_key}")
                else:
                    print(f"\n📄 Nenhum PDF encontrado em uploads/")
            else:
                print(f"\n📄 Pasta uploads/ está vazia")
                
        except Exception as e:
            print(f"❌ Erro verificando PDFs: {e}")
        
        print(f"\n🎯 Status do Pipeline:")
        print(f"   1. ✅ AWS configurado")
        print(f"   2. ✅ Bucket S3 existe")
        print(f"   3. ✅ Stack CloudFormation deployado")
        print(f"   4. ⚠️  S3 trigger precisa ser configurado manualmente")
        
        print(f"\n📋 Próximos passos:")
        print(f"   1. Execute: python3 create_s3_folders.py")
        print(f"   2. Execute: python3 configure_s3_trigger.py")
        print(f"   3. Faça upload de um PDF: aws s3 cp arquivo.pdf s3://{bucket_name}/uploads/")
        print(f"   4. Verifique os logs no CloudWatch")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testando configuração do Pipeline RAG...")
    success = test_pipeline()
    sys.exit(0 if success else 1)