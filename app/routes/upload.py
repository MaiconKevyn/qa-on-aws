from flask import Blueprint, request, jsonify, render_template
import logging
from app.services.s3_service import S3Service
from app.utils.validators import FileValidator

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/')
def index():
    return render_template('upload.html')

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'no_file',
                'message': 'No file provided'
            }), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'no_filename',
                'message': 'No file selected'
            }), 400

        is_valid, errors, sanitized_filename = FileValidator.validate_file(file, file.filename)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'validation_error',
                'message': '; '.join(errors)
            }), 400

        s3_service = S3Service()
        upload_result = s3_service.upload_file(file, sanitized_filename)

        if upload_result['success']:
            logger.info(f"File uploaded successfully: {upload_result['filename']}")
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'data': {
                    'filename': upload_result['filename'],
                    'original_filename': sanitized_filename,
                    's3_key': upload_result['s3_key'],
                    'bucket': upload_result['bucket']
                }
            }), 200
        else:
            logger.error(f"Upload failed: {upload_result.get('error', 'unknown')}")
            return jsonify({
                'success': False,
                'error': upload_result.get('error', 'upload_error'),
                'message': upload_result.get('message', 'Upload failed')
            }), 500

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({
            'success': False,
            'error': 'configuration_error',
            'message': 'Server configuration error'
        }), 500
    
    except Exception as e:
        logger.error(f"Unexpected error in upload endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500

@upload_bp.route('/health', methods=['GET'])
def health_check():
    try:
        s3_service = S3Service()
        bucket_exists = s3_service.check_bucket_exists()
        
        return jsonify({
            'status': 'healthy',
            's3_connection': 'ok' if bucket_exists else 'bucket_not_found',
            'timestamp': logger.handlers[0].formatter.formatTime(logger.makeRecord(
                'health', 20, '', 0, '', (), None
            )) if logger.handlers else 'no_timestamp'
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500