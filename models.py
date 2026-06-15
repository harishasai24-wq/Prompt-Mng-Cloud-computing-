"""
SQLAlchemy ORM Models for the AI-Assisted Prompt Management System
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ═══════════════════════════════════════════════════════════════════════════════
# ASSOCIATION TABLE: Prompt-Tag Many-to-Many
# ═══════════════════════════════════════════════════════════════════════════════
prompt_tag_map = db.Table('prompt_tag_map',
    db.Column('prompt_id', db.Integer, db.ForeignKey('prompts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('prompt_tags.id'), primary_key=True)
)


# ═══════════════════════════════════════════════════════════════════════════════
# USER MODEL
# ═══════════════════════════════════════════════════════════════════════════════
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prompts = db.relationship('Prompt', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT MODEL
# ═══════════════════════════════════════════════════════════════════════════════
class Prompt(db.Model):
    __tablename__ = 'prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.String(50), nullable=False)
    domain = db.Column(db.String(50))
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    versions = db.relationship('PromptVersion', backref='prompt', lazy='dynamic', 
                               cascade='all, delete-orphan', order_by='PromptVersion.version_number.desc()')
    tags = db.relationship('PromptTag', secondary=prompt_tag_map, backref=db.backref('prompts', lazy='dynamic'))
    
    def get_current_version(self):
        """Get the current active version"""
        return PromptVersion.query.filter_by(prompt_id=self.id, is_current=True).first()
    
    def get_latest_version(self):
        """Get the latest version by version number"""
        return PromptVersion.query.filter_by(prompt_id=self.id).order_by(
            PromptVersion.version_number.desc()
        ).first()
    
    def to_dict(self, include_versions=False, include_tags=True):
        """Convert to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type,
            'domain': self.domain,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'version_count': self.versions.count()
        }
        
        # Include current version info
        current = self.get_current_version()
        if current:
            data['current_version'] = current.to_dict()
        
        if include_versions:
            data['versions'] = [v.to_dict() for v in self.versions.all()]
        
        if include_tags:
            data['tags'] = [t.to_dict() for t in self.tags]
        
        return data


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT VERSION MODEL
# ═══════════════════════════════════════════════════════════════════════════════
class PromptVersion(db.Model):
    __tablename__ = 'prompt_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)
    change_notes = db.Column(db.Text)
    is_current = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    evaluations = db.relationship('PromptEvaluation', backref='version', lazy='dynamic',
                                  cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('prompt_id', 'version_number', name='unique_version_per_prompt'),
    )
    
    def get_latest_evaluation(self):
        """Get the most recent evaluation"""
        return PromptEvaluation.query.filter_by(version_id=self.id).order_by(
            PromptEvaluation.evaluated_at.desc()
        ).first()
    
    def to_dict(self, include_evaluation=True):
        """Convert to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'prompt_id': self.prompt_id,
            'version_number': self.version_number,
            'prompt_text': self.prompt_text,
            'change_notes': self.change_notes,
            'is_current': self.is_current,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_evaluation:
            latest_eval = self.get_latest_evaluation()
            if latest_eval:
                data['evaluation'] = latest_eval.to_dict()
        
        return data


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT EVALUATION MODEL
# ═══════════════════════════════════════════════════════════════════════════════
class PromptEvaluation(db.Model):
    __tablename__ = 'prompt_evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('prompt_versions.id'), nullable=False)
    clarity_score = db.Column(db.Numeric(5, 2), nullable=False)
    relevance_score = db.Column(db.Numeric(5, 2), nullable=False)
    length_score = db.Column(db.Numeric(5, 2), nullable=False)
    final_score = db.Column(db.Numeric(5, 2), nullable=False)
    evaluation_notes = db.Column(db.Text)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'version_id': self.version_id,
            'clarity_score': float(self.clarity_score),
            'relevance_score': float(self.relevance_score),
            'length_score': float(self.length_score),
            'final_score': float(self.final_score),
            'evaluation_notes': self.evaluation_notes,
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None
        }


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT TAG MODEL
# ═══════════════════════════════════════════════════════════════════════════════
class PromptTag(db.Model):
    __tablename__ = 'prompt_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#6366f1')
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'prompt_count': len(self.prompts.all()) if hasattr(self, 'prompts') else 0
        }


# ═══════════════════════════════════════════════════════════════════════════════
# LLM MODEL (Future Enhancement)
# ═══════════════════════════════════════════════════════════════════════════════
class LLMModel(db.Model):
    __tablename__ = 'llm_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(50))
    model_id = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'provider': self.provider,
            'model_id': self.model_id,
            'is_active': self.is_active
        }
