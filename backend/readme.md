## How to start it
```
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload

   python -m uvicorn app.main:app --reload --log-level debug

```

## Run PostgreSQL:
```
    docker-compose -f docker-compose.windows.yml up -d
```

## Run migrations (once Alembic is set up):
```
alembic init migrations
   alembic upgrade head
```

## Dump database
```
   pg_dump -U postgres -h localhost -p 5432 -d quiz2 --schema-only -f C:\cims\code\yl\quiz680\docs\quiz2_0603.sql
   123456
```


## Question Generation Techniques and Workflow
a) Text Processing Pipeline:
```
Input Text → Split into Sentences → Clean Sentences → Calculate Embeddings
```
b) Key Steps:
Text Preprocessing:
Split text into sentences
Filter out short sentences
Use sentence embeddings to identify important content
Question Generation Strategies:
Multiple Choice Questions (MCQs)
True/False Questions
Short Answer Questions
For Each Question Type:
Extract relevant context
Generate question using T5 model
Parse and validate response
Format and store question
c) Technical Components:
T5 Model: For generating questions and answers
SentenceTransformer: For semantic understanding and importance scoring
Custom parsing logic: For extracting structured data from model outputs
About the "Legacy Behaviour" Warning
This warning is related to the T5Tokenizer from the Hugging Face Transformers library. Let me explain:
a) What it means:
The T5Tokenizer has two modes of operation: legacy and new
The legacy mode is the original behavior
The new mode was introduced to fix some tokenization issues
b) Why it appears:
The warning appears because we're using the default (legacy) behavior
It's not an error, just an informational message
The legacy behavior is still valid and works fine for our use case
c) Should we change it?:
For our current implementation, the legacy behavior is sufficient
The new behavior might be more accurate in some cases but requires careful testing
Unless we're experiencing specific tokenization issues, we can safely ignore this warning
If you want to remove the warning, we could modify the code to explicitly set the legacy parameter. Would you like me to show you how to do that?
Also, would you like me to explain any specific part of the question generation process in more detail? For example:
How the key concept extraction works
How we determine important sentences
How the T5 model generates questions
How we validate and parse the generated questions

Calculate Average Embedding → Compute Similarities → Select Top Concepts

Calculate Pairwise Similarities → Score Importance → Select Top Sentences

For each sentence:
- Generate question with T5
- Parse and validate response
- Format and store question