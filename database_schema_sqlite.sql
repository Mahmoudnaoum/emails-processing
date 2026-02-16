-- Email Relationship Analysis Database Schema (SQLite Version)
-- Designed to support MVP for 5 users with email analysis and relationship tracking

-- Users table - to support multiple users submitting their emails
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Companies table - extracted from email domains
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- People table - individuals identified from emails
CREATE TABLE people (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    email TEXT NOT NULL,
    name TEXT,
    company_id INTEGER,
    role TEXT,
    is_primary_user BOOLEAN DEFAULT 0, -- Marks the user who owns this email account
    relationship_strength TEXT DEFAULT 'unknown', -- strong, moderate, weak, unknown
    last_interaction_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    UNIQUE(user_id, email)
);

-- Expertise areas table - for tracking areas of expertise
CREATE TABLE expertise_areas (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Person expertise mapping - many-to-many relationship
CREATE TABLE person_expertise (
    id INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL,
    expertise_id INTEGER NOT NULL,
    confidence_score REAL DEFAULT 0.5, -- 0.0 to 1.0
    source_email_id TEXT, -- Reference to the email that provided this expertise
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE,
    FOREIGN KEY (expertise_id) REFERENCES expertise_areas(id) ON DELETE CASCADE,
    UNIQUE(person_id, expertise_id)
);

-- Interactions table - core relationship data
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    thread_id TEXT, -- Gmail thread ID for grouping conversations
    email_id TEXT NOT NULL, -- Gmail email ID
    subject TEXT NOT NULL,
    interaction_date DATE NOT NULL,
    interaction_type TEXT DEFAULT 'email', -- email, meeting, call, etc.
    summary TEXT NOT NULL, -- LLM-generated summary of the interaction
    full_content TEXT, -- Full email content for reference
    participant_count INTEGER DEFAULT 2, -- Number of people involved
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Interaction participants table - people involved in each interaction
CREATE TABLE interaction_participants (
    id INTEGER PRIMARY KEY,
    interaction_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    role_in_interaction TEXT, -- sender, recipient, cc, mentioned, expert, etc.
    is_expert BOOLEAN DEFAULT 0, -- Whether this person provided expertise in this interaction
    expertise_area_id INTEGER, -- If they were the expert, what area?
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interaction_id) REFERENCES interactions(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE,
    FOREIGN KEY (expertise_area_id) REFERENCES expertise_areas(id),
    UNIQUE(interaction_id, person_id)
);

-- Interaction companies table - companies involved in each interaction
CREATE TABLE interaction_companies (
    id INTEGER PRIMARY KEY,
    interaction_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    involvement_type TEXT, -- primary_company, mentioned, client, partner, etc.
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interaction_id) REFERENCES interactions(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(interaction_id, company_id)
);

-- Email processing status table - track which emails have been processed
CREATE TABLE email_processing_status (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    email_id TEXT NOT NULL,
    thread_id TEXT,
    processed BOOLEAN DEFAULT 0,
    filtered_out BOOLEAN DEFAULT 0, -- True if email was filtered as newsletter/notification
    filter_reason TEXT, -- Reason for filtering
    processing_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, email_id)
);

-- Create indexes for performance
CREATE INDEX idx_people_user_email ON people(user_id, email);
CREATE INDEX idx_people_company ON people(company_id);
CREATE INDEX idx_interactions_user_date ON interactions(user_id, interaction_date DESC);
CREATE INDEX idx_interactions_thread ON interactions(thread_id);
CREATE INDEX idx_interaction_participants_interaction ON interaction_participants(interaction_id);
CREATE INDEX idx_interaction_participants_person ON interaction_participants(person_id);
CREATE INDEX idx_person_expertise_person ON person_expertise(person_id);
CREATE INDEX idx_email_processing_status_user_processed ON email_processing_status(user_id, processed);

-- Insert some default expertise areas
INSERT INTO expertise_areas (name, description) VALUES
('hiring', 'Recruitment and talent acquisition expertise'),
('growth', 'Business growth and scaling expertise'),
('strategy', 'Strategic planning and business strategy'),
('technology', 'Technical expertise and software development'),
('marketing', 'Marketing and customer acquisition'),
('finance', 'Financial planning and investment'),
('operations', 'Business operations and management'),
('sales', 'Sales and business development'),
('product', 'Product development and management'),
('leadership', 'Leadership and team management');

-- Create view for easy querying of a person's relationships
CREATE VIEW person_relationships AS
SELECT 
    p1.id as person_id,
    p1.name as person_name,
    p1.email as person_email,
    p2.id as related_person_id,
    p2.name as related_person_name,
    p2.email as related_person_email,
    c.name as related_company,
    COUNT(i.id) as interaction_count,
    MAX(i.interaction_date) as last_interaction_date,
    GROUP_CONCAT(i.subject, '; ') as recent_subjects
FROM people p1
JOIN interaction_participants ip1 ON p1.id = ip1.person_id
JOIN interactions i ON ip1.interaction_id = i.id
JOIN interaction_participants ip2 ON i.id = ip2.interaction_id AND ip2.person_id != p1.id
JOIN people p2 ON ip2.person_id = p2.id
LEFT JOIN companies c ON p2.company_id = c.id
WHERE p1.is_primary_user = 1
GROUP BY p1.id, p1.name, p1.email, p2.id, p2.name, p2.email, c.name
ORDER BY last_interaction_date DESC;