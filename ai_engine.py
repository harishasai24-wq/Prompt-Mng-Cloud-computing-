"""
Rule-Based AI Engine for Prompt Evaluation
This module contains the core AI logic for evaluating prompts
"""
import re
from typing import Dict, List, Tuple
import textstat
from textblob import TextBlob


class PromptEvaluator:
    """
    Rule-Based AI Engine that evaluates prompts based on:
    - Clarity: How clear and specific the prompt is
    - Relevance: How well it matches the task type and domain
    - Length: Whether the prompt is optimally sized
    """
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Words that indicate vague or unclear prompts
    VAGUE_KEYWORDS = [
        'something', 'stuff', 'thing', 'things', 'maybe', 'etc', 'whatever',
        'somehow', 'somewhere', 'anything', 'everything', 'nothing',
        'kind of', 'sort of', 'like', 'basically', 'actually'
    ]
    
    # Strong action words that indicate clear intent
    CLEAR_ACTION_WORDS = [
        'create', 'generate', 'write', 'analyze', 'summarize', 'explain',
        'list', 'describe', 'compare', 'evaluate', 'implement', 'design',
        'calculate', 'find', 'search', 'extract', 'convert', 'translate',
        'review', 'optimize', 'debug', 'test', 'validate', 'format'
    ]
    
    # Domain-specific keywords
    DOMAIN_KEYWORDS = {
        'healthcare': [
            'patient', 'diagnosis', 'treatment', 'medical', 'health',
            'symptom', 'disease', 'medication', 'clinical', 'doctor',
            'hospital', 'therapy', 'prescription', 'nursing', 'surgery'
        ],
        'coding': [
            'function', 'code', 'debug', 'implement', 'api', 'class',
            'method', 'variable', 'algorithm', 'database', 'server',
            'frontend', 'backend', 'python', 'javascript', 'sql'
        ],
        'education': [
            'teach', 'explain', 'learn', 'student', 'lesson', 'course',
            'curriculum', 'assignment', 'grade', 'exam', 'tutorial',
            'concept', 'theory', 'practice', 'exercise', 'quiz'
        ],
        'business': [
            'revenue', 'profit', 'customer', 'market', 'strategy',
            'sales', 'product', 'service', 'growth', 'investment',
            'roi', 'kpi', 'analytics', 'report', 'presentation'
        ],
        'creative': [
            'story', 'poem', 'character', 'plot', 'narrative',
            'fiction', 'dialogue', 'scene', 'imagination', 'creative',
            'artistic', 'style', 'voice', 'theme', 'metaphor'
        ],
        'legal': [
            'contract', 'agreement', 'clause', 'terms', 'legal',
            'compliance', 'regulation', 'law', 'court', 'litigation',
            'policy', 'liability', 'rights', 'obligation', 'statute'
        ]
    }
    
    # Task type indicators
    TASK_INDICATORS = {
        'generation': [
            'create', 'generate', 'write', 'produce', 'make', 'build',
            'compose', 'draft', 'construct', 'develop', 'design'
        ],
        'analysis': [
            'analyze', 'evaluate', 'assess', 'review', 'examine',
            'investigate', 'study', 'inspect', 'critique', 'audit'
        ],
        'summarization': [
            'summarize', 'condense', 'shorten', 'brief', 'synopsis',
            'overview', 'abstract', 'digest', 'recap', 'outline'
        ],
        'translation': [
            'translate', 'convert', 'transform', 'adapt', 'localize',
            'interpret', 'render', 'transpose'
        ],
        'classification': [
            'classify', 'categorize', 'sort', 'organize', 'group',
            'label', 'tag', 'identify', 'distinguish'
        ],
        'extraction': [
            'extract', 'find', 'locate', 'identify', 'retrieve',
            'pull', 'get', 'fetch', 'obtain', 'gather'
        ]
    }
    
    # Scoring weights
    DEFAULT_WEIGHTS = {
        'clarity': 0.4,
        'relevance': 0.4,
        'length': 0.2
    }
    
    # Length thresholds
    MIN_WORDS = 5
    OPTIMAL_MIN_WORDS = 15
    OPTIMAL_MAX_WORDS = 150
    MAX_WORDS = 300
    
    def __init__(self, weights: Dict[str, float] = None):
        """Initialize evaluator with optional custom weights"""
        self.weights = weights or self.DEFAULT_WEIGHTS
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN EVALUATION METHOD
    # ═══════════════════════════════════════════════════════════════════════════
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN EVALUATION METHOD
    # ═══════════════════════════════════════════════════════════════════════════
    
    def evaluate(self, prompt_text: str, task_type: str = None, 
                 domain: str = None) -> Dict:
        """
        Main evaluation method that returns all scores
        
        Args:
            prompt_text: The prompt text to evaluate
            task_type: Type of task (generation, analysis, etc.)
            domain: Domain context (healthcare, coding, etc.)
            
        Returns:
            Dictionary with all scores and evaluation notes
        """
        # Calculate individual scores
        clarity_result = self._calculate_clarity_score(prompt_text)
        relevance_result = self._calculate_relevance_score(prompt_text, task_type, domain)
        length_result = self._calculate_length_score(prompt_text)
        
        # New Advanced Metrics
        readability_result = self._calculate_readability(prompt_text)
        sentiment_result = self._analyze_sentiment(prompt_text)
        
        # Calculate weighted final score
        # Note: We keep the weights for the main 3 components for now, 
        # but could integrate readability/sentiment into the weight mix later.
        final_score = (
            clarity_result['score'] * self.weights['clarity'] +
            relevance_result['score'] * self.weights['relevance'] +
            length_result['score'] * self.weights['length']
        )
        
        # Compile evaluation notes
        all_notes = []
        all_notes.extend(clarity_result['notes'])
        all_notes.extend(relevance_result['notes'])
        all_notes.extend(length_result['notes'])
        all_notes.extend(readability_result['notes'])
        all_notes.extend(sentiment_result['notes'])
        
        return {
            'clarity_score': round(clarity_result['score'], 2),
            'relevance_score': round(relevance_result['score'], 2),
            'length_score': round(length_result['score'], 2),
            'final_score': round(final_score, 2),
            'evaluation_notes': ' | '.join(all_notes) if all_notes else 'No issues found.',
            'details': {
                'clarity': clarity_result,
                'relevance': relevance_result,
                'length': length_result,
                'readability': readability_result,
                'sentiment': sentiment_result
            }
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ADVANCED ANALYTICS (TEXTSTAT & TEXTBLOB)
    # ═══════════════════════════════════════════════════════════════════════════

    def _calculate_readability(self, prompt_text: str) -> Dict:
        """
        Calculate readability scores using textstat.
        Flesch Reading Ease: 0-100 (Higher is easier).
        """
        try:
            flesch_score = textstat.flesch_reading_ease(prompt_text)
            grade_level = textstat.text_standard(prompt_text, float_output=False)
        except Exception:
            flesch_score = 50.0
            grade_level = "N/A"
        
        notes = []
        if flesch_score < 30:
            notes.append("Very difficult to read")
        elif flesch_score > 90:
            notes.append("Very simple language")
            
        return {
            'flesch_reading_ease': flesch_score,
            'grade_level': grade_level,
            'notes': notes
        }

    def _analyze_sentiment(self, prompt_text: str) -> Dict:
        """
        Analyze sentiment and subjectivity using TextBlob.
        Subjectivity: 0.0 (Objective) - 1.0 (Subjective).
        """
        blob = TextBlob(prompt_text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        notes = []
        if subjectivity > 0.7:
            notes.append("Highly subjective language detected")
        
        return {
            'polarity': round(polarity, 2),
            'subjectivity': round(subjectivity, 2),
            'notes': notes
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # CLARITY SCORING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _calculate_clarity_score(self, prompt_text: str) -> Dict:
        """
        Calculate clarity score based on:
        - Absence of vague keywords
        - Presence of clear action words
        - Proper sentence structure
        - Specificity indicators
        """
        score = 100.0
        notes = []
        prompt_lower = prompt_text.lower()
        
        # Rule 1: Penalize vague keywords
        vague_found = []
        for keyword in self.VAGUE_KEYWORDS:
            if keyword in prompt_lower:
                vague_found.append(keyword)
                score -= 8
        
        if vague_found:
            notes.append(f"Vague terms found: {', '.join(vague_found[:3])}")
        
        # Rule 2: Reward clear action words
        action_found = []
        for word in self.CLEAR_ACTION_WORDS:
            if word in prompt_lower:
                action_found.append(word)
                score += 5
        
        if not action_found:
            score -= 15
            notes.append("Missing clear action verbs")
        
        # Rule 3: Check for question marks (indicates specific query)
        if '?' in prompt_text:
            score += 5
        
        # Rule 4: Check for numbered lists or bullet points
        if re.search(r'(\d+\.|•|-)\s', prompt_text):
            score += 10
            notes.append("Well-structured with lists")
        
        # Rule 5: Check for specific details (numbers, names, etc.)
        if re.search(r'\d+', prompt_text):
            score += 5
        
        # Rule 6: Penalize all caps (shouting)
        caps_ratio = sum(1 for c in prompt_text if c.isupper()) / max(len(prompt_text), 1)
        if caps_ratio > 0.5:
            score -= 10
            notes.append("Too many capital letters")
        
        # Clamp score
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'notes': notes,
            'action_words_found': action_found,
            'vague_words_found': vague_found
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RELEVANCE SCORING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _calculate_relevance_score(self, prompt_text: str, 
                                   task_type: str = None,
                                   domain: str = None) -> Dict:
        """
        Calculate relevance score based on:
        - Match with specified task type
        - Match with specified domain
        - Keyword density for task/domain
        """
        score = 50.0  # Base score
        notes = []
        prompt_lower = prompt_text.lower()
        
        domain_matches = []
        task_matches = []
        
        # Rule 1: Check domain keyword matches
        if domain and domain.lower() in self.DOMAIN_KEYWORDS:
            domain_keywords = self.DOMAIN_KEYWORDS[domain.lower()]
            for keyword in domain_keywords:
                if keyword in prompt_lower:
                    domain_matches.append(keyword)
                    score += 5
            
            if not domain_matches:
                score -= 10
                notes.append(f"Low relevance to {domain} domain")
            else:
                notes.append(f"Matches {domain}: {', '.join(domain_matches[:3])}")
        
        # Rule 2: Check task type alignment
        if task_type and task_type.lower() in self.TASK_INDICATORS:
            task_keywords = self.TASK_INDICATORS[task_type.lower()]
            for keyword in task_keywords:
                if keyword in prompt_lower:
                    task_matches.append(keyword)
                    score += 8
            
            if not task_matches:
                score -= 15
                notes.append(f"Doesn't align with {task_type} task")
            else:
                notes.append(f"Good {task_type} indicators")
        
        # Rule 3: Check for context specificity
        context_words = ['for', 'about', 'regarding', 'concerning', 'related to']
        has_context = any(word in prompt_lower for word in context_words)
        if has_context:
            score += 10
        
        # Rule 4: Check for output format specification
        format_words = ['json', 'list', 'table', 'bullet', 'paragraph', 'code', 'markdown']
        has_format = any(word in prompt_lower for word in format_words)
        if has_format:
            score += 10
            notes.append("Specifies output format")
        
        # Clamp score
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'notes': notes,
            'domain_matches': domain_matches,
            'task_matches': task_matches
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LENGTH SCORING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _calculate_length_score(self, prompt_text: str) -> Dict:
        """
        Calculate length score based on optimal word count range
        """
        word_count = len(prompt_text.split())
        notes = []
        
        if word_count < self.MIN_WORDS:
            # Too short
            score = (word_count / self.MIN_WORDS) * 30
            notes.append(f"Too short ({word_count} words)")
        
        elif word_count < self.OPTIMAL_MIN_WORDS:
            # Below optimal but acceptable
            score = 50 + ((word_count - self.MIN_WORDS) / 
                         (self.OPTIMAL_MIN_WORDS - self.MIN_WORDS)) * 30
            notes.append(f"Could be more detailed ({word_count} words)")
        
        elif word_count <= self.OPTIMAL_MAX_WORDS:
            # Optimal range
            score = 100
            notes.append(f"Optimal length ({word_count} words)")
        
        elif word_count <= self.MAX_WORDS:
            # Above optimal but acceptable
            excess = word_count - self.OPTIMAL_MAX_WORDS
            max_excess = self.MAX_WORDS - self.OPTIMAL_MAX_WORDS
            score = 100 - (excess / max_excess) * 30
            notes.append(f"Slightly long ({word_count} words)")
        
        else:
            # Too long
            score = max(0, 70 - ((word_count - self.MAX_WORDS) / 50) * 10)
            notes.append(f"Too long ({word_count} words)")
        
        return {
            'score': max(0, min(100, score)),
            'notes': notes,
            'word_count': word_count,
            'optimal_range': f"{self.OPTIMAL_MIN_WORDS}-{self.OPTIMAL_MAX_WORDS}"
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RECOMMENDATION ENGINE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_improvement_suggestions(self, evaluation_result: Dict, 
                                    prompt_text: str) -> List[str]:
        """
        Generate improvement suggestions based on evaluation results
        """
        suggestions = []
        
        # Clarity suggestions
        if evaluation_result['clarity_score'] < 70:
            suggestions.append("Add clear action verbs like 'create', 'analyze', or 'summarize'")
            if evaluation_result['details']['clarity'].get('vague_words_found'):
                suggestions.append("Replace vague words with specific terms")
        
        # Relevance suggestions
        if evaluation_result['relevance_score'] < 70:
            suggestions.append("Include more domain-specific keywords")
            suggestions.append("Specify the expected output format")
        
        # Length suggestions
        if evaluation_result['length_score'] < 70:
            word_count = evaluation_result['details']['length']['word_count']
            if word_count < self.OPTIMAL_MIN_WORDS:
                suggestions.append(f"Expand the prompt to at least {self.OPTIMAL_MIN_WORDS} words")
            else:
                suggestions.append(f"Condense the prompt to under {self.OPTIMAL_MAX_WORDS} words")
        
        return suggestions


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE FOR EASY ACCESS
# ═══════════════════════════════════════════════════════════════════════════════
evaluator = PromptEvaluator()


def evaluate_prompt(prompt_text: str, task_type: str = None, 
                   domain: str = None) -> Dict:
    """Convenience function to evaluate a prompt"""
    return evaluator.evaluate(prompt_text, task_type, domain)


def get_suggestions(evaluation_result: Dict, prompt_text: str) -> List[str]:
    """Convenience function to get improvement suggestions"""
    return evaluator.get_improvement_suggestions(evaluation_result, prompt_text)
