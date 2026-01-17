"""
AI-Assisted Prompt Management System
Main Flask Application
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import config
from models import db

import inspect
if not hasattr(inspect, 'formatargspec'):
    def formatargspec(args, varargs=None, varkwargs=None, defaults=None,
                      kwonlyargs=(), kwonlydefaults={}, annotations={},
                      formatvalue=lambda value: '=' + repr(value)):
        spec = inspect.signature(args)
        return str(spec)
    inspect.formatargspec = formatargspec

# Initialize JWT
jwt = JWTManager()


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Serve frontend from ../frontend folder
    frontend_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
    
    app = Flask(__name__, 
                static_folder=frontend_folder,
                static_url_path='')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'), 
         supports_credentials=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.prompts import prompts_bp
    from routes.versions import versions_bp
    from routes.evaluation import evaluation_bp
    from routes.tags import tags_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(prompts_bp, url_prefix='/api/prompts')
    app.register_blueprint(versions_bp, url_prefix='/api')
    app.register_blueprint(evaluation_bp, url_prefix='/api')
    app.register_blueprint(tags_bp, url_prefix='/api/tags')
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ERROR HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # ═══════════════════════════════════════════════════════════════════════════
    # JWT CALLBACKS
    # ═══════════════════════════════════════════════════════════════════════════
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has expired',
            'code': 'token_expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'code': 'invalid_token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization token is missing',
            'code': 'missing_token'
        }), 401
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HEALTH CHECK & ROOT ROUTES
    # ═══════════════════════════════════════════════════════════════════════════
    
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    @app.route('/api')
    def api_info():
        return jsonify({
            'name': 'AI-Assisted Prompt Management System',
            'version': '1.0.0',
            'status': 'running',
            'project': 'RiseOfTheJaguar'
        })
    
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'database': 'connected' if check_db_connection(app) else 'disconnected'
        })
    
    return app


def check_db_connection(app):
    """Check if database is connected"""
    try:
        with app.app_context():
            db.session.execute(db.text('SELECT 1'))
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# CLI COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

def init_db():
    """Initialize the database"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")


def seed_demo_data():
    """Seed demo data for testing"""
    from models import User, Prompt, PromptVersion, PromptTag
    
    app = create_app()
    with app.app_context():
        # Create demo user
        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            demo_user = User(
                username='demo',
                email='demo@example.com',
                full_name='Demo User',
                role='admin'
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.flush()
        
        # Create sample prompts
        sample_prompts = [
            {
                'title': 'Code Review Helper',
                'description': 'A prompt for reviewing code quality',
                'task_type': 'analysis',
                'domain': 'coding',
                'prompt_text': 'Analyze the following code for potential bugs, security issues, and performance improvements. Provide specific suggestions with code examples.'
            },
            {
                'title': 'Patient Summary Generator',
                'description': 'Generates patient visit summaries',
                'task_type': 'generation',
                'domain': 'healthcare',
                'prompt_text': 'Create a concise patient visit summary based on the provided notes. Include diagnosis, treatment plan, and follow-up recommendations in a structured format.'
            },
            {
                'title': 'Lesson Plan Creator',
                'description': 'Creates educational lesson plans',
                'task_type': 'generation',
                'domain': 'education',
                'prompt_text': 'Design a comprehensive lesson plan for teaching the specified topic. Include learning objectives, activities, assessment methods, and estimated time for each section.'
            }
        ]
        
        for i, prompt_data in enumerate(sample_prompts):
            existing = Prompt.query.filter_by(title=prompt_data['title'], user_id=demo_user.id).first()
            if not existing:
                prompt = Prompt(
                    user_id=demo_user.id,
                    title=prompt_data['title'],
                    description=prompt_data['description'],
                    task_type=prompt_data['task_type'],
                    domain=prompt_data['domain']
                )
                db.session.add(prompt)
                db.session.flush()
                
                # Create version
                version = PromptVersion(
                    prompt_id=prompt.id,
                    version_number=1,
                    prompt_text=prompt_data['prompt_text'],
                    change_notes='Initial version',
                    is_current=True
                )
                db.session.add(version)
        
        db.session.commit()
        print("Demo data seeded successfully!")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init-db':
            init_db()
        elif sys.argv[1] == 'seed':
            seed_demo_data()
        else:
            print(f"Unknown command: {sys.argv[1]}")
    else:
        app = create_app()
        app.run(host='0.0.0.0', port=5001, debug=True)
