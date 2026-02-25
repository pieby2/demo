import streamlit as st
import os
import requests

# Use environment variable for the backend URL if deployed, otherwise use localhost
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
API_URL = f"{BACKEND_URL}/ask"

st.set_page_config(page_title="Titanic Chatbot", page_icon="🚢", layout="centered")

with st.sidebar:
    st.header("⚙️ Configuration")
    user_api_key = st.text_input("Google Gemini API Key", type="password", help="Enter your Gemini API key here. Get one at Google AI Studio.")
    if not user_api_key:
        st.warning("Please enter your API Key to use the chatbot.")

st.title("🚢 Titanic Dataset Explorer")
st.write('Ask me anything about the Titanic passengers! E.g. "Show me a histogram of passenger ages"')

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("plot_url"):
            st.image(f"{BACKEND_URL}{message['plot_url']}")

# React to user input
if prompt := st.chat_input("Ask a question about the Titanic...", disabled=not user_api_key):
    # Display user message in chat message container
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            try:
                payload = {"query": prompt}
                if user_api_key:
                    payload["api_key"] = user_api_key
                    
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                }
                response = requests.post(API_URL, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer provided.")
                    plot_url = data.get("plot_url")
                    
                    st.markdown(answer)
                    if plot_url:
                        st.image(f"{BACKEND_URL}{plot_url}")
                        
                    st.session_state.messages.append({"role": "assistant", "content": answer, "plot_url": plot_url})
                else:
                    st.error(f"Error from API: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the backend API. Is the FastAPI server running?")
