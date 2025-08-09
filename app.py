import os
import boto3
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# AWS Configuration
s3_client = boto3.client(
    's3',
    region_name='sa-east-1'
)

BUCKET_NAME = 'source-pdf-qa-aws'
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Generate unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = str(uuid.uuid4())[:8]
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                s3_key = f"uploads/{timestamp}_{unique_id}.{file_extension}"
                
                # Upload directly to S3
                s3_client.upload_fileobj(
                    file,
                    BUCKET_NAME,
                    s3_key,
                    ExtraArgs={
                        'ContentType': 'application/pdf',
                        'ServerSideEncryption': 'AES256'
                    }
                )
                
                flash(f'✅ Arquivo {file.filename} enviado com sucesso!')
                flash(f'📁 Salvo como: {s3_key}')
                
                return redirect(url_for('upload_file'))
                
            except Exception as e:
                flash(f'❌ Erro no upload: {str(e)}')
                return redirect(request.url)
        else:
            flash('❌ Apenas arquivos PDF são permitidos')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/files')
def list_files():
    try:
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix='uploads/',
            MaxKeys=20
        )
        
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    'name': obj['Key'].split('/')[-1],
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Sort by modification date (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return render_template('files.html', files=files)
        
    except Exception as e:
        flash(f'❌ Erro ao listar arquivos: {str(e)}')
        return render_template('files.html', files=[])

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'QA on AWS Flask App'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)