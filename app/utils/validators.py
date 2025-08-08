import os
import logging
from werkzeug.utils import secure_filename
from app.config.settings import Config

logger = logging.getLogger(__name__)

class FileValidator:
    @staticmethod
    def is_allowed_file(filename):
        if not filename:
            return False, "No filename provided"
        
        if '.' not in filename:
            return False, "File must have an extension"
        
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        if file_extension not in [ext.strip().lower() for ext in Config.ALLOWED_EXTENSIONS]:
            return False, f"File type not allowed. Allowed types: {', '.join(Config.ALLOWED_EXTENSIONS)}"
        
        return True, "File type is valid"
    
    @staticmethod
    def validate_file_size(file_obj):
        if not file_obj:
            return False, "No file provided"
        
        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        file_obj.seek(0)
        
        max_size_bytes = Config.MAX_FILE_SIZE_MB * 1024 * 1024
        
        if file_size > max_size_bytes:
            return False, f"File too large. Maximum size allowed: {Config.MAX_FILE_SIZE_MB}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        logger.info(f"File size validation passed: {file_size / (1024*1024):.2f}MB")
        return True, "File size is valid"
    
    @staticmethod
    def sanitize_filename(filename):
        if not filename:
            return None
        
        filename = secure_filename(filename)
        
        if not filename:
            return "unnamed_file.pdf"
        
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:251] + ext
        
        return filename
    
    @staticmethod
    def validate_file(file_obj, filename):
        errors = []
        
        sanitized_filename = FileValidator.sanitize_filename(filename)
        if not sanitized_filename:
            errors.append("Invalid filename")
            return False, errors, None
        
        is_valid_type, type_message = FileValidator.is_allowed_file(sanitized_filename)
        if not is_valid_type:
            errors.append(type_message)
        
        is_valid_size, size_message = FileValidator.validate_file_size(file_obj)
        if not is_valid_size:
            errors.append(size_message)
        
        if errors:
            return False, errors, sanitized_filename
        
        logger.info(f"File validation successful: {sanitized_filename}")
        return True, [], sanitized_filename