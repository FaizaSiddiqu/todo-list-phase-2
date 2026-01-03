-- Phase III: Add conversation and message tables
-- Migration: 003_add_chat_tables.sql
-- Date: 2026-01-03

-- Create conversation table
CREATE TABLE IF NOT EXISTS conversation (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for conversation
CREATE INDEX IF NOT EXISTS idx_conversation_user_id ON conversation(user_id);

-- Create message table
CREATE TABLE IF NOT EXISTS message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for message
CREATE INDEX IF NOT EXISTS idx_message_conversation_id ON message(conversation_id);
CREATE INDEX IF NOT EXISTS idx_message_user_id ON message(user_id);
CREATE INDEX IF NOT EXISTS idx_message_created_at ON message(created_at);

-- Verification queries
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('conversation', 'message');
-- SELECT indexname FROM pg_indexes WHERE tablename IN ('conversation', 'message');
