"""
Versions Routes
Version control operations for prompts
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Prompt, PromptVersion

logger = logging.getLogger(__name__)
versions_bp = Blueprint('versions', __name__)


# ═══════════════════════════════════════════════════════════════════════════════
# LIST VERSIONS FOR A PROMPT
# ═══════════════════════════════════════════════════════════════════════════════
@versions_bp.route('/prompts/<int:prompt_id>/versions', methods=['GET'])
@jwt_required()
def list_versions(prompt_id):
    """
    List all versions for a prompt
    
    Returns:
        versions: List of version objects
    """
    user_id = int(get_jwt_identity())
    
    # Verify prompt ownership
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=user_id).first()
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    versions = PromptVersion.query.filter_by(prompt_id=prompt_id).order_by(
        PromptVersion.version_number.desc()
    ).all()
    
    return jsonify({
        'prompt_id': prompt_id,
        'prompt_title': prompt.title,
        'versions': [v.to_dict() for v in versions],
        'total': len(versions)
    }), 200


# ═══════════════════════════════════════════════════════════════════════════════
# GET SINGLE VERSION
# ═══════════════════════════════════════════════════════════════════════════════
@versions_bp.route('/versions/<int:version_id>', methods=['GET'])
@jwt_required()
def get_version(version_id):
    """
    Get a single version with full details
    
    Returns:
        version: Version object with evaluation
    """
    user_id = int(get_jwt_identity())
    
    version = PromptVersion.query.get(version_id)
    if not version:
        return jsonify({'error': 'Version not found'}), 404
    
    # Verify ownership
    if version.prompt.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'version': version.to_dict(include_evaluation=True),
        'prompt': version.prompt.to_dict(include_versions=False)
    }), 200


# ═══════════════════════════════════════════════════════════════════════════════
# SET CURRENT VERSION (WITH CONCURRENCY PROTECTION)
# ═══════════════════════════════════════════════════════════════════════════════
@versions_bp.route('/versions/<int:version_id>/set-current', methods=['POST'])
@jwt_required()
def set_current_version(version_id):
    """
    Set a specific version as the current version
    Uses SELECT FOR UPDATE to prevent race conditions
    
    Returns:
        version: Updated version object
        message: Success message
    """
    user_id = int(get_jwt_identity())
    
    try:
        # Lock the version row to prevent concurrent modifications
        version = db.session.query(PromptVersion).with_for_update().get(version_id)
        if not version:
            return jsonify({'error': 'Version not found'}), 404
        
        # Verify ownership
        prompt = version.prompt
        if prompt.user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Unset all other versions for this prompt (within the lock)
        PromptVersion.query.filter_by(prompt_id=prompt.id).update({'is_current': False})
        
        # Set this version as current
        version.is_current = True
        
        db.session.commit()
        
        return jsonify({
            'message': f'Version {version.version_number} is now the current version',
            'version': version.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.exception("Failed to set current version %s", version_id)
        return jsonify({'error': 'Failed to update version. Please try again.'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# COMPARE VERSIONS
# ═══════════════════════════════════════════════════════════════════════════════
@versions_bp.route('/versions/compare', methods=['GET'])
@jwt_required()
def compare_versions():
    """
    Compare two versions side by side
    
    Query Parameters:
        version1: First version ID
        version2: Second version ID
    
    Returns:
        comparison: Object with both versions and diff info
    """
    user_id = int(get_jwt_identity())
    
    version1_id = request.args.get('version1', type=int)
    version2_id = request.args.get('version2', type=int)
    
    if not version1_id or not version2_id:
        return jsonify({'error': 'Both version1 and version2 are required'}), 400
    
    version1 = PromptVersion.query.get(version1_id)
    version2 = PromptVersion.query.get(version2_id)
    
    if not version1 or not version2:
        return jsonify({'error': 'One or both versions not found'}), 404
    
    # Verify ownership
    if version1.prompt.user_id != user_id or version2.prompt.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if same prompt
    if version1.prompt_id != version2.prompt_id:
        return jsonify({'error': 'Versions must be from the same prompt'}), 400
    
    # Simple diff calculation
    text1_words = set(version1.prompt_text.split())
    text2_words = set(version2.prompt_text.split())
    
    added = text2_words - text1_words
    removed = text1_words - text2_words
    unchanged = text1_words & text2_words
    
    return jsonify({
        'comparison': {
            'version1': version1.to_dict(),
            'version2': version2.to_dict(),
            'diff': {
                'words_added': len(added),
                'words_removed': len(removed),
                'words_unchanged': len(unchanged),
                'length_change': len(version2.prompt_text) - len(version1.prompt_text)
            }
        }
    }), 200


# ═══════════════════════════════════════════════════════════════════════════════
# DELETE VERSION (WITH CONCURRENCY PROTECTION)
# ═══════════════════════════════════════════════════════════════════════════════
@versions_bp.route('/versions/<int:version_id>', methods=['DELETE'])
@jwt_required()
def delete_version(version_id):
    """
    Delete a specific version (cannot delete if only one version exists)
    Uses SELECT FOR UPDATE to prevent race conditions on count check
    
    Returns:
        message: Success message
    """
    user_id = int(get_jwt_identity())
    
    try:
        # Lock the version row to prevent concurrent modifications
        version = db.session.query(PromptVersion).with_for_update().get(version_id)
        if not version:
            return jsonify({'error': 'Version not found'}), 404
        
        # Verify ownership
        prompt = version.prompt
        if prompt.user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if this is the only version (count within transaction)
        version_count = db.session.query(PromptVersion).filter_by(
            prompt_id=prompt.id
        ).with_for_update().count()
        
        if version_count <= 1:
            return jsonify({'error': 'Cannot delete the only version. Delete the prompt instead.'}), 400
        
        # If deleting current version, set another as current
        was_current = version.is_current
        version_number = version.version_number
        
        db.session.delete(version)
        
        if was_current:
            # Set the latest remaining version as current
            new_current = db.session.query(PromptVersion).filter_by(
                prompt_id=prompt.id
            ).filter(
                PromptVersion.id != version_id
            ).order_by(
                PromptVersion.version_number.desc()
            ).first()
            if new_current:
                new_current.is_current = True
        
        db.session.commit()
        
        return jsonify({
            'message': f'Version {version_number} deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.exception("Failed to delete version %s", version_id)
        return jsonify({'error': 'Failed to delete version. Please try again.'}), 500
