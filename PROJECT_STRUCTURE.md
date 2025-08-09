# 📁 Estrutura do Projeto RAG - Limpa e Otimizada

## 🏗️ **Core Infrastructure**
```
template.yaml              # SAM template principal - define toda infraestrutura AWS
state_machines/
└── processing.json         # Step Functions workflow - orquestração do pipeline RAG
```

## ⚡ **Lambda Functions**
```
lambdas/
├── requirements.txt        # Dependências: boto3, PyMuPDF
├── trigger_step_function.py   # [1] S3 Event → Start Step Function
├── extract_text.py           # [2] PDF → Extracted Text JSON
├── generate_embeddings.py    # [3] Text → Bedrock Embeddings JSON  
├── index_opensearch.py       # [4] Embeddings → OpenSearch Index JSON
└── update_metadata.py        # [5] Create Final Summary JSON
```

## 🛠️ **Setup & Configuration Scripts**
```
SETUP.md                    # Documentação completa do projeto
setup_complete_pipeline.py  # ⭐ Setup automático completo (RECOMENDADO)
configure_s3_trigger.py     # Configuração S3 trigger apenas
create_s3_folders.py        # Criação estrutura S3 data lineage
test_pipeline.py           # Testes e verificações do pipeline
cleanup_project.py         # Script de limpeza (usado uma vez)
```

## 📱 **Optional Tools**
```
main.py                    # Flask app entry point (upload via web)
requirements.txt           # Flask dependencies (Flask, boto3, etc)
upload_pdf.py             # Script upload manual via CLI
```

## 🚀 **Pipeline Data Flow**
```
📄 PDF Upload → s3://bucket/uploads/arquivo.pdf
    ↓ (S3 Event)
⚡ trigger_step_function.py → Start Step Function
    ↓
🔄 Step Function Orchestration:
    ├── extract_text.py     → s3://bucket/extracted/arquivo.json
    ├── generate_embeddings.py → s3://bucket/embeddings/arquivo.json  
    ├── index_opensearch.py → s3://bucket/indexed/arquivo.json
    └── update_metadata.py  → s3://bucket/summaries/arquivo.json
```

## 📊 **S3 Data Lineage Structure**
```
s3://source-pdf-qa-aws/
├── uploads/          # PDFs originais
├── extracted/        # Texto extraído (PyMuPDF)
├── embeddings/       # Vetores embeddings (Bedrock)
├── indexed/          # Resultados OpenSearch
└── summaries/        # Resumos finais processamento
```

## 🎯 **Arquivos Essenciais para Produção**
1. **`template.yaml`** - Infraestrutura AWS completa
2. **`lambdas/`** - Todas as 5 funções Lambda
3. **`state_machines/processing.json`** - Workflow Step Functions
4. **`setup_complete_pipeline.py`** - Setup inicial

## ⚙️ **Como Usar**
```bash
# 1. Deploy inicial
sam deploy

# 2. Configurar pipeline  
python3 setup_complete_pipeline.py

# 3. Testar
aws s3 cp arquivo.pdf s3://source-pdf-qa-aws/uploads/

# 4. Verificar resultados
aws s3 ls s3://source-pdf-qa-aws/ --recursive | grep arquivo
```

## 🧹 **Arquivos Removidos na Limpeza**
- ❌ `fix_s3_trigger.py` - Funcionalidade duplicada
- ❌ `app/`, `static/`, `templates/` - Flask app não usada no pipeline
- ❌ `venv/` - Virtual environment recriável  
- ❌ `aws/`, `awscliv2.zip` - AWS CLI (60MB+)
- ❌ Arquivos temporários: `response*.json`, `test-*.json`
- ❌ Backups Lambda: `generate_embeddings_mock.py`

**Projeto otimizado: ~80% menor, 100% funcional!** ✨