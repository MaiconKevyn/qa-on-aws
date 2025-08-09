#!/usr/bin/env python3
"""
Script completo para configurar o pipeline RAG após o deploy
1. Cria estrutura de pastas S3
2. Configura S3 trigger
3. Testa o pipeline
"""

import boto3
import json
import sys
import time

def setup_complete_pipeline():
    """
    Configura o pipeline RAG completo
    """
    
    # Configurações
    bucket_name = 'source-pdf-qa-aws'
    region = 'sa-east-1'
    stack_name = 'qa-on-aws-dev'
    
    try:
        print("🚀 Configurando Pipeline RAG completo...")
        
        # 1. Criar estrutura de pastas S3
        print("\n📁 Etapa 1: Criando estrutura S3...")
        create_s3_structure(bucket_name, region)
        
        # 2. Configurar S3 trigger
        print("\n🔗 Etapa 2: Configurando S3 trigger...")
        configure_s3_trigger(bucket_name, region, stack_name)
        
        # 3. Verificar configuração
        print("\n✅ Etapa 3: Verificando configuração...")
        verify_setup(bucket_name, region, stack_name)
        
        print("\n🎯 Pipeline configurado com sucesso!")
        print(f"\n📋 Para testar:")
        print(f"   1. Faça upload de um PDF:")
        print(f"      aws s3 cp arquivo.pdf s3://{bucket_name}/uploads/")
        print(f"   2. Aguarde alguns segundos e verifique:")
        print(f"      aws s3 ls s3://{bucket_name}/extracted/")
        print(f"   3. Monitore os logs:")
        print(f"      aws logs tail /aws/lambda/qa-on-aws-dev-trigger-step-function --follow")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def create_s3_structure(bucket_name, region):
    """Cria estrutura de pastas no S3"""
    
    s3_client = boto3.client('s3', region_name=region)
    
    folders = [
        'uploads/',
        'extracted/', 
        'embeddings/',
        'indexed/',
        'summaries/',
    ]
    
    for folder in folders:
        try:
            placeholder_key = f"{folder}.gitkeep"
            s3_client.put_object(
                Bucket=bucket_name,
                Key=placeholder_key,
                Body="# Folder structure for RAG pipeline\n",
                ContentType='text/plain'
            )
            print(f"   ✅ {folder}")
        except Exception as e:
            print(f"   ⚠️  {folder}: {e}")

def configure_s3_trigger(bucket_name, region, stack_name):
    """Configura S3 trigger para iniciar Step Function"""
    
    try:
        # Obter ARN da Lambda trigger do stack
        cf = boto3.client('cloudformation', region_name=region)
        stack_response = cf.describe_stacks(StackName=stack_name)
        outputs = stack_response['Stacks'][0]['Outputs']
        
        trigger_lambda_arn = None
        for output in outputs:
            if output['OutputKey'] == 'TriggerLambdaArn':
                trigger_lambda_arn = output['OutputValue']
                break
        
        if not trigger_lambda_arn:
            raise ValueError("TriggerLambdaArn não encontrado nos outputs")
        
        print(f"   📋 Lambda ARN: {trigger_lambda_arn}")
        
        # Configurar clientes
        s3_client = boto3.client('s3', region_name=region)
        lambda_client = boto3.client('lambda', region_name=region)
        
        # 1. Dar permissão S3 → Lambda
        function_name = trigger_lambda_arn.split(':')[-1]
        
        try:
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId='s3-trigger-permission',
                Action='lambda:InvokeFunction',
                Principal='s3.amazonaws.com',
                SourceArn=f'arn:aws:s3:::{bucket_name}'
            )
            print(f"   ✅ Permissão S3 → Lambda configurada")
        except lambda_client.exceptions.ResourceConflictException:
            print(f"   ✅ Permissão S3 → Lambda já existe")
        
        # 2. Configurar notificação S3
        notification_config = {
            'LambdaFunctionConfigurations': [
                {
                    'Id': 'pdf-upload-trigger',
                    'LambdaFunctionArn': trigger_lambda_arn,
                    'Events': ['s3:ObjectCreated:*'],
                    'Filter': {
                        'Key': {
                            'FilterRules': [
                                {'Name': 'prefix', 'Value': 'uploads/'},
                                {'Name': 'suffix', 'Value': '.pdf'}
                            ]
                        }
                    }
                }
            ]
        }
        
        s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration=notification_config
        )
        
        print(f"   ✅ S3 Event Notification configurada")
        print(f"   🎯 Trigger: uploads/*.pdf → {function_name}")
        
    except Exception as e:
        print(f"   ❌ Erro configurando S3 trigger: {e}")
        raise

def verify_setup(bucket_name, region, stack_name):
    """Verifica se tudo está configurado corretamente"""
    
    try:
        # Verificar stack
        cf = boto3.client('cloudformation', region_name=region)
        stack = cf.describe_stacks(StackName=stack_name)['Stacks'][0]
        print(f"   ✅ Stack: {stack['StackStatus']}")
        
        # Verificar bucket
        s3_client = boto3.client('s3', region_name=region)
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"   ✅ Bucket: {bucket_name}")
        
        # Verificar pastas
        folders = ['uploads/', 'extracted/', 'embeddings/', 'indexed/', 'summaries/']
        folder_count = 0
        for folder in folders:
            try:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=folder,
                    MaxKeys=1
                )
                if 'Contents' in response:
                    folder_count += 1
            except:
                pass
        
        print(f"   ✅ Estrutura S3: {folder_count}/{len(folders)} pastas")
        
        # Verificar notificação S3
        try:
            notification = s3_client.get_bucket_notification_configuration(Bucket=bucket_name)
            if 'LambdaFunctionConfigurations' in notification:
                print(f"   ✅ S3 Trigger: Configurado")
            else:
                print(f"   ⚠️  S3 Trigger: Não encontrado")
        except:
            print(f"   ⚠️  S3 Trigger: Erro ao verificar")
        
    except Exception as e:
        print(f"   ❌ Erro na verificação: {e}")

if __name__ == "__main__":
    print("⚙️  Configurando Pipeline RAG...")
    success = setup_complete_pipeline()
    sys.exit(0 if success else 1)