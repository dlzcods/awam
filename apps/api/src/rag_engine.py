import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from sentence_transformers import CrossEncoder
from . import config, utils

class RAGEngine:
    def __init__(self):
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set.")
            
        if config.LLM_PROVIDER == "groq":
            if not config.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not set but LLM_PROVIDER is 'groq'")
            
            from langchain_groq import ChatGroq
            print(f"DEBUG: Using Groq LLM ({config.GROQ_MODEL})")
            self.llm = ChatGroq(
                model=config.GROQ_MODEL,
                api_key=config.GROQ_API_KEY,
                temperature=0.7
            )
        else:
            print(f"DEBUG: Using Gemini LLM ({config.LLM_MODEL})")
            self.llm = ChatGoogleGenerativeAI(
                model=config.LLM_MODEL,
                google_api_key=config.GOOGLE_API_KEY,
                temperature=0.7
            )
        
        # Use model2vec static embeddings (very fast)
        from .embeddings import Model2VecEmbeddings
        self.embeddings = Model2VecEmbeddings(config.EMBEDDING_MODEL)
        
        try:
            self.vectorstore = FAISS.load_local(
                config.INDEX_PATH, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"Index not found or error loading: {e}. Please run ingestion first.")
            self.vectorstore = None

        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def initial_retrieval(self, query, top_k=3):
        """Hop 1: Rough retrieval."""
        if not self.vectorstore:
            return []
        
        docs = self.vectorstore.similarity_search(query, k=top_k)
        return docs

    def reformulate_query(self, original_query, context_docs):
        """Uses LLM to reformulate query based on retrieved docs."""
        if not context_docs:
            return original_query
            
        context_text = utils.format_docs_with_metadata(context_docs)
        
        template = """
        Role: Ahli Hukum Senior.
        Tugas: Reformulasi pertanyaan awam menjadi QUERY PENCARIAN HUKUM baku.

        Aturan:
        1. Gunakan istilah hukum baku (contoh: "bikin usaha" -> "perizinan berusaha", "piscok" -> "usaha mikro/makanan").
        2. JANGAN ubah topik spesifik user menjadi contoh lain dari konteks (misal: "piscok" JANGAN jadi "toko kelontong" mentang-mentang ada di referensi).
        3. Jika pertanyaan spesifik, generalisir ke kategori hukumnya (misal: "jualan gorengan" -> "UMKM Sektor Kuliner").
        4. Output HANYA pertanyaan yang direformulasi.

        Konteks Awal (Sebagai referensi istilah saja):
        {context_text}

        Pertanyaan User: {original_query}

        Output: Query baku saja.
        """
        prompt = PromptTemplate(
            input_variables=["context_text", "original_query"],
            template=template
        )
        
        chain = prompt | self.llm
        response = chain.invoke({
            "context_text": context_text,
            "original_query": original_query
        })
        
        import re
        content = response.content
        cleaned_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        
        return cleaned_content

    def final_retrieval_and_rerank(self, formulated_query, top_k_initial=15, top_k_final=8):
        """Hop 2: Retrieve with new query and Rerank."""
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

    def generate_answer(self, query, final_docs):
        """Generates the final answer."""
        context_text = utils.format_docs_with_metadata(final_docs)
        
        template = """
        Role: Asisten Hukum AI yang Deskriptif dan Tuntas.
        Instruksi: Jawab pertanyaan user secara LENGKAP berdasarkan referensi.

        ATURAN PENTING:
        1. PERHATIKAN Detail Prosedural: Jika jawaban melibatkan kewajiban (seperti izin usaha atau pendaftaran), JELASKAN syarat, langkah-langkah, dan prosedurnya secara rinci jika informasinya tersedia dalam referensi. Jangan hanya menyebut "wajib punya izin".
        2. Prioritaskan aturan terbaru (Perhatikan Tanggal Terbit).
        3. Sebutkan Dasar Hukum (Pasal/UU) yang spesifik.
        4. JANGAN menyertakan teks metadata mentah.
        5. JANGAN membuat kalimat penutup meta.

        Dokumen Referensi:
        {context_text}

        Pertanyaan: {query}
        """
        prompt = PromptTemplate(
            input_variables=["context_text", "query"],
            template=template
        )
        
        chain = prompt | self.llm
        response = chain.invoke({
            "context_text": context_text,
            "query": query
        })
        
        import re
        content = response.content
        cleaned_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        
        return cleaned_content

    def process_query(self, user_query):
        """Pipeline execution."""
        start_time = time.time()
        
        # 1. Hop 1
        print("--- Hop 1: Initial Retrieval ---")
        initial_docs = self.initial_retrieval(user_query)
        print(f"DEBUG: Found {len(initial_docs)} docs in Hop 1")
        
        # 2. Reformulate
        print("--- Reformulating Query ---")
        new_query = self.reformulate_query(user_query, initial_docs)
        print(f"DEBUG: Reformulated Query: {new_query}")
        
        # 3. Hop 2 & Rerank
        print("--- Hop 2: Final Retrieval & Rerank ---")
        final_docs = self.final_retrieval_and_rerank(new_query)
        print(f"DEBUG: Found {len(final_docs)} final docs")
        for i, d in enumerate(final_docs[:3]):
            print(f"DEBUG: Top Doc {i+1}: {d.metadata.get('title', 'No Title')}")
        
        # 4. Generate
        print("--- Generating Answer ---")
        answer = self.generate_answer(user_query, final_docs)
        
        # 5. Extract References (Deduplicated)
        references = []
        seen_urls = set()
        for d in final_docs:
            url = d.metadata.get("link", "#")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            ref = {
                "title": d.metadata.get("title", "Unknown Title"),
                "url": url,
                "publish_date": d.metadata.get("publish_date", "Unknown Date"),
                "theme": d.metadata.get("theme", "General")
            }
            references.append(ref)

        execution_time = round(time.time() - start_time, 2)
        print(f"--- Pipeline Finished in {execution_time}s ---")

        return {
            "original_query": user_query,
            "reformulated_query": new_query,
            "final_docs": final_docs,
            "answer": answer,
            "references": references,
            "execution_time": execution_time
        }
