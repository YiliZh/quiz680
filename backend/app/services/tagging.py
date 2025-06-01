from keybert import KeyBERT
from typing import List

kw_model = KeyBERT("all-MiniLM-L6-v2")

def extract_tags(text: str, top_n: int = 8) -> List[str]:
    keywords = kw_model.extract_keywords(text, top_n=top_n)
    return [k for k, _ in keywords] 