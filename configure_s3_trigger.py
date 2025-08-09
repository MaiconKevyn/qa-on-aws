#!/usr/bin/env python3
"""
Script para configurar S3 trigger após o deploy do SAM
Executa: python configure_s3_trigger.py
"""

import boto3
import json
import sys

def configure_s3_trigger():
    """
    Configura o S3 bucket para triggerar a Lambda quando PDF é enviado
    """
    
    # Configurações
    bucket_name = 'source-pdf-qa-aws'
    region = 'sa-east-1'
    
    # Buscar ARN da Lambda trigger do stack
    try:
        cloudformation = boto3.client('cloudformation', region_name=region)
        
        # Buscar outputs do stack
        stack_response = cloudformation.describe_stacks(StackName='qa-on-aws-dev')
        outputs = stack_response['Stacks'][0]['Outputs']
        
        trigger_lambda_arn = None
        for output in outputs:
            if output['OutputKey'] == 'TriggerLambdaArn':
                trigger_lambda_arn = output['OutputValue']
                break
        
        if not trigger_lambda_arn:
            print("❌ Erro: TriggerLambdaArn não encontrado nos outputs do stack")
            return False
            
        print(f"📋 Configurando S3 trigger:")
        print(f"   Bucket: {bucket_name}")
        print(f"   Lambda: {trigger_lambda_arn}")
        
        # Configurar S3 client
        s3_client = boto3.client('s3', region_name=region)
        lambda_client = boto3.client('lambda', region_name=region)
        
        # 1. Dar permissão para o S3 invocar a Lambda
        try:
            lambda_client.add_permission(
                FunctionName=trigger_lambda_arn.split(':')[-1],  # Nome da função
                StatementId='s3-trigger-permission',
                Action='lambda:InvokeFunction',
                Principal='s3.amazonaws.com',
                SourceArn=f'arn:aws:s3:::{bucket_name}'
            )
            print("✅ Permissão S3 → Lambda configurada")
        except lambda_client.exceptions.ResourceConflictException:
            print("✅ Permissão S3 → Lambda já existe")
        
        # 2. Configurar notificação no S3
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
        
        print("✅ S3 Event Notification configurada com sucesso!")
        print("\n🎯 Configuração completa:")
        print(f"   • Bucket: {bucket_name}")
        print(f"   • Trigger: uploads/*.pdf")
        print(f"   • Lambda: {trigger_lambda_arn}")
        print("\n🚀 Faça upload de um PDF em uploads/ para testar o pipeline!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar S3 trigger: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Configurando S3 Event Trigger...")
    success = configure_s3_trigger()
    sys.exit(0 if success else 1)