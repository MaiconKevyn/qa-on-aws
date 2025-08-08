#!/usr/bin/env python3
"""
Script simples para upload de PDF local para S3
Uso: python upload_pdf.py caminho/para/arquivo.pdf
"""

import sys
import os
from datetime import datetime
from app.services.s3_service import S3Service

def main():
    # Arquivo fixo para teste
    file_path = "MaiconKevyn_cv.pdf"
    
    # Verificar se arquivo existe
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        sys.exit(1)
    
    # Verificar se é PDF
    if not file_path.lower().endswith('.pdf'):
        print("❌ Apenas arquivos PDF são permitidos")
        sys.exit(1)
    
    # Verificar tamanho (10MB max)
    file_size = os.path.getsize(file_path)
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        print(f"❌ Arquivo muito grande: {file_size/1024/1024:.1f}MB (máximo: 10MB)")
        sys.exit(1)
    
    print(f"📄 Arquivo: {os.path.basename(file_path)}")
    print(f"📦 Tamanho: {file_size/1024/1024:.2f}MB")
    print(f"🚀 Fazendo upload para S3...")
    
    try:
        # Criar serviço S3
        s3_service = S3Service()
        
        # Fazer upload
        with open(file_path, 'rb') as file_obj:
            result = s3_service.upload_file(file_obj, os.path.basename(file_path))
        
        if result['success']:
            print(f"✅ Upload realizado com sucesso!")
            print(f"   📁 Bucket: {result['bucket']}")
            print(f"   🔗 Chave S3: {result['s3_key']}")
            print(f"   📄 Nome único: {result['filename']}")
            print(f"   🌐 URL: {result['url']}")
        else:
            print(f"❌ Falha no upload: {result['message']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()