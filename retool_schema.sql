-- Simplified Database Schema for Retool Integration
-- Run this in your Retool PostgreSQL database

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- People table
CREATE TABLE IF NOT EXISTS people (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    company_id INTEGER REFERENCES companies(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Expertise areas table
CREATE TABLE IF NOT EXISTS expertise_areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT
);

-- Person expertise junction table
CREATE TABLE IF NOT EXISTS person_expertise (
    person_id INTEGER REFERENCES people(id) ON DELETE CASCADE,
    expertise_id INTEGER REFERENCES expertise_areas(id) ON DELETE CASCADE,
    PRIMARY KEY (person_id, expertise_id)
);

-- Interactions table
CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    email_id VARCHAR(255) UNIQUE NOT NULL,
    thread_id VARCHAR(255),
    subject VARCHAR(500),
    summary TEXT,
    date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interaction participants junction table
CREATE TABLE IF NOT EXISTS interaction_participants (
    interaction_id INTEGER REFERENCES interactions(id) ON DELETE CASCADE,
    person_id INTEGER REFERENCES people(id) ON DELETE CASCADE,
    PRIMARY KEY (interaction_id, person_id)
);

-- Processed emails tracking
CREATE TABLE IF NOT EXISTS processed_emails (
    email_id VARCHAR(255) PRIMARY KEY,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_people_email ON people(email);
CREATE INDEX IF NOT EXISTS idx_people_company ON people(company_id);
CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies(domain);
CREATE INDEX IF NOT EXISTS idx_interactions_date ON interactions(date);
CREATE INDEX IF NOT EXISTS idx_interactions_email_id ON interactions(email_id);
