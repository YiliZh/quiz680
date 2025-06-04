-- Add processing_logs and has_questions columns to uploads table
ALTER TABLE public.uploads
ADD COLUMN processing_logs text,
ADD COLUMN has_questions boolean DEFAULT false; 