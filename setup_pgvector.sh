#!/bin/bash

set -e

DB_NAME="code_review_ai"
PG_VECTOR_REPO="https://github.com/pgvector/pgvector.git"

echo "Installing PostgreSQL and development libraries..."
sudo apt update
sudo apt install -y postgresql-server-dev-all git make gcc

echo "Installing pgvector extension..."
git clone $PG_VECTOR_REPO
cd pgvector
make
sudo make install

echo "Creating database '$DB_NAME' and enabling pgvector extension..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
sudo -u postgres psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "Creating tables..."
sudo -u postgres psql -d $DB_NAME -c "
CREATE TABLE IF NOT EXISTS reviews (
    review_id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comments TEXT[],
    suggestions TEXT[]
);

CREATE TABLE IF NOT EXISTS code_snippets (
    snippet_id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    review_id UUID REFERENCES reviews(review_id),
    file_name VARCHAR(255) NOT NULL,
    code TEXT NOT NULL,
    language VARCHAR(50),
    added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_base (
    knowledge_id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    review_id UUID REFERENCES reviews(review_id),
    snippet_id UUID REFERENCES code_snippets(snippet_id),
    embedding VECTOR(1536),
    raw_text TEXT,
    embedding_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"

echo "PostgreSQL setup complete with pgvector and required tables."