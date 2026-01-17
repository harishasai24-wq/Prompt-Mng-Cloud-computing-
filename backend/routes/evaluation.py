"""
Evaluation Routes
AI-powered prompt evaluation and recommendations
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Prompt, PromptVersion, PromptEvaluation
from ai_engine import evaluate_prompt, get_suggestions

logger = logging.getLogger(__name__)
evaluation_bp = Blueprint('evaluation', __name__)


# ═══════════════════════════════════════════════════════════════════════════════
# GET EVALUATION FOR A VERSION (READ-ONLY - NO SIDE EFFECTS)
# ═══════════════════════════════════════════════════════════════════════════════
@evaluation_bp.route('/evaluations/version/<int:version_id>', methods=['GET'])
@jwt_required()
def get_version_evaluation(version_id):
    """
    Get existing evaluation for a version (no AI execution, no DB writes)
    
    Returns:
        evaluation: Existing evaluation if found
        version: Version info
    """
    user_id = int(get_jwt_identity())
    
    version = PromptVersion.query.get(version_id)
    if not version:
        return jsonify({'error': 'Version not found'}), 404
    
    # Verify ownership
    prompt = version.prompt
    if prompt.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get existing evaluation (read-only)
    evaluation = version.get_latest_evaluation()
    
    if not evaluation:
        return jsonify({
            'evaluation': None,
            'message': 'No evaluation exists for this version',
            'version': version.to_dict(include_evaluation=False)
        }), 200
    
    return jsonify({
        'evaluation': evaluation.to_dict(),
        'version': version.to_dict(include_evaluation=False)
    }), 200


# ═══════════════════════════════════════════════════════════════════════════════
# EVALUATE A VERSION (CREATES NEW EVALUATION)
# ═══════════════════════════════════════════════════════════════════════════════
@evaluation_bp.route('/evaluate/<int:version_id>', methods=['POST'])
@jwt_required()
def evaluate_version(version_id):
    """
    Run AI evaluation on a prompt version
    
    Returns:
        evaluation: Evaluation scores and notes
        suggestions: Improvement suggestions
    """
    user_id = int(get_jwt_identity())
    
    version = PromptVersion.query.get(version_id)
    if not version:
        return jsonify({'error': 'Version not found'}), 404
    
    # Verify ownership
    prompt = version.prompt
    if prompt.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Run AI evaluation
        result = evaluate_prompt(
            prompt_text=version.prompt_text,
            task_type=prompt.task_type,
            domain=prompt.domain
        )
        
        # Get improvement suggestions
        suggestions = get_suggestions(result, version.prompt_text)
        
        # Store evaluation in database
        evaluation = PromptEvaluation(
            version_id=version.id,
            clarity_score=result['clarity_score'],
            relevance_score=result['relevance_score'],
            length_score=result['length_score'],
            final_score=result['final_score'],
            evaluation_notes=result['evaluation_notes']
        )
        
        db.session.add(evaluation)
        db.session.commit()
        
        return jsonify({
            'message': 'Evaluation completed',
            'evaluation': evaluation.to_dict(),
            'details': result['details'],
            'suggestions': suggestions,
            'version': version.to_dict(include_evaluation=False)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.exception("Evaluation failed for version %s", version_id)
        return jsonify({'error': 'Evaluation failed. Please try again.'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# EVALUATE ALL VERSIONS OF A PROMPT
# ═══════════════════════════════════════════════════════════════════════════════
@evaluation_bp.route('/evaluate/prompt/<int:prompt_id>', methods=['POST'])
@jwt_required()
def evaluate_all_versions(prompt_id):
    """
    Evaluate all versions of a prompt that haven't been evaluated
    
    Returns:
        evaluations: List of new evaluations
        total_evaluated: Count of versions evaluated
    """
    user_id = int(get_jwt_identity())
    
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=user_id).first()
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    evaluations = []
    
    try:
        for version in prompt.versions:
            # Skip if already evaluated
            if version.get_latest_evaluation():
                continue
            
            # Run evaluation
            result = evaluate_prompt(
                prompt_text=version.prompt_text,
                task_type=prompt.task_type,
                domain=prompt.domain
            )
            
            evaluation = PromptEvaluation(
                version_id=version.id,
                clarity_score=result['clarity_score'],
                relevance_score=result['relevance_score'],
                length_score=result['length_score'],
                final_score=result['final_score'],
                evaluation_notes=result['evaluation_notes']
            )
            
            db.session.add(evaluation)
            evaluations.append(evaluation)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Evaluated {len(evaluations)} versions',
            'evaluations': [e.to_dict() for e in evaluations],
            'total_evaluated': len(evaluations)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Evaluation failed: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# GET EVALUATIONS FOR A PROMPT
# ═══════════════════════════════════════════════════════════════════════════════
@evaluation_bp.route('/evaluations/<int:prompt_id>', methods=['GET'])
@jwt_required()
def get_evaluations(prompt_id):
    """
    Get all evaluations for a prompt's versions
    
    Returns:
        evaluations: List of all evaluations ordered by score
    """
    user_id = int(get_jwt_identity())
    
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=user_id).first()
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    # Get all evaluations for all versions of this prompt
    evaluations = db.session.query(PromptEvaluation).join(PromptVersion).filter(
        PromptVersion.prompt_id == prompt_id
    ).order_by(PromptEvaluation.final_score.desc()).all()
    
    return jsonify({
        'prompt_id': prompt_id,
        'prompt_title': prompt.title,
        'evaluations': [{
            **e.to_dict(),
            'version_number': e.version.version_number,
            'prompt_text_preview': e.version.prompt_text[:100] + '...' if len(e.version.prompt_text) > 100 else e.version.prompt_text
        } for e in evaluations]
    }), 200


# ═══════════════════════════════════════════════════════════════════════════════
# GET RECOMMENDATION (BEST VERSION)
# ═══════════════════════════════════════════════════════════════════════════════
@evaluation_bp.route('/recommend/<int:prompt_id>', methods=['GET'])
@jwt_required()
def get_recommendation(prompt_id):
    """
    Get the recommended (best scoring) version of a prompt
    
    Returns:
        recommendation: Best version with evaluation
        alternatives: Other versions ranked by score
    """
    user_id = int(get_jwt_identity())
    
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=user_id).first()
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    # Get best evaluation
    best = db.session.query(PromptEvaluation).join(PromptVersion).filter(
        PromptVersion.prompt_id == prompt_id
    ).order_by(PromptEvaluation.final_score.desc()).first()
    
    if not best:
        return jsonify({
            'error': 'No evaluations found. Please evaluate versions first.',
            'prompt_id': prompt_id
        }), 404
    
    # Get alternatives (other versions with evaluations)
    alternatives = db.session.query(PromptEvaluation).join(PromptVersion).filter(
        PromptVersion.prompt_id == prompt_id,
        PromptEvaluation.id != best.id
    ).order_by(PromptEvaluation.final_score.desc()).limit(5).all()
    
    return jsonify({
        'recommendation': {
            'version': best.version.to_dict(include_evaluation=False),
            'evaluation': best.to_dict(),
            'is_current': best.version.is_current
        },
        'alternatives': [{
            'version_number': e.version.version_number,
            'final_score': float(e.final_score),
            'version_id': e.version_id
        } for e in alternatives],
        'prompt': {
            'id': prompt.id,
            'title': prompt.title,
            'task_type': prompt.task_type,
            'domain': prompt.domain
        }
    }), 200


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK EVALUATE (WITHOUT SAVING)
# ═══════════════════════════════════════════════════════════════════════════════
@evaluation_bp.route('/quick-evaluate', methods=['POST'])
@jwt_required()
def quick_evaluate():
    """
    Quick evaluation without saving to database
    Useful for real-time feedback while editing
    
    Request Body:
        prompt_text: string
        task_type: string (optional)
        domain: string (optional)
    
    Returns:
        evaluation: Scores and suggestions
    """
    data = request.get_json()
    
    if not data or not data.get('prompt_text'):
        return jsonify({'error': 'prompt_text is required'}), 400
    
    result = evaluate_prompt(
        prompt_text=data['prompt_text'],
        task_type=data.get('task_type'),
        domain=data.get('domain')
    )
    
    suggestions = get_suggestions(result, data['prompt_text'])
    
    return jsonify({
        'evaluation': {
            'clarity_score': result['clarity_score'],
            'relevance_score': result['relevance_score'],
            'length_score': result['length_score'],
            'final_score': result['final_score'],
            'notes': result['evaluation_notes']
        },
        'details': result['details'],
        'suggestions': suggestions
    }), 200
