"""
Prompts Routes
CRUD operations for prompts
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Prompt, PromptVersion, PromptTag, PromptEvaluation

prompts_bp = Blueprint('prompts', __name__)


# ═══════════════════════════════════════════════════════════════════════════════
# LIST PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════
@prompts_bp.route('', methods=['GET'])
@jwt_required()
def list_prompts():
    """
    List all prompts for the current user
    
    Query Parameters:
        task_type: Filter by task type
        domain: Filter by domain
        search: Search in title/description
        page: Page number (default: 1)
        per_page: Items per page (default: 10)
    
    Returns:
        prompts: List of prompt objects
        pagination: Pagination info
    """
    user_id = int(get_jwt_identity())
    
    # Build query
    query = Prompt.query.filter_by(user_id=user_id)
    
    # Apply filters
    task_type = request.args.get('task_type')
    if task_type:
        query = query.filter_by(task_type=task_type)
    
    domain = request.args.get('domain')
    if domain:
        query = query.filter_by(domain=domain)
    
    search = request.args.get('search')
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (Prompt.title.ilike(search_term)) | 
            (Prompt.description.ilike(search_term))
        )
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 50)  # Max 50 per page
    
    # Order by most recent
    query = query.order_by(Prompt.updated_at.desc())
    
    # Execute with pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'prompts': [p.to_dict() for p in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


# ═══════════════════════════════════════════════════════════════════════════════
# CREATE PROMPT
# ═══════════════════════════════════════════════════════════════════════════════
@prompts_bp.route('', methods=['POST'])
@jwt_required()
def create_prompt():
    """
    Create a new prompt with initial version
    
    Request Body:
        title: string
        description: string (optional)
        task_type: string
        domain: string (optional)
        prompt_text: string (initial version text)
        is_public: boolean (optional)
        tags: list of tag IDs (optional)
    
    Returns:
        prompt: Created prompt object with version
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validation
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    task_type = data.get('task_type', '').strip()
    if not task_type:
        return jsonify({'error': 'Task type is required'}), 400
    
    prompt_text = data.get('prompt_text', '').strip()
    if not prompt_text:
        return jsonify({'error': 'Prompt text is required'}), 400
    
    # Create prompt
    prompt = Prompt(
        user_id=user_id,
        title=title,
        description=data.get('description', '').strip(),
        task_type=task_type,
        domain=data.get('domain', '').strip() or None,
        is_public=data.get('is_public', False)
    )
    
    try:
        db.session.add(prompt)
        db.session.flush()  # Get prompt ID
        
        # Create initial version
        version = PromptVersion(
            prompt_id=prompt.id,
            version_number=1,
            prompt_text=prompt_text,
            change_notes='Initial version',
            is_current=True
        )
        db.session.add(version)
        
        # Add tags if provided
        tag_ids = data.get('tags', [])
        if tag_ids:
            tags = PromptTag.query.filter(PromptTag.id.in_(tag_ids)).all()
            prompt.tags = tags
        
        db.session.commit()
        
        return jsonify({
            'message': 'Prompt created successfully',
            'prompt': prompt.to_dict(include_versions=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create prompt: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# GET SINGLE PROMPT
# ═══════════════════════════════════════════════════════════════════════════════
@prompts_bp.route('/<int:prompt_id>', methods=['GET'])
@jwt_required()
def get_prompt(prompt_id):
    """
    Get a single prompt with all versions
    
    Returns:
        prompt: Prompt object with versions
    """
    user_id = int(get_jwt_identity())
    
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=user_id).first()
    
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    return jsonify({
        'prompt': prompt.to_dict(include_versions=True)
    }), 200


# ═══════════════════════════════════════════════════════════════════════════════
# UPDATE PROMPT (Creates new version)
# ═══════════════════════════════════════════════════════════════════════════════
@prompts_bp.route('/<int:prompt_id>', methods=['PUT'])
@jwt_required()
def update_prompt(prompt_id):
    """
    Update a prompt - creates a new version if prompt_text changes
    
    Request Body:
        title: string (optional)
        description: string (optional)
        task_type: string (optional)
        domain: string (optional)
        prompt_text: string (optional - creates new version)
        change_notes: string (optional)
        is_public: boolean (optional)
        tags: list of tag IDs (optional)
    
    Returns:
        prompt: Updated prompt object
    """
    user_id = int(get_jwt_identity())
    
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=user_id).first()
    
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    data = request.get_json()
    
    # Update metadata
    if 'title' in data:
        prompt.title = data['title'].strip()
    
    if 'description' in data:
        prompt.description = data['description'].strip()
    
    if 'task_type' in data:
        prompt.task_type = data['task_type'].strip()
    
    if 'domain' in data:
        prompt.domain = data['domain'].strip() or None
    
    if 'is_public' in data:
        prompt.is_public = data['is_public']
    
    # Update tags
    if 'tags' in data:
        tag_ids = data['tags']
        tags = PromptTag.query.filter(PromptTag.id.in_(tag_ids)).all()
        prompt.tags = tags
    
    # Create new version if prompt_text changed
    new_version = None
    if 'prompt_text' in data and data['prompt_text'].strip():
        current = prompt.get_current_version()
        
        # Check if text actually changed
        if not current or current.prompt_text != data['prompt_text'].strip():
            # Mark old version as not current
            if current:
                current.is_current = False
            
            # Get next version number
            latest = prompt.get_latest_version()
            next_version = (latest.version_number + 1) if latest else 1
            
            # Create new version
            new_version = PromptVersion(
                prompt_id=prompt.id,
                version_number=next_version,
                prompt_text=data['prompt_text'].strip(),
                change_notes=data.get('change_notes', f'Version {next_version}'),
                is_current=True
            )
            db.session.add(new_version)
    
    try:
        db.session.commit()
        
        response_data = {
            'message': 'Prompt updated successfully',
            'prompt': prompt.to_dict(include_versions=True)
        }
        
        if new_version:
            response_data['new_version'] = new_version.to_dict()
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update prompt: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# DELETE PROMPT
# ═══════════════════════════════════════════════════════════════════════════════
@prompts_bp.route('/<int:prompt_id>', methods=['DELETE'])
@jwt_required()
def delete_prompt(prompt_id):
    """
    Delete a prompt and all its versions
    
    Returns:
        message: Success message
    """
    user_id = int(get_jwt_identity())
    
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=user_id).first()
    
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    try:
        db.session.delete(prompt)
        db.session.commit()
        
        return jsonify({'message': 'Prompt deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete prompt: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# GET STATS
# ═══════════════════════════════════════════════════════════════════════════════
@prompts_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """
    Get statistics for the current user's prompts
    
    Returns:
        stats: Object with counts and breakdowns
    """
    user_id = int(get_jwt_identity())
    
    # Total prompts
    total_prompts = Prompt.query.filter_by(user_id=user_id).count()
    
    # Total versions
    total_versions = db.session.query(PromptVersion).join(Prompt).filter(
        Prompt.user_id == user_id
    ).count()
    
    # By task type
    task_type_stats = db.session.query(
        Prompt.task_type, db.func.count(Prompt.id)
    ).filter_by(user_id=user_id).group_by(Prompt.task_type).all()
    
    # By domain
    domain_stats = db.session.query(
        Prompt.domain, db.func.count(Prompt.id)
    ).filter_by(user_id=user_id).filter(
        Prompt.domain.isnot(None)
    ).group_by(Prompt.domain).all()
    
    # Recent prompts
    recent = Prompt.query.filter_by(user_id=user_id).order_by(
        Prompt.updated_at.desc()
    ).limit(5).all()
    
    # Average Score
    avg_score = db.session.query(db.func.avg(PromptEvaluation.final_score)).join(
        PromptVersion
    ).join(
        Prompt
    ).filter(
        Prompt.user_id == user_id
    ).scalar()
    
    # Active Tags (unique tags used in user's prompts)
    active_tags_count = db.session.query(db.func.count(db.distinct(PromptTag.id))).join(
        PromptTag.prompts
    ).filter(
        Prompt.user_id == user_id
    ).scalar()
    
    return jsonify({
        'stats': {
            'total_prompts': total_prompts,
            'total_versions': total_versions,
            'avg_score': round(float(avg_score), 1) if avg_score else 0,
            'active_tags': active_tags_count,
            'by_task_type': dict(task_type_stats),
            'by_domain': dict(domain_stats),
            'recent_prompts': [p.to_dict() for p in recent]
        }
    }), 200
