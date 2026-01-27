-- Database Schema for Alazhar E-Learning Project
-- Run this script in your Supabase SQL editor to create all required tables

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Video Info Table (Base YouTube video data)
CREATE TABLE IF NOT EXISTS video_info (
    video_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    published_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Suggestion Video Info Table (Extended metadata for videos)
CREATE TABLE IF NOT EXISTS suggestion_video_info (
    video_id TEXT PRIMARY KEY,
    main_level TEXT,
    common_sub_level TEXT,
    specialized_level TEXT,
    lecture_title TEXT,
    lesson_name TEXT,
    batch DATE,
    is_related_video BOOLEAN,
    FOREIGN KEY (video_id) REFERENCES video_info(video_id) ON DELETE CASCADE
);

-- Title Suggestions Table
CREATE TABLE IF NOT EXISTS title_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id TEXT NOT NULL,
    title_text TEXT NOT NULL,
    approval_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (video_id) REFERENCES video_info(video_id) ON DELETE CASCADE
);

-- Description Suggestions Table
CREATE TABLE IF NOT EXISTS description_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id TEXT NOT NULL,
    description_text TEXT NOT NULL,
    approval_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (video_id) REFERENCES video_info(video_id) ON DELETE CASCADE
);

-- Title Votes Table
CREATE TABLE IF NOT EXISTS title_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title_suggestion_id UUID NOT NULL,
    voter_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (title_suggestion_id) REFERENCES title_suggestions(id) ON DELETE CASCADE,
    UNIQUE(title_suggestion_id, voter_hash)
);

-- Description Votes Table
CREATE TABLE IF NOT EXISTS description_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    description_suggestion_id UUID NOT NULL,
    voter_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (description_suggestion_id) REFERENCES description_suggestions(id) ON DELETE CASCADE,
    UNIQUE(description_suggestion_id, voter_hash)
);

-- Video Votes Table
CREATE TABLE IF NOT EXISTS video_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id TEXT NOT NULL,
    voter_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (video_id) REFERENCES video_info(video_id) ON DELETE CASCADE
);

-- Lesson Name Suggestions Table
CREATE TABLE IF NOT EXISTS lesson_name_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id TEXT NOT NULL,
    lesson_name_text TEXT NOT NULL,
    approval_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (video_id) REFERENCES video_info(video_id) ON DELETE CASCADE
);

-- Lesson Name Votes Table
CREATE TABLE IF NOT EXISTS lesson_name_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lesson_name_suggestion_id UUID NOT NULL,
    voter_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (lesson_name_suggestion_id) REFERENCES lesson_name_suggestions(id) ON DELETE CASCADE,
    UNIQUE(lesson_name_suggestion_id, voter_hash)
);

-- Lecturer Suggestions Table
CREATE TABLE IF NOT EXISTS lecturer_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id TEXT NOT NULL,
    lecturer_name_text TEXT NOT NULL,
    approval_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (video_id) REFERENCES video_info(video_id) ON DELETE CASCADE
);

-- Lecturer Votes Table
CREATE TABLE IF NOT EXISTS lecturer_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lecturer_suggestion_id UUID NOT NULL,
    voter_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (lecturer_suggestion_id) REFERENCES lecturer_suggestions(id) ON DELETE CASCADE,
    UNIQUE(lecturer_suggestion_id, voter_hash)
);

-- Related-suggestions: users vote whether each video is "related" or not (is_related)
CREATE TABLE IF NOT EXISTS related_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id TEXT NOT NULL,
    is_related BOOLEAN NOT NULL,
    approval_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (video_id) REFERENCES video_info(video_id) ON DELETE CASCADE,
    UNIQUE(video_id, is_related)
);

CREATE TABLE IF NOT EXISTS related_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    related_suggestion_id UUID NOT NULL,
    voter_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (related_suggestion_id) REFERENCES related_suggestions(id) ON DELETE CASCADE,
    UNIQUE(related_suggestion_id, voter_hash)
);

CREATE INDEX IF NOT EXISTS idx_related_suggestions_video_id ON related_suggestions(video_id);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_title_suggestions_video_id ON title_suggestions(video_id);
CREATE INDEX IF NOT EXISTS idx_title_suggestions_approval_count ON title_suggestions(approval_count DESC);
CREATE INDEX IF NOT EXISTS idx_description_suggestions_video_id ON description_suggestions(video_id);
CREATE INDEX IF NOT EXISTS idx_description_suggestions_approval_count ON description_suggestions(approval_count DESC);
CREATE INDEX IF NOT EXISTS idx_title_votes_suggestion_id ON title_votes(title_suggestion_id);
CREATE INDEX IF NOT EXISTS idx_description_votes_suggestion_id ON description_votes(description_suggestion_id);
CREATE INDEX IF NOT EXISTS idx_video_info_published_at ON video_info(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_lesson_name_suggestions_video_id ON lesson_name_suggestions(video_id);
CREATE INDEX IF NOT EXISTS idx_lesson_name_suggestions_approval_count ON lesson_name_suggestions(approval_count DESC);
CREATE INDEX IF NOT EXISTS idx_lecturer_suggestions_video_id ON lecturer_suggestions(video_id);
CREATE INDEX IF NOT EXISTS idx_lecturer_suggestions_approval_count ON lecturer_suggestions(approval_count DESC);
