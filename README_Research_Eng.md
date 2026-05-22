# Indonesian Legal RAG System with Query Reformulation (Double-Hop)

This project implements an advanced **Retrieval-Augmented Generation (RAG)** system designed specifically for answering Indonesian legal questions. It utilizes a **"Double-Hop"** method and **Query Reformulation** to improve document retrieval accuracy and answer relevance.

Currently powered by **Qwen 3 32B (via Groq)** for high-speed intelligent reasoning, with **Google Gemini-2.5-Flash** as a robust alternative.

## 🚀 Key Features & Achievements

1.  **Double-Hop Retrieval Logic**: Performs two distinct searches (Context Gathering -> Reformulation -> Precision Search).
2.  **Query Reformulation (Layman -> Legal)**: Uses an LLM to rewrite user's layperson questions (e.g., *"Boss cut my salary unfairly"*) into standardized legal queries.
    *   **Evaluation Result**: Achieved **100% Hit Rate** on stratified layman datasets.
3.  **Cross-Encoder Reranking**: Re-orders search results to ensure the most relevant regulation appears at position #1.
4.  **Interactive UI**: Built with **Streamlit** for a responsive chat experience.
5.  **Cloud Deployment**: Ready for **Modal** serverless deployment.

## 🔄 End-to-End Flow

1.  **Hop 1: Initial Retrieval (Context Gathering)**
    *   Rough search in Vector DB using the raw user query.
2.  **Reasoning & Reformulation**
    *   **Qwen 3 32B** analyzes the context.
    *   Reformulates the layman question into a formal legal query.
3.  **Hop 2: Precision Search**
    *   System searches again using the *Reformulated Query*.
    *   Results are reranked using a local Cross-Encoder model.
4.  **Generation**
    *   **Qwen 3 32B** generates the final answer based on the selected legal documents, citing specific articles and laws.

## 🛠️ Tech Stack

*   **Language**: Python 3.10+
*   **Primary LLM**: **Qwen 3 32B** (via Groq API) - *Fast & Smart*
*   **Alternative LLM**: **Gemini 2.5 Flash** (Google)
*   **Embedding**: Google Text-Embedding-004
*   **Vector Database**: FAISS (CPU)
*   **Frontend**: Streamlit
*   **Deployment**: Modal (Serverless)

## 📂 Project Structure

```text
legal-rag-system/
├── data/
│   ├── hukumonline_sample.json      # Legal dataset
│   └── eval_datasets/               # Evaluation datasets
├── src/
│   ├── evaluation/                  # Evaluation scripts
│   ├── config.py                    # API Configuration
│   ├── ingestion.py                 # Indexing & Metadata Extraction
│   ├── rag_engine.py                # Core Logic (Reformulation + Rerank)
│   ├── generate_eval_data.py        # Evaluation Data Generator (Layman Style)
│   └── evaluation.py                # Evaluation Script (Retrieval Only)
├── app.py                           # Streamlit Frontend
├── main.py                          # CLI Version
├── modal_app.py                     # Modal Deployment Config
└── requirements.txt                 # Python Dependencies
```

## 💻 How to Run

### Prerequisites
*   Python 3.10+
*   API Keys: **Groq API Key** (for Qwen) and **Google API Key** (for Embedding).

### 1. Local Setup (Streamlit)
```powershell
# 1. Clone & Enter Directory
git clone https://github.com/JHIA/query-reformulation-rag.git
cd query-reformulation-rag

# 2. Setup Venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Setup .env
# Create .env file and add:
# GOOGLE_API_KEY=...
# GROQ_API_KEY=...
# LLM_PROVIDER=groq
# GROQ_MODEL=qwen/qwen-2.5-32b-instruct

# 5. Run App
streamlit run app.py
```

### 2. Deployment to Modal (Serverless)
```powershell
# 1. Setup Modal
pip install modal
modal setup

# 2. Upload Volume (Index FAISS)
modal volume create rag-storage
modal volume put -f rag-storage faiss_index data/faiss_index

# 3. Deploy
modal deploy modal_app.py
```

## 📊 Full Evaluation Report

**Date:** December 26, 2025

### 1. Summary
The goal of this test was to answer: **"If a user asks using layman/casual language (curhat), can the system find the correct legal rule?"**

The result is exceptional. Out of 15 tests across different topics, the system found the exact rule **100%** of the time.

### 2. Methodology
We designed a rigorous testing scenario to avoid evaluation bias:
1.  **Question Generation (Dataset Generation)**:
    Using an AI persona of a "Layperson" to generate natural language queries with everyday casual language from 15 different legal categories.

2.  **Retrieval Accuracy Analysis (Hit Rate & MRR)**:
    We assessed document retrieval performance using two key metrics:
    *   **Hit Rate (Recall@K)**: Measures if the relevant legal document was successfully found within the top search results (Top-K).
    *   **MRR (Mean Reciprocal Rank)**: Measures how high the first relevant document ranks, indicating user efficiency in finding answers without deep scrolling.

3.  **Generation Quality Analysis (LLM-as-a-Judge)**:
    We used an LLM-as-a-Judge scenario to evaluate two aspects of answer quality:
    *   **Faithfulness**: Measures if the system's answer is purely derived from the retrieved context (to detect hallucinations).
    *   **Answer Relevancy**: Measures if the answer is relevant and addresses the core of the user's question.

### 3.1 Retrieval Accuracy Assessment (Hit Rate & MRR)
Below are the 15 "Layman Terms" questions tested, including the Query Transformation and performance comparison (AI vs Raw):

| Topic | User Question (Input) | Reformulated Query (AI) | Targeted Document (Answer) | Rank (AI) | Change (vs Raw) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Business** | *"How to get a permit for selling fuel?"* | *"Prosedur dan persyaratan pengurusan izin usaha perdagangan BBM menurut UU Migas"* | Business Licensing for Fuel Trading | **#1** | ➖ Stable |
| **Human Rights** | *"Prisoner bullied in cell, any law protects them?"* | *"Perlindungan hukum terhadap narapidana korban kekerasan/perundungan di Lapas"* | Protection for Prisoners from Bullying | **#1** | ➖ Stable |
| **Legal Science** | *"Diff between legal protection vs law enforcement?"* | *"Perbedaan Konseptual Antara Perlindungan Hukum dan Penegakan Hukum"* | Definition of Legal Protection vs Enforcement | **#1** | ➖ Stable |
| **IPR** | *"My product sold by others without permit, report how?"* | *"Penegakan hukum atas pelanggaran hak distribusi eksklusif (UU 7/2014 Pasal 11)"* | Enforcement on Exclusive Distribution Rights | **#1** | ➖ Stable |
| **Family** | *"Husband says divorce verbally often, is it valid?"* | *"Status Perkawinan Setelah Talak Lisan dalam Hukum Islam & Keabsahannya"* | Marital Status if Divorced Verbally | **#1** | ➖ Stable |
| **State** | *"What are citizen rights in law?"* | *"Hak warga negara dalam bidang hukum (UUD 1945 & UU No. 39/1999)"* | 11 Citizen Rights in Law | **#1** | 🔼 **IMPROVED (2 -> 1)** |
| **Labor** | *"Can underage kids work?"* | *"Ketentuan hukum izin kerja & perlindungan bagi pekerja anak (UU Ketenagakerjaan)"* | Legal Protection for Child Workers | **#1** | 🔼 **IMPROVED (2 -> 1)** |
| **Sports** | *"Rules for foreign soccer players in Indonesia?"* | *"Syarat hukum dan regulasi bagi Pemain Sepak Bola Asing di Liga Indonesia"* | Rules on Foreign Soccer Players | **#2** | 🔻 Declined (1 -> 2) |
| **Civil Law** | *"What is 'Renvoi' in Supreme Court decision?"* | *"Dasar Hukum dan Tata Cara Renvoi Putusan Mahkamah Agung"* | Legal Basis of Renvoi | **#1** | ➖ Stable |
| **Consumer** | *"Clothes lost at laundry, must they compensate?"* | *"Kewajiban ganti rugi pemilik laundry atas hilangnya barang konsumen (UU Perlindungan Konsumen)"* | Laundry Compensation for Lost Items | **#1** | ➖ Stable |
| **Property** | *"Can waqf land be sold again?"* | *"Status hukum peralihan/penjualan tanah wakaf oleh nadhir (UU No. 41/2004)"* | Law on Selling Waqf Land | **#2** | 🔻 Declined (1 -> 2) |
| **Criminal** | *"Requirements for drug rehab?"* | *"Syarat dan Prosedur Permohonan Rehabilitasi Hukum Tersangka Narkoba"* | Requirements for Rehabilitation | **#1** | ➖ Stable |
| **Legal Prof** | *"Are lawyers immune to law?"* | *"Hak imunitas advokat vs tuntutan pidana (UU Advokat)"* | Can Advocates be Criminally Charged? | **#1** | ➖ Stable |
| **Startup** | *"Can startups manage traditional markets?"* | *"Legalitas perusahaan startup mengelola pasar tradisional (Perpres 112/2007)"* | Traditional Market Mgmt by Startups | **#1** | ➖ Stable |
| **Tech/ITE** | *"Is spreading parody songs mocking people illegal?"* | *"Tindakan hukum menyebarkan lagu parodi bermuatan penghinaan (UU ITE & KUHP)"* | Law on Spreading Insulting Songs | **#1** | 🔼 **IMPROVED (2 -> 1)** |

### 3.2 Generation Quality Assessment (LLM-as-a-Judge)
In addition to automated system evaluation, we performed an **LLM-as-a-Judge Simulation** on 15 samples using **Faithfulness** and **Answer Relevancy** criteria.

## 📊 Detail Evaluation Per Sample

### 1. Fuel Trading Business License
> **Pertanyaan:** "Gimana sih caranya ngurus izin kalau mau buka usaha jual beli BBM? Ribet nggak ya?"
>
> *(English: "How do I get a permit if I want to open a fuel trading business? Is it complicated?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* The answer accurately cites GR No. 28/2025 and GR No. 36/2004 from the context. No hallucinated additional info.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* The answer directly responds to the "is it complicated" complaint with an explanation of OSS and risk classification. Very solution-oriented.

### 2. Protection of Prisoners who are Victims of Bullying
> **Pertanyaan:** "Kalau ada napi yang dibully... ada hukum yang ngelindungin mereka nggak sih?"
>
> *(English: "If a prisoner is bullied... is there any law that protects them?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* The answer precisely cites Law No. 22 of 2022 Article 3 letters b and c from the available context.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Directly answers "Yes, there are protection rights", matching the user's intent seeking certainty.

### 3. Legal Protection vs Law Enforcement
> **Pertanyaan:** "Sebenernya apa sih bedanya perlindungan hukum sama penegakan hukum?"
>
> *(English: "What is actually the difference between legal protection and law enforcement?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Definitions are taken exactly from expert opinions (Philipus M. Hadjon, Jimly Asshiddiqie) found in the document. The preventive/repressive difference is explained well.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* The answer structure using a comparison table is very helpful in answering user confusion.

### 4. Violation of Exclusive Distribution Rights
> **Pertanyaan:** "Misal aku punya hak tunggal... ada orang lain ikut jualan tanpa izin, bisa dilaporin pakai hukum apa?"
>
> *(English: "Suppose I have sole rights... someone else sells without permission, what law can I use to report them?")*

- **Faithfulness:** ⭐⭐⭐⭐ (4/5)
  - *Analysis:* The answer mentions criminal sanctions under Article 100 of the Trademark Law. Although there is a legal basis in one document, another document in the context explicitly states *"does not regulate sanctions against unauthorized parties"* (for genuine goods reseller cases). The AI answer failed to capture this nuance of exception, so the score was reduced slightly due to generalization.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Comprehensive answer covering criminal and civil options according to the user's desire to "report".

### 5. Status of Verbal Divorce (Talak)
> **Pertanyaan:** "Suami sering banget bilang talak... cuma lisan doang, status nikahnya cerai beneran atau nggak?"
>
> *(English: "My husband often says talak... only verbally, is the marriage status really divorced or not?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* The answer firmly cites Article 39 of the Marriage Law and KHI stating that divorce is only valid before the court. Very faithful to the document.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Directly calms the user's anxiety with the answer "Marriage Status Remains Valid".

### 6. 11 Citizen Rights
> **Pertanyaan:** "Hak-hak kita di mata hukum itu apa aja sih? Katanya ada 11 ya?"
>
> *(English: "What are our rights in the eyes of the law? I heard there are 11?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* The answer details points 1-11 very neatly according to the document context which indeed discusses those 11 rights. 100% accuracy.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Listicle format (bullet points) is very suitable for this type of question.

### 7. Child Workers
> **Pertanyaan:** "Anak kecil di bawah umur itu sebenernya boleh kerja nggak sih?"
>
> *(English: "Can underage children actually work or not?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* The answer explains the legal nuance correctly: *"Prohibited, BUT there are exceptions (ages 13-15 for light work)"*. This is accurately taken from the Manpower Law in the context.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Answers the doubt "can they or not" with a conditional explanation that is easy to understand.

### 8. Foreign Soccer Players
> **Pertanyaan:** "Pemain bola asing... aturannya gimana?"
>
> *(English: "Foreign soccer players... what are the rules?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Combines info from the Sports Law, Manpower Law, and PSSI Regulations scattered across different chunks into one whole answer. Good synthesis skill.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Relevant, covering work permits (IMTA) and sports regulations.

### 9. Renvoi of Supreme Court Decisions
> **Pertanyaan:** "Maksudnya 'Renvoi' dalam putusan MA itu apa sih?"
>
> *(English: "What does 'Renvoi' mean in a Supreme Court decision?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* The definition of Renvoi as a correction of clerical errors is taken exactly from Perma No. 6 of 2022 in the context.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Explains technical legal terms in language that is not too stiff.

### 10. Laundry Compensation
> **Pertanyaan:** "Kalau baju ilang pas lagi di-laundry, pemilik wajib ganti rugi nggak?"
>
> *(English: "If clothes get lost while at the laundry, is the owner required to compensate?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Cites Article 19 of the Consumer Protection Law regarding the obligation to compensate within 7 days. Very accurate according to the document.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Very pro-consumer according to the user's question, providing concrete steps (BPSK claim).

### 11. Selling Waqf Land
> **Pertanyaan:** "Tanah yang udah diwakafin itu boleh dijual lagi nggak sih?"
>
> *(English: "Can land that has been endowed (waqf) be sold again?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* The answer firmly states **"PROHIBITED"** based on Article 40 of the Waqf Law. Mentions the 5-year criminal sanction (Article 67) found in the context.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Direct answer to the point without beating around the bush.

### 12. Rehabilitation of Drug Suspects
> **Pertanyaan:** "Kalau tersangka narkoba mau minta rehabilitasi, syarat sama prosedurnya gimana?"
>
> *(English: "If a drug suspect wants to request rehabilitation, what are the requirements and procedures?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Explains the Pre-trial procedure (Article 77 KUHAP) and special requirements (assessment) found in the document.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* The procedure flow is explained step-by-step (Submission -> Examination -> Decision 7 days).

### 13. Advocate & Notary Immunity
> **Pertanyaan:** "Pengacara atau notaris itu kebal hukum nggak sih?"
>
> *(English: "Are lawyers or notaries immune to the law?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Distinguishes clearly: Advocates have limited immunity (Article 16 Advocate Law), Notaries **DO NOT** (Notary Office Law). This distinction is taken exactly from the context.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Answers the "immune to law" myth with balanced legal facts.

### 14. Startups Managing Traditional Markets
> **Pertanyaan:** "Bisa nggak sih perusahaan startup gitu ngelola pasar tradisional?"
>
> *(English: "Can startup companies manage traditional markets?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Cites Perpres 112/2007 Article 4 which allows the private sector to manage markets. MSME partnership requirements are also included according to the document.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* The answer "Yes, with conditions..." fits perfectly to answer the user's doubt.

### 15. Insulting Parody Songs
> **Pertanyaan:** "Kalau iseng nyebarin lagu parodi yang isinya ngehina orang, itu bisa kena pasal hukum nggak ya?"
>
> *(English: "If I jokingly spread a parody song that insults people, can I be charged with a law?")*

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Cites Article 27A of the ITE Law (newest 2024) regarding attacking honor. Explains the "intentional" element and 2-year prison sanction according to context.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analysis:* Answers the "joking" concern with an explanation of the "intent" element (mens rea) in criminal law.

### 4. Results & Conclusion

The evaluation in steps 3.1 and 3.2 involved 4 key metrics:

1.  **Faithfulness**: Measures the factual consistency of the system's generated answer against the given context document (to detect hallucinations).
2.  **Answer Relevancy**: Measures the relevance level of the system's answer to the user's query.
3.  **Hit Rate (Recall@K)**: Measures the probability of the system finding at least one relevant document in the top-k search results.
4.  **MRR (Mean Reciprocal Rank)**: Measures the ranking accuracy by giving higher weight if the relevant document appears at the top.

The test results are as follows:

| Metric | Score | Predicate |
| :--- | :--- | :--- |
| **Faithfulness** | **98.6%** | Highly Reliable |
| **Relevancy** | **100%** | Highly Relevant |
| **Hit Rate** | **100%** | Highly Effective |
| **MRR (without reformulation)** | **90%** | High Precision |
| **MRR (with reformulation)** | **93%** | High Precision |

The system demonstrates exceptional maturity in 3 main aspects:

1.  **Context Understanding**: Able to filter relevant information from long and complex document chunks.
2.  **Regulatory Compliance**: Highly compliant with the latest regulations (e.g., correctly citing the 2024 ITE Law).
3.  **User Intent Alignment**: The query reformulation capability proved **successful**. The generated answers truly "connect" with everyday language questions by improving accuracy and ranking precision, effectively bridging the gap between layman language and legal terminology.

---

### 5. Gap Analysis & Limitations
For academic transparency, we note the following limitations:

1.  **Limited Dataset Scope**:
    *   The knowledge base contains only **15 legal categories** with **~50 articles each** (~750 total). The 100% score applies to this specific scope, but broader testing is needed for national-scale deployment.
    
2.  **Data Privacy Risk**:
    *   The system relies on Third-Party APIs (Groq/Google), meaning user queries are sent externally. Not recommended for highly confidential cases without additional encryption or On-Premise models.

3.  **Infrastructure Dependency**:
    *   Fully dependent on Cloud API uptime. If the API involves downtime, the system has no local fallback.
