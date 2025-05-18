import streamlit as st
import requests

# --- KONFIGURASI ---
OPENROUTER_APIKEY = "" # Ganti dengan API Key OpenRouter
MODEL = "deepseek/deepseek-chat-v3-0324"
API_URL = "https://openrouter.ai/api/v1/chat/completions"


HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_APIKEY}",
    "HTTP-Referer": "http://localhost:8501",
    "X-Title": "Chatbot"
}

# --- UI STREAMLIT ---
st.set_page_config(page_title="Chatbot", page_icon="🤖")
st.title("🤖 Chatbot")
st.markdown(f"Powered by `{MODEL}` via [OpenRouter](https://openrouter.ai)")

# --- HISTORY CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan history chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- INPUT USER ---
user_input = st.chat_input("Tanyakan sesuatu...")

if user_input:
    # Tampilkan input user
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Kirim ke API OpenRouter
    with st.spinner("Thinking..."):
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                *st.session_state.messages  # Kirim semua history
            ]
        }

        try:
            response = requests.post(API_URL, headers=HEADERS, json=payload)
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"]

            st.chat_message("assistant").write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Gagal mendapatkan jawaban: {e}")
