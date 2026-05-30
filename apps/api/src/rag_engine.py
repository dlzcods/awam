import os
import time
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from sentence_transformers import CrossEncoder
from . import config, utils

# ── Prompts ───────────────────────────────────────────────────────────────

REFORMULATION_SYSTEM = """\
Role: Ahli Hukum Senior.
Tugas: Reformulasi pertanyaan awam menjadi QUERY PENCARIAN HUKUM baku.
Aturan:
1. Gunakan istilah hukum baku (contoh: "bikin usaha" -> "perizinan berusaha").
2. JANGAN ubah topik spesifik user menjadi contoh lain dari konteks.
3. Jika pertanyaan spesifik, generalisir ke kategori hukumnya.
4. Output HANYA pertanyaan yang direformulasi, tanpa penjelasan tambahan."""

REFORMULATION_USER_TEMPLATE = """\
Konteks Awal (Sebagai referensi istilah saja):
{context_text}

Pertanyaan User: {original_query}"""

GENERATION_SYSTEM = """\
Role: Penasihat hukum AI yang adaptif. Kamu menyesuaikan gaya jawaban dengan jenis pertanyaan, bukan mengikuti template baku.

PRINSIP:
1. PAHAMI DULU. Sebelum menjawab, pikirkan: apa kekhawatiran penanya yang tidak terucap? Apa yang sebenarnya mereka butuhkan — penjelasan, prosedur, perbandingan, atau analisis? Jawab kebutuhan itu, bukan cuma pertanyaan literalnya.

2. JELASKAN SEPERTI MANUSIA. Gunakan bahasa Indonesia natural. Kalau ada istilah hukum, langsung jelaskan dalam kalimat yang sama. Analogi dan contoh nyata sangat dianjurkan.

3. BERI KONTEKS, BUKAN CUMA ATURAN. Jangan cuma sebut "Pasal X mengatur Y" — jelaskan kenapa aturan itu ada, apa logika di baliknya, dan bagaimana dampaknya di dunia nyata. Kalau ada celah hukum, pengecualian, atau perdebatan, sebutkan.

4. HUBUNGKAN TITIK-TITIK. Kalau ada beberapa referensi yang saling terkait, jangan sajikan sebagai poin terpisah. Jelaskan hubungannya.

5. PRAKTIS TAPI FLEKSIBEL. Kalau pertanyaannya memang butuh langkah konkret, berikan. Tapi kalau pertanyaannya teoritis, jangan paksakan.

6. Kamu TIDAK BOLEH melakukan perhitungan matematika. Jelaskan rumusnya saja, biarkan pembaca yang menghitung sendiri.

7. JANGAN gunakan format LaTeX (seperti $\rightarrow$). Gunakan karakter panah biasa (→) atau kata seperti "lalu", "kemudian", "selanjutnya".

8. PENTING: Kamu TIDAK PERLU menulis marka sitasi seperti [1], [2]. Tulis penjelasan hukum secara natural seperti manusia menjelaskan ke manusia. Sistem akan menambahkan sitasi secara otomatis setelahnya.

9. GUNAKAN PARAGRAF. Pisahkan ide atau langkah yang berbeda dengan baris kosong. Jawaban dengan paragraf yang terstruktur JAUH lebih mudah dibaca daripada satu blok teks panjang."""

GENERATION_USER_TEMPLATE = """\
Dokumen Referensi:
{context_text}

Pertanyaan: {query}

"""



# ── Engine ─────────────────────────────────────────────────────────────────

def _clean_tex(text: str) -> str:
    """Strip LaTeX artifacts that LLMs sometimes output (e.g. $\\rightarrow$)."""
    import re
    text = re.sub(r'\$\\rightarrow\$', '→', text)
    text = re.sub(r'\$\\leftarrow\$', '←', text)
    text = re.sub(r'\$\\Rightarrow\$', '→', text)
    text = re.sub(r'\$[^$]+\$', '', text)
    return text


def split_indo_sentences(text: str) -> list[str]:
    """Split Indonesian text into sentences.
    Handles abbreviations (No., UU., a.n., dll., dsb., Dr.) correctly.
    Works on Python 3.10+ (no variable-width lookbehind)."""
    import re

    # Known abbreviations that end with a dot but are not sentence boundaries
    abbrevs = {
        'No', 'no', 'Dr', 'dr', 'UU', 'a.n', 'dll', 'dsb', 'dst',
        'ybs', 'sda', 'tsb', 'Yth', 'Prof', 'Ir', 'H', 'Bpk', 'Ibu', 'Sdr',
    }

    # Replace abbreviation dots with placeholder, split, then restore
    placeholder = '\x00DOT\x00'

    def hide_abbrev(m):
        word = m.group(1)
        # Mask: known abbreviations AND numbered sections (1., 2., etc.)
        if word in abbrevs or word.isdigit():
            return word + placeholder
        return m.group(0)

    text_masked = re.sub(r'(\b\w{1,3})\.', hide_abbrev, text)
    raw = re.split(r'[.!?]\s+', text_masked)
    sentences = [s.replace(placeholder, '.') for s in raw]
    return [s.strip() for s in sentences if s.strip()]


def auto_cite(answer: str, documents, embeddings, threshold: float = 0.7) -> str:
    """
    Post-process: attach [N] citations to each sentence based on semantic
    similarity with source documents. Preserves paragraph structure.
    """
    if not documents:
        return answer

    # Strip any existing [N] citations the LLM may have output
    import re
    clean = re.sub(r'\s*\[\d+\]', '', answer)

    # Process paragraph by paragraph to preserve structure
    paragraphs = clean.split('\n\n')
    cited_paragraphs = []

    doc_texts = [d.page_content for d in documents]
    doc_embeddings = embeddings.embed_documents(doc_texts)

    import numpy as np

    def normalize(v):
        v = np.array(v, dtype=np.float32)
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    doc_embeddings = np.array([normalize(e) for e in doc_embeddings])

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        sentences = split_indo_sentences(para)

        # If paragraph has bullets/numbers but split didn't separate them
        # (no periods between items), split by newline instead
        if len(sentences) <= 1 and '\n' in para and re.search(r'(?:^|\n)\s*[*\-]|\d{1,2}[.)]', para):
            sentences = [s.strip() for s in para.split('\n') if s.strip()]

        if len(sentences) <= 1:
            is_structural = len(para) < 50 or para.startswith('**') or re.match(r'\d{1,2}\s', para)
            if is_structural:
                cited_paragraphs.append(para)
                continue

            # Single-sentence paragraph: cite the whole thing
            sent_emb = np.array(embeddings.embed_query(para), dtype=np.float32)
            sent_emb = normalize(sent_emb)
            scores = np.dot(doc_embeddings, sent_emb)
            best_idx = int(np.argmax(scores))
            best_score = float(scores[best_idx])
            if best_score >= threshold:
                cited_paragraphs.append(f"{para} [{best_idx + 1}]")
            else:
                cited_paragraphs.append(para)
            continue

        cited_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or sentence.isdigit():
                continue

            # Deterministic: don't cite structural/heading sentences
            is_structural = (
                len(sentence) < 50                    # Short headers/transitions
                or sentence.startswith('**')          # Markdown bold heading
                or re.match(r'\d{1,2}\s', sentence)   # Numbered sections ("1 Text")
            )

            if is_structural:
                cited_sentences.append(sentence)
                continue

            sent_emb = np.array(embeddings.embed_query(sentence), dtype=np.float32)
            sent_emb = normalize(sent_emb)
            scores = np.dot(doc_embeddings, sent_emb)
            best_idx = int(np.argmax(scores))
            best_score = float(scores[best_idx])

            if best_score >= threshold:
                cited_sentences.append(f"{sentence} [{best_idx + 1}]")
            else:
                cited_sentences.append(sentence)

        cited_paragraphs.append("\n".join(cited_sentences))

    return "\n\n".join(cited_paragraphs)


class RAGEngine:
    def __init__(self):
        provider = config.LLM_PROVIDER

        if provider == "gemini":
            if not config.GEMINI_API_KEY:
                raise ValueError("LLM_PROVIDER=gemini but GEMINI_API_KEY not set.")
            import google.genai as genai
            print(f"DEBUG: Using Gemini LLM ({config.GEMINI_MODEL})")
            self._gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)
            self._is_gemini = True
        else:
            if not config.GROQ_API_KEY:
                raise ValueError("LLM_PROVIDER=groq but GROQ_API_KEY not set.")
            from langchain_groq import ChatGroq
            print(f"DEBUG: Using Groq LLM ({config.GROQ_MODEL})")
            self.llm_reformulate = ChatGroq(
                model=config.GROQ_MODEL, api_key=config.GROQ_API_KEY,
                temperature=0.7, max_tokens=4096,
            )
            self.llm_generate = ChatGroq(
                model=config.GROQ_MODEL, api_key=config.GROQ_API_KEY,
                temperature=0.3, max_tokens=4096,
            )
            self._is_gemini = False

        from .embeddings import MultilingualE5Embeddings
        self.embeddings = MultilingualE5Embeddings(config.EMBEDDING_MODEL)

        try:
            self.vectorstore = FAISS.load_local(
                config.INDEX_PATH, self.embeddings,
                allow_dangerous_deserialization=True,
            )
        except Exception as e:
            print(f"Index not found: {e}. Run ingestion first.")
            self.vectorstore = None

        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    # ── Retrieval ──────────────────────────────────────────────────────

    def initial_retrieval(self, query, top_k=3):
        if not self.vectorstore:
            return []
        return self.vectorstore.similarity_search(query, k=top_k)

    def final_retrieval_and_rerank(self, formulated_query, top_k_initial=10, top_k_final=3):
        if not self.vectorstore:
            return []
        docs = self.vectorstore.similarity_search(formulated_query, k=top_k_initial)
        if not docs:
            return []
        doc_texts = [d.page_content for d in docs]
        pairs = [[formulated_query, text] for text in doc_texts]
        scores = self.reranker.predict(pairs)
        doc_score_pairs = list(zip(docs, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in doc_score_pairs[:top_k_final]]

    # ── Reformulation ──────────────────────────────────────────────────

    def reformulate_query(self, original_query, context_docs):
        if not context_docs:
            return original_query
        context_text = utils.format_docs_with_metadata(context_docs)

        if self._is_gemini:
            return self._reformulate_gemini(original_query, context_text)
        else:
            return self._reformulate_groq(original_query, context_text)

    def _reformulate_gemini(self, original_query, context_text):
        from google.genai import types
        contents = REFORMULATION_USER_TEMPLATE.format(
            context_text=context_text, original_query=original_query,
        )
        response = self._gemini_client.models.generate_content(
            model=config.GEMINI_MODEL,
            config=types.GenerateContentConfig(
                system_instruction=REFORMULATION_SYSTEM,
                temperature=0.7,
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL",),
                max_output_tokens=4096,
            ),
            contents=contents,
        )
        return _clean_tex(response.text.strip())

    def _reformulate_groq(self, original_query, context_text):
        template = REFORMULATION_SYSTEM + "\n\n" + REFORMULATION_USER_TEMPLATE
        prompt = PromptTemplate(
            input_variables=["context_text", "original_query"], template=template,
        )
        chain = prompt | self.llm_reformulate
        response = chain.invoke({
            "context_text": context_text, "original_query": original_query,
        })
        import re
        return _clean_tex(re.sub(r' thinking.*? response', '', response.content, flags=re.DOTALL).strip())

    # ── Generation ─────────────────────────────────────────────────────

    def generate_answer(self, query, final_docs):
        context_text = utils.format_docs_with_metadata(final_docs)

        if self._is_gemini:
            raw = self._generate_gemini(query, context_text)
        else:
            raw = self._generate_groq(query, context_text)

        # Auto-cite: attach [N] based on semantic similarity
        cited = auto_cite(raw, final_docs, self.embeddings)
        return cited

    def _generate_gemini(self, query, context_text):
        from google.genai import types
        contents = GENERATION_USER_TEMPLATE.format(
            context_text=context_text, query=query,
        )
        response = self._gemini_client.models.generate_content(
            model=config.GEMINI_MODEL,
            config=types.GenerateContentConfig(
                system_instruction=GENERATION_SYSTEM,
                temperature=0.3,
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL",),
                max_output_tokens=4096,
            ),
            contents=contents,
        )
        return _clean_tex(response.text.strip())

    def _generate_groq(self, query, context_text):
        template = GENERATION_SYSTEM + "\n\n" + GENERATION_USER_TEMPLATE
        prompt = PromptTemplate(
            input_variables=["context_text", "query"], template=template,
        )
        chain = prompt | self.llm_generate
        response = chain.invoke({
            "context_text": context_text, "query": query,
        })
        import re
        return _clean_tex(re.sub(r' thinking.*? response', '', response.content, flags=re.DOTALL).strip())

    # ── Full pipeline ──────────────────────────────────────────────────

    def process_query(self, user_query):
        start_time = time.time()

        print("--- Hop 1: Initial Retrieval ---")
        initial_docs = self.initial_retrieval(user_query)
        print(f"DEBUG: Found {len(initial_docs)} docs in Hop 1")

        print("--- Reformulating Query ---")
        new_query = self.reformulate_query(user_query, initial_docs)
        print(f"DEBUG: Reformulated: {new_query}")

        print("--- Hop 2: Final Retrieval & Rerank ---")
        final_docs = self.final_retrieval_and_rerank(new_query)
        print(f"DEBUG: Found {len(final_docs)} final docs")

        deduped_docs = []
        seen_urls = set()
        for d in final_docs:
            url = d.metadata.get("link", "")
            if url and url in seen_urls:
                continue
            seen_urls.add(url)
            deduped_docs.append(d)
        print(f"DEBUG: {len(deduped_docs)} unique articles after dedup")

        print("--- Generating Answer ---")
        answer = self.generate_answer(user_query, deduped_docs)

        references = []
        for d in deduped_docs:
            references.append({
                "title": d.metadata.get("title", "Unknown Title"),
                "url": d.metadata.get("link", "#"),
                "publish_date": d.metadata.get("publish_date", "Unknown Date"),
                "theme": d.metadata.get("theme", "General"),
            })

        execution_time = round(time.time() - start_time, 2)
        print(f"--- Pipeline Finished in {execution_time}s ---")

        return {
            "original_query": user_query,
            "reformulated_query": new_query,
            "final_docs": deduped_docs,
            "answer": answer,
            "references": references,
            "execution_time": execution_time,
        }