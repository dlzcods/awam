import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("MODAL_API_URL", "") 

st.set_page_config(
    page_title="HukumOnline RAG Assistant",
    page_icon="⚖️",
    layout="centered"
)

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #2e6c80;
        color: white;
    }
    .ref-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    .ref-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .ref-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .ref-title {
        font-weight: bold;
        color: #2e6c80;
        text-decoration: none;
        display: block;
        margin-bottom: 0.5rem;
    }
    .ref-meta {
        font-size: 0.8rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ Asisten Hukum Online")
st.caption("Powered by Query Reformulation & RAG")

if not API_URL:
    st.warning("⚠️ MODAL_API_URL is not set. Please deploy the backend and set the URL in .env")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "execution_time" in message:
            st.caption(f"⏱️ Waktu pemrosesan: {message['execution_time']} detik")
        if "references" in message and message["references"]:
            st.markdown("### 📚 Referensi")
            for ref in message["references"]:
                title = ref.get('title', 'No Title')
                url = ref.get('url', '#')
                date = ref.get('publish_date', '')[:10]
                st.markdown(f"- **[{title}]({url})** \n  *{date}* | `{ref.get('theme', 'General')}`")

if prompt := st.chat_input("Apa pertanyaan hukum Anda?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not API_URL:
            st.error("Cannot process query: API URL missing.")
            st.stop()
            
        try:
            with st.spinner("Sedang menghubungi ahli hukum digital..."):
                response = requests.post(f"{API_URL}", json={"query": prompt}, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                with st.expander("🔍 Analisis Query (Reformulasi)"):
                    st.markdown(f"**Query Asli:** {data.get('original_query', prompt)}")
                    st.markdown(f"**Query Hukum:** {data.get('reformulated_query', 'N/A')}")
                
                answer_text = data.get("answer", "Maaf, tidak dapat menghasilkan jawaban.")
                exec_time = data.get("execution_time", 0)
                
                st.markdown(answer_text)
                st.caption(f"⏱️ Waktu pemrosesan: {exec_time} detik")
                
                refs = data.get("references", [])
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer_text,
                    "references": refs,
                    "execution_time": exec_time
                })

                refs = data.get("references", [])
                if refs:
                    st.markdown("### 📚 Referensi")
                    for ref in refs:
                        title = ref.get('title', 'No Title')
                        url = ref.get('url', '#')
                        date = ref.get('publish_date', '')[:10]
                        st.markdown(f"- **[{title}]({url})** \n  *{date}* | `{ref.get('theme', 'General')}`")
                    
            else:
                st.error(f"Error API: {response.status_code} - {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("Gagal terhubung ke Server API. Pastikan API backend berjalan.")
        except Exception as e:
            st.error(f"Terjadi kesalahan tak terduga: {e}")
