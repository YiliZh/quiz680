# PDF‑to‑Quiz Pipeline – Technology Reality vs Roadmap

*Updated for tech‑stack accuracy – June 4 2025*

---

## 1  Executive Snapshot

Your current codebase already converts **PDFs → chapter objects → database rows → auto‑generated questions**.
Below we separate the **libraries that already exist in your repo** from **suggested upgrades** so your presentation is crystal‑clear.

---

## 2  Workflow Diagram (unchanged)

```mermaid
flowchart LR
    A[PDF Upload] --> B[Text Extraction\n(PyPDF2 / pdfplumber)]
    B --> C[Chapter Segmentation\n(Regex →  Semantic)]
    C --> D[Summarisation\n(Prototype / LLM)]
    D --> E[Keyword Tagging\n(KeyBERT)]
    E --> F[Embeddings &  Analysis\n(Sentence‑Transformers)]
    F --> G[Question Generation\n(Rule engine)]
    G --> H[Persist → PostgreSQL]
    H --> I[Quiz API & React UI]
```

*Grey boxes in the live demo represent code you already have; dashed outlines (if you add them on slides) can mark future upgrades.*

---

## 3  Technology Matrix – **What’s In / What’s Next**

| # | Pipeline Goal         | **Libraries Already in Repo**                                       | **Recommended Upgrades**                          | Key Algorithm / Rationale                           |
| - | --------------------- | ------------------------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------- |
| 1 | PDF upload & metadata | **FastAPI**, **SQLAlchemy**                                         | —                                                 | REST upload ➜ DB provenance                         |
| 2 | Text extraction       | **PyPDF2**, **pdfplumber**                                          | `unstructured`, Tesseract OCR (scanned)           | Vector glyph → Unicode mapping                      |
| 3 | Chapter detection     | Custom **regex** inside `pdf.py`                                    | **HDBSCAN** on MiniLM embeddings                  | Move from string heuristics → semantic segmentation |
| 4 | Summarisation         | Simple first‑paragraph slice (`extract_summary`)                    | **Mistral‑7B** / GPT via LangChain                | Abstractive map‑reduce for concision                |
| 5 | Keyword tagging       | **KeyBERT** (`tagging.py`)                                          | **spaCy NER** merge                               | Maximal Marginal Relevance diversifies tags         |
| 6 | Content embeddings    | **Sentence‑Transformers** (`all‑MiniLM‑L6‑v2`)                      | —                                                 | Cosine similarity, k‑means ranking                  |
| 7 | Question generation   | Rule‑based engine in `question_generator.py`, **NumPy**, **random** | GPT‑4o Chain‑of‑Thought OR fine‑tuned **T5‑base** | Bloom‑aligned MCQ templates → LLM for fluency       |
| 8 | Persistence           | **SQLAlchemy**, **PostgreSQL**                                      | —                                                 | Normalised schema (Upload ↔ Chapter ↔ Question)     |
| 9 | Quiz delivery         | FastAPI routes (not shown), React front‑end stubs                   | JWT auth, Remix/Next.js UI                        | `/quiz/{chapter_id}` serves JSON MCQs               |

Legend: **Bold** = confirmed in repo imports; *italics* = optional; empty cell = no upgrade required yet.

---

## 4  Speaker‑Note Highlights

### 4.1  What’s working today (✅)

* Accurate text extraction with PyPDF2 / pdfplumber.
* Keyword tagging via KeyBERT & MiniLM.
* Question generation without external APIs – runs offline.

### 4.2  Highest‑impact next steps (🚀)

1. **Semantic segmentation** – replace brittle regex with embedding clustering.
2. **Abstractive summaries** – reduces prompt cost, improves question quality.
3. **LLM‑powered Q‑gen** – switchable adapter layer (GPT‑4o or fine‑tuned T5).

---

## 5  Code‑Module Map (quick ref)

| Module                          | Uses                                           |
| ------------------------------- | ---------------------------------------------- |
| `pdf.py`                        | PyPDF2, regex segmentation, keyword extraction |
| `extractor.py`                  | pdfplumber proof‑of‑concept                    |
| `tagging.py`                    | KeyBERT                                        |
| `question_generator.py`         | Sentence‑Transformers, NumPy, torch            |
| `quiz.py` / `quiz_generator.py` | ORM + placeholder quiz API                     |

---

*Prepared by ChatGPT‑o3 – aligning slide content with your actual repo, June 4 2025*
