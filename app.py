import streamlit as st
import requests
import subprocess

st.title("Nid's AI Chat")

# Auto-detect Ollama models
def get_ollama_models():
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]
        return [line.split()[0] for line in lines if line] or ["llama3.2:latest"]
    except:
        return ["llama3.2:latest"]

# Sidebar
with st.sidebar:
    st.header("Settings")
    models = get_ollama_models()
    model = st.selectbox("Choose Model", models)
    if st.button("Clear Chat"):
        st.session_state.messages = []

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
if prompt := st.chat_input("Ask the AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            response = requests.post(
                "http://localhost:8000/chat",
                json={
                    "model": model,
                    "messages": st.session_state.messages
                },
                stream=True,
                timeout=30
            )
            response.raise_for_status()

            for token in response.iter_content(chunk_size=None, decode_unicode=True):
                if token:
                    full_response += token
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except requests.exceptions.ConnectionError:
            st.error("Backend not running. Run: `uvicorn backend:app --port 8000`")
        except requests.exceptions.Timeout:
            st.error("Ollama is slow or not responding. Check `ollama serve`")
        except Exception as e:
            st.error(f"Error: {e}")