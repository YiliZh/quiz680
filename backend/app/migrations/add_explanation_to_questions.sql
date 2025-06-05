-- Add explanation column to questions table
ALTER TABLE public.questions
ADD COLUMN explanation TEXT;

-- Add comment to explain the column's purpose
COMMENT ON COLUMN public.questions.explanation IS 'Detailed explanation of why the answer is correct'; 