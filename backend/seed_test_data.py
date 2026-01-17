"""
Comprehensive Test Data Seeding Script
Seeds the database with diverse prompts, versions, evaluations, and tags
"""
from datetime import datetime, timedelta
import random
from app import create_app
from models import db, User, Prompt, PromptVersion, PromptEvaluation, PromptTag

def seed_test_data():
    """Seed comprehensive test data"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting test data seeding...")
        
        # ═══════════════════════════════════════════════════════════════════
        # 1. CREATE USERS
        # ═══════════════════════════════════════════════════════════════════
        users_data = [
            {'username': 'demo', 'email': 'demo@example.com', 'full_name': 'Demo User', 'role': 'admin', 'password': 'demo123'},
            {'username': 'alice', 'email': 'alice@company.com', 'full_name': 'Alice Johnson', 'role': 'user', 'password': 'alice123'},
            {'username': 'bob', 'email': 'bob@company.com', 'full_name': 'Bob Smith', 'role': 'user', 'password': 'bob123'},
        ]
        
        users = {}
        for u_data in users_data:
            user = User.query.filter_by(username=u_data['username']).first()
            if not user:
                user = User(
                    username=u_data['username'],
                    email=u_data['email'],
                    full_name=u_data['full_name'],
                    role=u_data['role']
                )
                user.set_password(u_data['password'])
                db.session.add(user)
                db.session.flush()
                print(f"  ✅ Created user: {u_data['username']}")
            users[u_data['username']] = user
        
        # ═══════════════════════════════════════════════════════════════════
        # 2. CREATE TAGS
        # ═══════════════════════════════════════════════════════════════════
        tags_data = [
            {'name': 'Production', 'color': '#22c55e', 'description': 'Production-ready prompts'},
            {'name': 'Testing', 'color': '#eab308', 'description': 'Prompts under testing'},
            {'name': 'Deprecated', 'color': '#ef4444', 'description': 'Old or deprecated prompts'},
            {'name': 'High Priority', 'color': '#f97316', 'description': 'High priority prompts'},
            {'name': 'AI Assistant', 'color': '#8b5cf6', 'description': 'General AI assistant prompts'},
            {'name': 'Code Gen', 'color': '#06b6d4', 'description': 'Code generation prompts'},
            {'name': 'Healthcare', 'color': '#ec4899', 'description': 'Healthcare domain prompts'},
            {'name': 'Education', 'color': '#14b8a6', 'description': 'Education domain prompts'},
        ]
        
        tags = {}
        for t_data in tags_data:
            tag = PromptTag.query.filter_by(name=t_data['name']).first()
            if not tag:
                tag = PromptTag(name=t_data['name'], color=t_data['color'], description=t_data['description'])
                db.session.add(tag)
                db.session.flush()
                print(f"  🏷️  Created tag: {t_data['name']}")
            tags[t_data['name']] = tag
        
        # ═══════════════════════════════════════════════════════════════════
        # 3. CREATE PROMPTS WITH VERSIONS AND EVALUATIONS
        # ═══════════════════════════════════════════════════════════════════
        prompts_data = [
            {
                'user': 'demo',
                'title': 'Code Review Assistant',
                'description': 'Analyzes code for bugs, security issues, and best practices',
                'task_type': 'analysis',
                'domain': 'coding',
                'tags': ['Production', 'Code Gen', 'High Priority'],
                'versions': [
                    {
                        'text': 'Review this code and find bugs.',
                        'notes': 'Initial basic version',
                        'scores': {'clarity': 45, 'relevance': 50, 'length': 30}
                    },
                    {
                        'text': 'Analyze the following code for potential bugs, security vulnerabilities, and performance issues. List each issue with severity level.',
                        'notes': 'Added security and performance analysis',
                        'scores': {'clarity': 72, 'relevance': 78, 'length': 65}
                    },
                    {
                        'text': 'You are an expert code reviewer. Analyze the following code for:\n1. Bugs and logical errors\n2. Security vulnerabilities (OWASP Top 10)\n3. Performance bottlenecks\n4. Code style and best practices\n\nFor each issue found, provide:\n- Severity: Critical/High/Medium/Low\n- Location: Line number or function name\n- Description: What the issue is\n- Fix: How to resolve it\n\nCode to review:\n{code}',
                        'notes': 'Comprehensive structured version with OWASP reference',
                        'scores': {'clarity': 92, 'relevance': 95, 'length': 88},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'Patient Diagnosis Summary',
                'description': 'Generates structured patient diagnosis summaries from clinical notes',
                'task_type': 'generation',
                'domain': 'healthcare',
                'tags': ['Healthcare', 'Production'],
                'versions': [
                    {
                        'text': 'Summarize patient diagnosis.',
                        'notes': 'Initial version',
                        'scores': {'clarity': 35, 'relevance': 40, 'length': 25}
                    },
                    {
                        'text': 'Based on the clinical notes provided, create a structured patient diagnosis summary including:\n\n**Patient Information:**\n- Chief Complaint\n- History of Present Illness\n- Past Medical History\n\n**Diagnosis:**\n- Primary Diagnosis (ICD-10 code if applicable)\n- Secondary Diagnoses\n\n**Treatment Plan:**\n- Medications\n- Follow-up Schedule\n- Lifestyle Recommendations\n\nClinical Notes:\n{notes}',
                        'notes': 'Added ICD-10 codes and structured format',
                        'scores': {'clarity': 88, 'relevance': 90, 'length': 82},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'Educational Lesson Plan Generator',
                'description': 'Creates detailed lesson plans for various subjects and grade levels',
                'task_type': 'generation',
                'domain': 'education',
                'tags': ['Education', 'Testing'],
                'versions': [
                    {
                        'text': 'Create a lesson plan for {subject}.',
                        'notes': 'Basic template',
                        'scores': {'clarity': 40, 'relevance': 45, 'length': 30}
                    },
                    {
                        'text': 'Design a comprehensive lesson plan for teaching {subject} to {grade_level} students.\n\nInclude:\n1. **Learning Objectives** (3-5 measurable outcomes)\n2. **Materials Needed**\n3. **Introduction** (5-10 minutes) - Hook activity\n4. **Main Lesson** (20-30 minutes)\n5. **Practice Activities** (15-20 minutes)\n6. **Assessment** - How to evaluate understanding\n7. **Differentiation** - Modifications for diverse learners\n8. **Homework/Extension**\n\nDuration: {duration} minutes\nStandards: Align with {standards}',
                        'notes': 'Comprehensive with differentiation and standards alignment',
                        'scores': {'clarity': 85, 'relevance': 88, 'length': 80},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'SQL Query Generator',
                'description': 'Converts natural language to optimized SQL queries',
                'task_type': 'transformation',
                'domain': 'coding',
                'tags': ['Code Gen', 'Testing'],
                'versions': [
                    {
                        'text': 'Convert to SQL: {request}',
                        'notes': 'Minimal version',
                        'scores': {'clarity': 30, 'relevance': 35, 'length': 20}
                    },
                    {
                        'text': 'Convert the following natural language request into an optimized SQL query.\n\nDatabase Schema:\n{schema}\n\nRequest: {request}\n\nProvide:\n1. The SQL query\n2. Explanation of the query\n3. Any indexes that would improve performance',
                        'notes': 'Added schema context and optimization tips',
                        'scores': {'clarity': 78, 'relevance': 82, 'length': 75},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'Customer Support Response',
                'description': 'Generates professional and empathetic customer support responses',
                'task_type': 'generation',
                'domain': 'customer_service',
                'tags': ['Production', 'AI Assistant'],
                'versions': [
                    {
                        'text': 'Reply to customer complaint.',
                        'notes': 'Basic version',
                        'scores': {'clarity': 38, 'relevance': 42, 'length': 28}
                    },
                    {
                        'text': 'You are a professional customer support representative. Respond to the following customer inquiry with:\n- Empathy and understanding\n- Clear solution or next steps\n- Professional and friendly tone\n\nCompany: {company_name}\nCustomer Issue: {issue}\nCustomer Sentiment: {sentiment}\n\nGuidelines:\n- Acknowledge the customer\'s feelings\n- Apologize if appropriate\n- Provide specific resolution steps\n- Offer compensation if policy allows\n- End with reassurance',
                        'notes': 'Added sentiment awareness and structured response',
                        'scores': {'clarity': 86, 'relevance': 89, 'length': 78},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'Technical Documentation Writer',
                'description': 'Creates clear technical documentation from code or specifications',
                'task_type': 'generation',
                'domain': 'technical',
                'tags': ['Code Gen', 'High Priority'],
                'versions': [
                    {
                        'text': 'Write documentation for {component}.',
                        'notes': 'Initial version',
                        'scores': {'clarity': 42, 'relevance': 48, 'length': 32}
                    },
                    {
                        'text': 'Create comprehensive technical documentation for the following component:\n\n**Component:** {component}\n**Type:** {type} (API/Library/Service)\n\nGenerate:\n\n## Overview\nBrief description\n\n## Installation\nStep-by-step setup instructions\n\n## API Reference\n- Endpoints/Methods with parameters\n- Request/Response examples\n- Error codes\n\n## Usage Examples\nCommon use cases with code snippets\n\n## Configuration\nAvailable options and defaults\n\n## Troubleshooting\nCommon issues and solutions',
                        'notes': 'Comprehensive documentation template',
                        'scores': {'clarity': 90, 'relevance': 92, 'length': 85},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'Data Analysis Report Generator',
                'description': 'Generates insights and reports from data analysis results',
                'task_type': 'analysis',
                'domain': 'analytics',
                'tags': ['Testing', 'AI Assistant'],
                'versions': [
                    {
                        'text': 'Analyze this data and write a report.',
                        'notes': 'Basic version',
                        'scores': {'clarity': 35, 'relevance': 40, 'length': 28},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'Meeting Notes Summarizer',
                'description': 'Summarizes meeting transcripts into actionable notes',
                'task_type': 'summarization',
                'domain': 'productivity',
                'tags': ['Production', 'AI Assistant'],
                'versions': [
                    {
                        'text': 'Summarize meeting notes.',
                        'notes': 'Basic version',
                        'scores': {'clarity': 32, 'relevance': 38, 'length': 22}
                    },
                    {
                        'text': 'Analyze the following meeting transcript and create structured notes:\n\n**Meeting Transcript:**\n{transcript}\n\n**Generate:**\n\n## Meeting Summary\nBrief overview (2-3 sentences)\n\n## Key Discussion Points\n- Main topics discussed\n\n## Decisions Made\n- List all decisions with rationale\n\n## Action Items\n| Owner | Task | Deadline |\n|-------|------|----------|\n\n## Follow-up Required\n- Items needing further discussion\n\n## Next Meeting\n- Proposed date/agenda if mentioned',
                        'notes': 'Structured with action items table',
                        'scores': {'clarity': 88, 'relevance': 91, 'length': 83},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'API Error Handler',
                'description': 'Generates user-friendly error messages from technical errors',
                'task_type': 'transformation',
                'domain': 'coding',
                'tags': ['Code Gen', 'Deprecated'],
                'versions': [
                    {
                        'text': 'Convert this error to user message: {error}',
                        'notes': 'Simple conversion',
                        'scores': {'clarity': 55, 'relevance': 60, 'length': 45},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'Interview Question Generator',
                'description': 'Creates relevant interview questions based on job role',
                'task_type': 'generation',
                'domain': 'hr',
                'tags': ['Testing'],
                'versions': [
                    {
                        'text': 'Generate interview questions for {role}.',
                        'notes': 'Basic version',
                        'scores': {'clarity': 45, 'relevance': 50, 'length': 35}
                    },
                    {
                        'text': 'Create a comprehensive interview question set for the following position:\n\n**Role:** {role}\n**Level:** {level} (Junior/Mid/Senior)\n**Department:** {department}\n\nGenerate questions in these categories:\n\n## Technical Questions (5-7)\nRole-specific technical skills\n\n## Behavioral Questions (3-5)\nUsing STAR method format\n\n## Situational Questions (3-4)\nHypothetical scenarios\n\n## Culture Fit (2-3)\nTeam and company alignment\n\nFor each question, provide:\n- The question\n- What it assesses\n- Red flags in answers\n- Strong answer indicators',
                        'notes': 'Comprehensive with evaluation criteria',
                        'scores': {'clarity': 87, 'relevance': 90, 'length': 82},
                        'is_current': True
                    }
                ]
            },
            # ════════════════════════════════════════════════════════════════
            # 5 MORE PROMPTS TO REACH 15 TOTAL
            # ════════════════════════════════════════════════════════════════
            {
                'user': 'demo',
                'title': 'Email Subject Line Optimizer',
                'description': 'Generates engaging email subject lines for marketing campaigns',
                'task_type': 'generation',
                'domain': 'marketing',
                'tags': ['Production', 'AI Assistant'],
                'versions': [
                    {
                        'text': 'Write a subject line for this email.',
                        'notes': 'Basic version',
                        'scores': {'clarity': 40, 'relevance': 45, 'length': 35}
                    },
                    {
                        'text': 'Generate 5 compelling email subject lines for the following campaign:\n\n**Campaign Type:** {campaign_type}\n**Target Audience:** {audience}\n**Key Message:** {message}\n**Tone:** {tone}\n\nFor each subject line provide:\n- The subject line (under 50 characters)\n- Predicted open rate impact\n- A/B testing recommendation',
                        'notes': 'Added A/B testing and metrics',
                        'scores': {'clarity': 82, 'relevance': 85, 'length': 78},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'Bug Report Analyzer',
                'description': 'Analyzes bug reports and suggests fixes',
                'task_type': 'analysis',
                'domain': 'coding',
                'tags': ['Code Gen', 'Testing'],
                'versions': [
                    {
                        'text': 'Analyze this bug report: {bug}',
                        'notes': 'Minimal version',
                        'scores': {'clarity': 38, 'relevance': 42, 'length': 30}
                    },
                    {
                        'text': 'Analyze the following bug report and provide a comprehensive diagnosis:\n\n**Bug Report:**\n{bug_report}\n\n**System Info:**\n{system_info}\n\n**Generate:**\n\n## Root Cause Analysis\n- Probable cause\n- Contributing factors\n\n## Reproduction Steps\n1. Step-by-step to reproduce\n\n## Suggested Fix\n- Code changes needed\n- Files to modify\n\n## Testing Recommendations\n- Test cases to add\n- Regression tests',
                        'notes': 'Comprehensive with root cause analysis',
                        'scores': {'clarity': 85, 'relevance': 88, 'length': 80},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'Legal Contract Summarizer',
                'description': 'Summarizes legal contracts highlighting key terms and risks',
                'task_type': 'summarization',
                'domain': 'legal',
                'tags': ['Production', 'High Priority'],
                'versions': [
                    {
                        'text': 'Summarize this contract.',
                        'notes': 'Basic version',
                        'scores': {'clarity': 32, 'relevance': 35, 'length': 25}
                    },
                    {
                        'text': 'Analyze and summarize the following legal contract:\n\n**Contract Text:**\n{contract}\n\n**Generate:**\n\n## Executive Summary\nOne paragraph overview\n\n## Key Terms\n- Duration/Term\n- Payment terms\n- Deliverables\n- Termination clauses\n\n## Parties Obligations\n| Party | Obligations |\n|-------|-------------|\n\n## Risk Assessment\n- Potential liabilities\n- Unfavorable clauses\n- Missing protections\n\n## Recommended Actions\n- Negotiation points\n- Clauses to modify',
                        'notes': 'Added risk assessment and negotiation tips',
                        'scores': {'clarity': 90, 'relevance': 93, 'length': 85},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'Product Description Writer',
                'description': 'Creates compelling product descriptions for e-commerce',
                'task_type': 'generation',
                'domain': 'marketing',
                'tags': ['Production', 'AI Assistant'],
                'versions': [
                    {
                        'text': 'Write a product description for {product}.',
                        'notes': 'Simple version',
                        'scores': {'clarity': 45, 'relevance': 50, 'length': 40}
                    },
                    {
                        'text': 'Create an engaging product description for e-commerce:\n\n**Product:** {product_name}\n**Category:** {category}\n**Key Features:** {features}\n**Target Customer:** {target}\n**Price Point:** {price}\n\n**Generate:**\n\n## Headline\nAttention-grabbing title\n\n## Short Description\n2-3 sentences for listings\n\n## Full Description\n- Benefits (not just features)\n- Use cases\n- What makes it unique\n\n## SEO Keywords\nRelevant search terms\n\n## Call to Action\nCompelling purchase prompt',
                        'notes': 'SEO optimized with multiple formats',
                        'scores': {'clarity': 86, 'relevance': 89, 'length': 82},
                        'is_current': True
                    }
                ]
            },
            {
                'user': 'demo',
                'title': 'Research Paper Outline Generator',
                'description': 'Creates structured outlines for academic research papers',
                'task_type': 'generation',
                'domain': 'education',
                'tags': ['Education', 'Testing'],
                'versions': [
                    {
                        'text': 'Create an outline for a paper on {topic}.',
                        'notes': 'Basic outline',
                        'scores': {'clarity': 42, 'relevance': 48, 'length': 35}
                    },
                    {
                        'text': 'Generate a comprehensive research paper outline:\n\n**Topic:** {topic}\n**Academic Level:** {level}\n**Citation Style:** {citation_style}\n**Word Count Target:** {word_count}\n\n**Generate:**\n\n## Title Options\n3 potential titles\n\n## Abstract Structure\nKey points to include\n\n## Introduction\n- Hook\n- Background\n- Thesis statement\n\n## Literature Review\n- Key themes to explore\n- Suggested sources\n\n## Methodology\nApproach and methods\n\n## Expected Results\nHypotheses\n\n## Conclusion Framework\nMain arguments to summarize\n\n## References\nSuggested starting sources',
                        'notes': 'Full academic structure with citation guidance',
                        'scores': {'clarity': 88, 'relevance': 91, 'length': 84},
                        'is_current': True
                    }
                ]
            }
        ]
        
        for p_data in prompts_data:
            # Check if prompt already exists
            existing = Prompt.query.filter_by(
                title=p_data['title'], 
                user_id=users[p_data['user']].id
            ).first()
            
            if existing:
                print(f"  ⏭️  Prompt exists: {p_data['title']}")
                continue
            
            # Create prompt
            prompt = Prompt(
                user_id=users[p_data['user']].id,
                title=p_data['title'],
                description=p_data['description'],
                task_type=p_data['task_type'],
                domain=p_data['domain']
            )
            db.session.add(prompt)
            db.session.flush()
            
            # Add tags
            for tag_name in p_data.get('tags', []):
                if tag_name in tags:
                    prompt.tags.append(tags[tag_name])
            
            # Create versions with evaluations
            for i, v_data in enumerate(p_data['versions'], 1):
                version = PromptVersion(
                    prompt_id=prompt.id,
                    version_number=i,
                    prompt_text=v_data['text'],
                    change_notes=v_data['notes'],
                    is_current=v_data.get('is_current', False),
                    created_at=datetime.utcnow() - timedelta(days=len(p_data['versions']) - i)
                )
                db.session.add(version)
                db.session.flush()
                
                # Create evaluation
                scores = v_data['scores']
                final_score = (scores['clarity'] * 0.4 + scores['relevance'] * 0.4 + scores['length'] * 0.2)
                
                evaluation = PromptEvaluation(
                    version_id=version.id,
                    clarity_score=scores['clarity'],
                    relevance_score=scores['relevance'],
                    length_score=scores['length'],
                    final_score=round(final_score, 2),
                    evaluation_notes=f"Auto-evaluated: Clarity {scores['clarity']}/100, Relevance {scores['relevance']}/100, Length {scores['length']}/100",
                    evaluated_at=version.created_at + timedelta(hours=1)
                )
                db.session.add(evaluation)
            
            print(f"  📝 Created prompt: {p_data['title']} ({len(p_data['versions'])} versions)")
        
        # Commit all changes
        db.session.commit()
        print("\n✅ Test data seeding completed successfully!")
        print(f"   Users: {len(users_data)}")
        print(f"   Tags: {len(tags_data)}")
        print(f"   Prompts: {len(prompts_data)}")
        print(f"   Total versions: {sum(len(p['versions']) for p in prompts_data)}")


if __name__ == '__main__':
    seed_test_data()
