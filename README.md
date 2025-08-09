# 🧠 QA on AWS - RAG Pipeline

Sistema de processamento de documentos PDF usando arquitetura serverless na AWS com Step Functions e Flask.

## 📋 Visão Geral

Este projeto implementa um pipeline RAG (Retrieval-Augmented Generation) completo que:
- Recebe documentos PDF via interface web Flask
- Processa automaticamente através de Step Functions
- Extrai texto, gera embeddings e indexa no OpenSearch
- Mantém lineage completo dos dados processados

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask Web     │    │   AWS S3        │    │ Step Functions  │
│   Interface     │───▶│   Bucket        │───▶│   Orchestrator  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Pipeline RAG - 4 Lambdas                     │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│ 1. Extract Text │ 2. Generate     │ 3. Index        │ 4. Update │
│    (PyMuPDF)    │    Embeddings   │    OpenSearch   │ Metadata  │
│                 │    (Bedrock)    │                 │           │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   S3 Data       │
                    │   Lineage       │
                    │                 │
                    └─────────────────┘
```

## 🗂️ Estrutura do Projeto

```
qa-on-aws/
├── app.py                      # Aplicação Flask principal
├── requirements.txt            # Dependências Python
├── template.yaml              # Infraestrutura SAM (CloudFormation)
├── configure_s3_trigger.py    # Script configuração S3 → Lambda
├── setup_complete_pipeline.py # Setup automático completo
├── test_pipeline.py           # Testes do pipeline
│
├── lambdas/                   # Funções Lambda
│   ├── trigger_step_function.py  # [Trigger] S3 Event → Step Function
│   ├── extract_text.py           # [1] PDF → Texto extraído
│   ├── generate_embeddings.py    # [2] Texto → Embeddings Bedrock
│   ├── index_opensearch.py       # [3] Embeddings → OpenSearch
│   ├── update_metadata.py        # [4] Metadados finais
│   └── requirements.txt          # Dependências Lambda
│
├── state_machines/
│   └── processing.json        # Workflow Step Functions
│
└── templates/                 # Templates Flask
    ├── base.html             # Template base
    ├── index.html            # Página inicial
    ├── upload.html           # Upload de PDFs
    └── files.html            # Lista arquivos
```

## 🔄 Fluxo de Processamento

### 1. **Upload via Flask**
```
Usuario → Flask Web Interface → S3 Bucket (uploads/)
```

### 2. **Trigger Automático**
```
S3 Event → Lambda Trigger → Step Function Start
```

### 3. **Pipeline RAG (Step Functions)**
```
Step 1: extract_text.py
├── Input:  s3://bucket/uploads/documento.pdf  
└── Output: s3://bucket/extracted/documento.json

Step 2: generate_embeddings.py  
├── Input:  s3://bucket/extracted/documento.json
└── Output: s3://bucket/embeddings/documento.json

Step 3: index_opensearch.py
├── Input:  s3://bucket/embeddings/documento.json  
└── Output: s3://bucket/indexed/documento.json

Step 4: update_metadata.py
├── Input:  s3://bucket/indexed/documento.json
└── Output: s3://bucket/summaries/documento.json
```

### 4. **Data Lineage S3**
```
s3://source-pdf-qa-aws/
├── uploads/           # PDFs originais
├── extracted/         # Texto extraído (PyMuPDF)  
├── embeddings/        # Vetores embeddings (Bedrock)
├── indexed/          # Resultados OpenSearch
└── summaries/        # Resumos finais processamento
```

## 🚀 Setup e Deploy

### Pré-requisitos
- AWS CLI configurado
- SAM CLI instalado
- Python 3.11+
- Credenciais AWS com permissões apropriadas

### 1. Deploy da Infraestrutura
```bash
# Deploy do template SAM
sam deploy --guided

# Primeira execução, aceite os defaults e salve parâmetros
```

### 2. Configuração do S3 Trigger
```bash
# Configurar evento S3 → Lambda (necessário após primeiro deploy)
python3 configure_s3_trigger.py
```

### 3. Setup Completo (Alternativo)
```bash
# Script que faz deploy + configurações automaticamente
python3 setup_complete_pipeline.py
```

### 4. Executar Flask App
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar AWS credentials (se necessário)
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret  
export AWS_DEFAULT_REGION=sa-east-1

# Executar aplicação
python app.py
```

Aplicação disponível em: http://localhost:5000

## 🧪 Testes

### Teste do Pipeline Completo
```bash
# Verificar status de arquivos processados
python3 test_pipeline.py

# Upload manual via CLI
python3 upload_pdf.py caminho/para/arquivo.pdf
```

### Verificação Manual
```bash
# Listar arquivos em cada etapa
aws s3 ls s3://source-pdf-qa-aws/ --recursive

# Ver logs CloudWatch
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/qa-on-aws
```

## 🔧 Configuração

### Variáveis de Ambiente

**Flask App (.env)**
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=sa-east-1
FLASK_ENV=development
FLASK_DEBUG=1
```

**Lambda Functions**
- `BUCKET_NAME=source-pdf-qa-aws`
- `STEP_FUNCTION_ARN` (auto-configurado pelo SAM)

### Recursos AWS Criados

| Recurso | Nome | Descrição |
|---------|------|-----------|
| **S3 Bucket** | `source-pdf-qa-aws` | Armazenamento de dados |
| **Step Function** | `qa-on-aws-dev-rag-pipeline` | Orquestração pipeline |
| **Lambda Functions** | `qa-on-aws-dev-*` | Processamento etapas |
| **IAM Roles** | Auto-criadas | Permissões mínimas necessárias |

## 📊 Monitoramento

### CloudWatch Logs
```bash
# Logs das Lambda Functions
/aws/lambda/qa-on-aws-dev-trigger-step-function
/aws/lambda/qa-on-aws-dev-extract-text
/aws/lambda/qa-on-aws-dev-generate-embeddings
/aws/lambda/qa-on-aws-dev-index-opensearch
/aws/lambda/qa-on-aws-dev-update-metadata

# Logs Step Functions
/aws/stepfunctions/qa-on-aws-dev-rag-pipeline
```

### Métricas Importantes
- **Step Function Executions**: Sucessos/falhas do pipeline
- **Lambda Duration**: Tempo de execução por etapa  
- **Lambda Errors**: Erros por função
- **S3 Object Count**: Arquivos em cada pasta

## 🔐 Segurança

- **IAM Roles**: Permissões mínimas por Lambda
- **S3 Encryption**: Server-side encryption (AES256)
- **VPC**: Não utilizando VPC (funções em rede pública AWS)
- **Secrets**: Não há secrets hardcoded no código

## 🔍 Troubleshooting

### Pipeline não executa após upload
```bash
# Verificar se S3 trigger está configurado
python3 configure_s3_trigger.py

# Verificar logs da Lambda trigger  
aws logs tail /aws/lambda/qa-on-aws-dev-trigger-step-function --follow
```

### Erro em etapa específica
```bash
# Ver execuções Step Function
aws stepfunctions list-executions --state-machine-arn <ARN>

# Ver detalhes de execução específica
aws stepfunctions describe-execution --execution-arn <EXECUTION_ARN>
```

### Flask não consegue fazer upload
```bash
# Verificar credenciais AWS
aws sts get-caller-identity

# Verificar permissões S3
aws s3 ls s3://source-pdf-qa-aws/
```

## 📈 Melhorias Futuras

- [ ] Interface de consulta RAG com chat
- [ ] Suporte a outros formatos (DOCX, TXT)
- [ ] Dashboard de monitoramento em tempo real
- [ ] Cache de embeddings para documentos similares
- [ ] API REST para integração externa
- [ ] Processamento paralelo para documentos grandes

## 📄 Licença

Este projeto é de uso educacional e demonstrativo.

---

**Desenvolvido com ❤️ usando AWS Serverless Stack**