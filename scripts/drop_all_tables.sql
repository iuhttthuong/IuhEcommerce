-- Drop all tables, sequences, and types
DO $$ DECLARE
    r RECORD;
BEGIN
    -- Drop foreign key constraints
    FOR r IN (SELECT DISTINCT tc.constraint_name, tc.table_name
              FROM information_schema.table_constraints AS tc
              JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
              WHERE constraint_type = 'FOREIGN KEY') LOOP
        EXECUTE 'ALTER TABLE ' || quote_ident(r.table_name) || ' DROP CONSTRAINT ' || quote_ident(r.constraint_name);
    END LOOP;

    -- Drop all tables
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema() AND tableowner = 'E_commerce_chatbot') LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;

    -- Drop custom types
    FOR r IN (SELECT typname FROM pg_type WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = current_schema()) AND typtype = 'c') LOOP
        EXECUTE 'DROP TYPE IF EXISTS ' || quote_ident(r.typname) || ' CASCADE';
    END LOOP;

    -- Drop extensions
    DROP EXTENSION IF EXISTS pgcrypto CASCADE;
    DROP EXTENSION IF EXISTS vector CASCADE;
END $$;
