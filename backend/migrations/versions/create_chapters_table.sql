-- Drop dependent tables first
DROP TABLE IF EXISTS public.questions CASCADE;
DROP TABLE IF EXISTS public.chapter_tags CASCADE;
DROP TABLE IF EXISTS public.chapters CASCADE;

-- Create table
CREATE TABLE public.chapters (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER NOT NULL,
    chapter_no INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chapters_upload
        FOREIGN KEY (upload_id)
        REFERENCES public.uploads(id)
        ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_chapters_upload_id ON public.chapters USING btree (upload_id);
CREATE INDEX idx_chapters_chapter_no ON public.chapters USING btree (chapter_no);

-- Add comment
COMMENT ON TABLE public.chapters IS 'Stores chapters extracted from uploaded PDFs';

-- Recreate questions table
CREATE TABLE public.questions (
    id SERIAL PRIMARY KEY,
    chapter_id INTEGER NOT NULL,
    q_text TEXT NOT NULL,
    options JSONB NOT NULL,
    answer_key INTEGER NOT NULL,
    explanation TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_questions_chapter
        FOREIGN KEY (chapter_id)
        REFERENCES public.chapters(id)
        ON DELETE CASCADE
);

-- Create indexes for questions
CREATE INDEX idx_questions_chapter_id ON public.questions USING btree (chapter_id);

-- Add comment for questions
COMMENT ON TABLE public.questions IS 'Stores quiz questions for each chapter'; 