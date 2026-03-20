-- Database initialization script
-- This script runs automatically when PostgreSQL starts for the first time

-- Enable essential extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search indexes
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- For encryption functions

-- Create schema with comment
CREATE SCHEMA IF NOT EXISTS public;
COMMENT ON SCHEMA public IS 'Standard public schema';

-- Set default schema
SET search_path TO public;

-- Grant permissions
GRANT USAGE ON SCHEMA public TO postgres;
GRANT CREATE ON SCHEMA public TO postgres;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create function for soft delete trigger
CREATE OR REPLACE FUNCTION check_soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        NEW.deleted_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

COMMIT;
