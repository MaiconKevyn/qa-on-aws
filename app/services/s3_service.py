import boto3
import logging
import uuid
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
from app.config.settings import Config

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        try:
            Config.validate_aws_config()
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                region_name=Config.AWS_REGION
            )
            self.bucket_name = Config.S3_BUCKET_NAME
            self.folder_prefix = Config.S3_FOLDER_PREFIX
        except ValueError as e:
            logger.error(f"AWS configuration error: {e}")
            raise
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
    
    def upload_file(self, file_obj, original_filename):
        try:
            unique_filename = self._generate_unique_filename(original_filename)
            s3_key = f"{self.folder_prefix}{unique_filename}"
            
            file_obj.seek(0)
            
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': 'application/pdf',
                    'Metadata': {
                        'original_filename': original_filename,
                        'upload_timestamp': datetime.utcnow().isoformat()
                    }
                }
            )
            
            logger.info(f"File uploaded successfully: {s3_key}")
            
            return {
                'success': True,
                'filename': unique_filename,
                's3_key': s3_key,
                'bucket': self.bucket_name,
                'url': f"https://{self.bucket_name}.s3.{Config.AWS_REGION}.amazonaws.com/{s3_key}"
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"AWS S3 error ({error_code}): {e}")
            return {
                'success': False,
                'error': f"Upload failed: {error_code}",
                'message': 'Failed to upload file to storage'
            }
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return {
                'success': False,
                'error': 'upload_error',
                'message': 'An unexpected error occurred during upload'
            }
    
    def _generate_unique_filename(self, original_filename):
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        file_extension = original_filename.split('.')[-1] if '.' in original_filename else 'pdf'
        
        return f"{timestamp}_{unique_id}.{file_extension}"
    
    def check_bucket_exists(self):
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            return False