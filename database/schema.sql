-- ═══════════════════════════════════════════════════════════════════════════════
-- AI-ASSISTED PROMPT MANAGEMENT SYSTEM - DATABASE SCHEMA
-- RiseOfTheJaguar Project
-- ═══════════════════════════════════════════════════════════════════════════════

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS prompt_tag_map CASCADE;
DROP TABLE IF EXISTS prompt_evaluations CASCADE;
DROP TABLE IF EXISTS prompt_versions CASCADE;
DROP TABLE IF EXISTS prompt_tags CASCADE;
DROP TABLE IF EXISTS prompts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ═══════════════════════════════════════════════════════════════════════════════
-- USERS TABLE
-- Stores user authentication and profile information
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',  -- 'admin' or 'user'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- PROMPTS TABLE
-- Main prompt storage with metadata
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL,  -- 'generation', 'analysis', 'summarization', etc.
    domain VARCHAR(50),               -- 'healthcare', 'coding', 'education', etc.
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- PROMPT_VERSIONS TABLE
-- Version control for prompts - each edit creates a new version
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE prompt_versions (
    id SERIAL PRIMARY KEY,
    prompt_id INTEGER REFERENCES prompts(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    prompt_text TEXT NOT NULL,
    change_notes TEXT,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique version numbers per prompt
    UNIQUE(prompt_id, version_number)
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- PROMPT_EVALUATIONS TABLE
-- Stores AI evaluation scores for each version
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE prompt_evaluations (
    id SERIAL PRIMARY KEY,
    version_id INTEGER REFERENCES prompt_versions(id) ON DELETE CASCADE,
    clarity_score DECIMAL(5,2) NOT NULL,
    relevance_score DECIMAL(5,2) NOT NULL,
    length_score DECIMAL(5,2) NOT NULL,
    final_score DECIMAL(5,2) NOT NULL,
    evaluation_notes TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- PROMPT_TAGS TABLE
-- Tag definitions for categorization
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE prompt_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#6366f1',  -- Hex color code
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- PROMPT_TAG_MAP TABLE
-- Many-to-many relationship between prompts and tags
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE prompt_tag_map (
    prompt_id INTEGER REFERENCES prompts(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES prompt_tags(id) ON DELETE CASCADE,
    PRIMARY KEY (prompt_id, tag_id)
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- LLM_MODELS TABLE (Future Enhancement)
-- Store LLM model configurations for advanced evaluation
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE llm_models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(50),  -- 'openai', 'google', 'anthropic'
    model_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- INDEXES FOR PERFORMANCE
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE INDEX idx_prompts_user_id ON prompts(user_id);
CREATE INDEX idx_prompts_task_type ON prompts(task_type);
CREATE INDEX idx_prompts_domain ON prompts(domain);
CREATE INDEX idx_versions_prompt_id ON prompt_versions(prompt_id);
CREATE INDEX idx_versions_is_current ON prompt_versions(is_current);
CREATE INDEX idx_evaluations_version_id ON prompt_evaluations(version_id);
CREATE INDEX idx_evaluations_final_score ON prompt_evaluations(final_score DESC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- TRIGGER: Update timestamp on prompts update
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_prompts_updated_at
    BEFORE UPDATE ON prompts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ═══════════════════════════════════════════════════════════════════════════════
-- SEED DATA: Default tags
-- ═══════════════════════════════════════════════════════════════════════════════
INSERT INTO prompt_tags (name, color, description) VALUES
    ('Code Generation', '#10b981', 'Prompts for generating code'),
    ('Text Analysis', '#f59e0b', 'Prompts for analyzing text'),
    ('Summarization', '#6366f1', 'Prompts for summarizing content'),
    ('Healthcare', '#ef4444', 'Healthcare domain prompts'),
    ('Education', '#8b5cf6', 'Education domain prompts'),
    ('Creative Writing', '#ec4899', 'Creative writing prompts'),
    ('Data Analysis', '#14b8a6', 'Data analysis prompts'),
    ('Customer Support', '#f97316', 'Customer support prompts');

-- ═══════════════════════════════════════════════════════════════════════════════
-- SEED DATA: Demo user (password: demo123)
-- ═══════════════════════════════════════════════════════════════════════════════
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
    ('demo', 'demo@example.com', 'pbkdf2:sha256:260000$demo$demo123hash', 'Demo User', 'admin');
