import os
import sys
import json
import time
import pandas as pd

# Note: We must insert root into path to import modules correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up TWO levels to reach project root (src/evaluation -> src -> root)
root_dir = os.path.dirname(os.path.dirname(current_dir))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.rag_engine import RAGEngine
from src import config

def generate_evaluation_dataset():
    print("--- RAG Response Generation for Manual Review ---")
    
    cache_file = os.path.join(root_dir, 'ragas_input.json')
    
    questions = []
    answers = []
    contexts = []

    if os.path.exists(cache_file):
        print(f"\n[CACHE] Found existing data at {cache_file}")
        print("Skipping Generation Phase. Loading cached answers...")
        with open(cache_file, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)
            questions = data_dict['question']
            answers = data_dict['answer']
            contexts = data_dict['contexts']
    else:
        print("\n[GENERATOR] No cache found. Initializing RAG Engine to generate answers...")
        engine = RAGEngine()
        
        raw_data_path = os.path.join(root_dir, 'data', 'eval_datasets', 'evaluation_dataset.json')
        with open(raw_data_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        print(f"Starting Generation Loop for {len(raw_data)} questions (with 5s safety delay)...")
        
        for i, item in enumerate(raw_data):
            q = item['question']
            print(f"[{i+1}/{len(raw_data)}] Processing: {q[:40]}...")
            
            try:
                result = engine.process_query(q)
                
                questions.append(q)
                answers.append(result['answer'])
                
                ctx_texts = [doc.page_content for doc in result['final_docs']]
                contexts.append(ctx_texts)
                
                time.sleep(5) 
                
            except Exception as e:
                print(f"Error processing {q}: {e}")
                questions.append(q)
                answers.append("Error generating answer.")
                contexts.append(["Error retrieving context."])
        
        print(f"\n[CACHE] Saving generated answers to {cache_file}...")
        cache_data = {
            'question': questions,
            'answer': answers,
            'contexts': contexts
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

    # 3. Export to CSV for Manual Review
    print("\n[EXPORT] Converting to CSV for manual evaluation...")
    
    # helper to sanitize text for CSV (prevent breaking rows)
    def clean_text(text):
        if isinstance(text, str):
            # Replace actual newlines with literal '\n' to prevent CSV row breaking
            return text.replace('\n', '\\n').replace('\r', '')
        return text

    # Flatten contexts and sanitize all fields
    clean_questions = [clean_text(q) for q in questions]
    clean_answers = [clean_text(a) for a in answers]
    
    formatted_contexts = []
    for ctx_list in contexts:
        # Join with a separator, then sanitize
        combined = " || ".join(ctx_list)
        formatted_contexts.append(clean_text(combined))

    df = pd.DataFrame({
        'Question': clean_questions,
        'RAG_Answer': clean_answers,
        'Retrieved_Contexts': formatted_contexts
    })
    
    output_csv = os.path.join(root_dir, 'rag_manual_evaluation.csv')
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"SUCCESS: Dataset saved to: {output_csv}")

if __name__ == "__main__":
    generate_evaluation_dataset()
