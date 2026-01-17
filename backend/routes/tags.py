"""
Tags Routes
Tag management for prompt categorization
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Prompt, PromptTag

tags_bp = Blueprint('tags', __name__)


# ═══════════════════════════════════════════════════════════════════════════════
# LIST ALL TAGS
# ═══════════════════════════════════════════════════════════════════════════════
@tags_bp.route('', methods=['GET'])
@jwt_required()
def list_tags():
    """
    List all available tags
    
    Returns:
        tags: List of tag objects with usage counts
    """
    tags = PromptTag.query.order_by(PromptTag.name).all()
    
    return jsonify({
        'tags': [t.to_dict() for t in tags]
    }), 200


# ═══════════════════════════════════════════════════════════════════════════════
# CREATE TAG
# ═══════════════════════════════════════════════════════════════════════════════
@tags_bp.route('', methods=['POST'])
@jwt_required()
def create_tag():
    """
    Create a new tag
    
    Request Body:
        name: string
        color: string (hex color, optional)
        description: string (optional)
    
    Returns:
        tag: Created tag object
    """
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Tag name is required'}), 400
    
    name = data['name'].strip()
    
    # Check if tag exists
    if PromptTag.query.filter_by(name=name).first():
        return jsonify({'error': 'Tag already exists'}), 409
    
    tag = PromptTag(
        name=name,
        color=data.get('color', '#6366f1'),
        description=data.get('description', '').strip() or None
    )
    
    try:
        db.session.add(tag)
        db.session.commit()
        
        return jsonify({
            'message': 'Tag created successfully',
            'tag': tag.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create tag: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# UPDATE TAG
# ═══════════════════════════════════════════════════════════════════════════════
@tags_bp.route('/<int:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag(tag_id):
    """
    Update a tag
    
    Request Body:
        name: string (optional)
        color: string (optional)
        description: string (optional)
    
    Returns:
        tag: Updated tag object
    """
    tag = PromptTag.query.get(tag_id)
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        new_name = data['name'].strip()
        if new_name != tag.name:
            if PromptTag.query.filter_by(name=new_name).first():
                return jsonify({'error': 'Tag name already exists'}), 409
            tag.name = new_name
    
    if 'color' in data:
        tag.color = data['color']
    
    if 'description' in data:
        tag.description = data['description'].strip() or None
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Tag updated successfully',
            'tag': tag.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update tag: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# DELETE TAG
# ═══════════════════════════════════════════════════════════════════════════════
@tags_bp.route('/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    """
    Delete a tag
    
    Returns:
        message: Success message
    """
    tag = PromptTag.query.get(tag_id)
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404
    
    try:
        db.session.delete(tag)
        db.session.commit()
        
        return jsonify({'message': 'Tag deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete tag: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ADD TAG TO PROMPT
# ═══════════════════════════════════════════════════════════════════════════════
@tags_bp.route('/prompts/<int:prompt_id>/tags', methods=['POST'])
@jwt_required()
def add_tag_to_prompt(prompt_id):
    """
    Add a tag to a prompt
    
    Request Body:
        tag_id: int
    
    Returns:
        prompt: Updated prompt with tags
    """
    user_id = int(get_jwt_identity())
    
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=user_id).first()
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    data = request.get_json()
    tag_id = data.get('tag_id')
    
    if not tag_id:
        return jsonify({'error': 'tag_id is required'}), 400
    
    tag = PromptTag.query.get(tag_id)
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404
    
    if tag in prompt.tags:
        return jsonify({'error': 'Tag already added to this prompt'}), 409
    
    try:
        prompt.tags.append(tag)
        db.session.commit()
        
        return jsonify({
            'message': 'Tag added successfully',
            'prompt': prompt.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add tag: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# REMOVE TAG FROM PROMPT
# ═══════════════════════════════════════════════════════════════════════════════
@tags_bp.route('/prompts/<int:prompt_id>/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def remove_tag_from_prompt(prompt_id, tag_id):
    """
    Remove a tag from a prompt
    
    Returns:
        prompt: Updated prompt with tags
    """
    user_id = int(get_jwt_identity())
    
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=user_id).first()
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    tag = PromptTag.query.get(tag_id)
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404
    
    if tag not in prompt.tags:
        return jsonify({'error': 'Tag not associated with this prompt'}), 404
    
    try:
        prompt.tags.remove(tag)
        db.session.commit()
        
        return jsonify({
            'message': 'Tag removed successfully',
            'prompt': prompt.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove tag: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# GET PROMPTS BY TAG
# ═══════════════════════════════════════════════════════════════════════════════
@tags_bp.route('/<int:tag_id>/prompts', methods=['GET'])
@jwt_required()
def get_prompts_by_tag(tag_id):
    """
    Get all prompts with a specific tag
    
    Returns:
        tag: Tag object
        prompts: List of prompts with this tag
    """
    user_id = int(get_jwt_identity())
    
    tag = PromptTag.query.get(tag_id)
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404
    
    prompts = Prompt.query.filter(
        Prompt.user_id == user_id,
        Prompt.tags.contains(tag)
    ).order_by(Prompt.updated_at.desc()).all()
    
    return jsonify({
        'tag': tag.to_dict(),
        'prompts': [p.to_dict() for p in prompts]
    }), 200
