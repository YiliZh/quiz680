-- Drop existing table and its dependencies
DROP TABLE IF EXISTS public.uploads CASCADE;

-- Create new uploads table
CREATE TABLE public.uploads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    stored_path VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'processing',
    uploaded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id
CREATE INDEX idx_uploads_user_id ON public.uploads USING btree (user_id);

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_uploads_updated_at
    BEFORE UPDATE ON public.uploads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 