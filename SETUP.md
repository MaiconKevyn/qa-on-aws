# 🚀 Setup do Pipeline RAG - Guia Completo

## ✅ Status Atual
- [x] Deploy realizado com sucesso no GitHub Actions
- [x] Stack CloudFormation criado: `qa-on-aws-dev`
- [x] Lambdas deployadas:
  - `qa-on-aws-dev-trigger-step-function`
  - `qa-on-aws-dev-extract-text`
  - `qa-on-aws-dev-generate-embeddings`
  - `qa-on-aws-dev-index-opensearch`
  - `qa-on-aws-dev-update-metadata`
- [x] Step Function criada: `qa-on-aws-dev-rag-pipeline`

## 📋 Próximos Passos

### 1. Configurar AWS CLI Local
```bash
# Instalar AWS CLI (se não tiver)
pip install awscli

# Configurar credenciais
aws configure
# AWS Access Key ID: [Sua chave]
# AWS Secret Access Key: [Sua chave secreta]
# Default region name: sa-east-1
# Default output format: json
```

### 2. Executar Setup Completo
```bash
# Configurar estrutura S3 e triggers (recomendado)
python3 setup_complete_pipeline.py

# OU configurar apenas o trigger (se já tiver estrutura S3)
python3 configure_s3_trigger.py
```

### 3. Testar o Pipeline
```bash
# Upload de um PDF de teste
aws s3 cp arquivo.pdf s3://source-pdf-qa-aws/uploads/

# Verificar se foi processado
aws s3 ls s3://source-pdf-qa-aws/extracted/
```

## 🔄 Fluxo do Pipeline

```
1. PDF Upload → s3://source-pdf-qa-aws/uploads/arquivo.pdf
   ↓
2. S3 Event → Trigger Lambda (qa-on-aws-dev-trigger-step-function)
   ↓  
3. Step Function → Start RAG Pipeline
   ↓
4. Extract Text → s3://source-pdf-qa-aws/extracted/arquivo.json
   ↓
5. Generate Embeddings → s3://source-pdf-qa-aws/embeddings/arquivo.json
   ↓
6. Index OpenSearch → s3://source-pdf-qa-aws/indexed/arquivo.json
   ↓
7. Update Metadata → s3://source-pdf-qa-aws/summaries/arquivo.json
```

## 📁 Estrutura S3 Final

```
s3://source-pdf-qa-aws/
├── uploads/          # PDFs originais enviados
├── extracted/        # Texto extraído em JSON
├── embeddings/       # Embeddings gerados em JSON
├── indexed/          # Resultados indexação OpenSearch
└── summaries/        # Resumos finais processamento
```

## 🔍 Debug e Monitoramento

### Verificar Logs das Lambdas
```bash
# Logs da trigger lambda
aws logs tail /aws/lambda/qa-on-aws-dev-trigger-step-function --follow

# Logs da extração de texto
aws logs tail /aws/lambda/qa-on-aws-dev-extract-text --follow

# Logs Step Function
aws stepfunctions list-executions --state-machine-arn [ARN_DA_STEP_FUNCTION]
```

### Verificar Status Step Function
```bash
# Listar execuções
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:sa-east-1:498504717701:stateMachine:qa-on-aws-dev-rag-pipeline

# Detalhes de uma execução
aws stepfunctions describe-execution --execution-arn [EXECUTION_ARN]
```

## 🛠️ Troubleshooting

### Problema: S3 trigger não funciona
- Verificar permissões Lambda
- Verificar configuração S3 notification
- Verificar filtros (uploads/*.pdf)

### Problema: Lambda falha
- Verificar logs CloudWatch
- Verificar IAM permissions
- Verificar variáveis ambiente

### Problema: Step Function falha  
- Verificar definição JSON
- Verificar ARNs das Lambdas
- Verificar IAM role Step Function

## ⚡ Comandos Úteis

```bash
# Verificar stack CloudFormation
aws cloudformation describe-stacks --stack-name qa-on-aws-dev

# Listar objetos S3
aws s3 ls s3://source-pdf-qa-aws/ --recursive

# Invocar Lambda manualmente
aws lambda invoke \
  --function-name qa-on-aws-dev-extract-text \
  --payload '{"bucket":"source-pdf-qa-aws","key":"uploads/test.pdf"}' \
  response.json

# Executar Step Function manualmente
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:sa-east-1:498504717701:stateMachine:qa-on-aws-dev-rag-pipeline \
  --input '{"bucket":"source-pdf-qa-aws","key":"uploads/test.pdf"}'
```

## 🎯 Teste de Sucesso

Quando tudo estiver funcionando, você deve ver:

1. **Upload PDF**: `s3://source-pdf-qa-aws/uploads/documento.pdf`
2. **Trigger**: Execução Step Function iniciada
3. **Extract**: `s3://source-pdf-qa-aws/extracted/documento.pdf.json`
4. **Embeddings**: `s3://source-pdf-qa-aws/embeddings/documento.pdf.json`  
5. **Indexed**: `s3://source-pdf-qa-aws/indexed/documento.pdf.json`
6. **Summary**: `s3://source-pdf-qa-aws/summaries/documento.pdf.json`

✅ **Pipeline RAG funcionando perfeitamente!**