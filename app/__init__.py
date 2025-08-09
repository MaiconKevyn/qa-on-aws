from flask import Flask
import logging
import os
from app.config.settings import Config
from app.routes.upload import upload_bp

def create_app():
    # Define paths relativo à raiz do projeto
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    app.config['SECRET_KEY'] = Config.FLASK_SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE_MB * 1024 * 1024
    
    setup_logging(app)
    
    app.register_blueprint(upload_bp)
    
    return app

def setup_logging(app):
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )
    
    app.logger.info('QA on AWS application started')