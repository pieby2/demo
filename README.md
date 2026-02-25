# Titanic Chatbot 🚢

A friendly chatbot that analyzes the Titanic dataset. Ask questions in plain English and get text answers and visual insights!

## Features
- **Natural Language Questions**: Ask things like "What percentage of passengers were male?"
- **Visualizations**: Request plots like "Show me a histogram of passenger ages".
- **Clean Interface**: Built with Streamlit for an intuitive chat experience.
- **Agentic Backend**: Powered by FastAPI, LangChain, and Google Gemini.

## Requirements
- Python 3.9+ 
- A Google Gemini API Key.

## Setup Instructions

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your API Key**:
   Open the `.env` file and replace `your_api_key_here` with your actual Google Gemini API Key:
   ```
   GEMINI_API_KEY=your_actual_key
   ```

3. **Run the Backend**:
   In a terminal, run:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

4. **Run the Frontend**:
   In a separate terminal, run:
   ```bash
   streamlit run frontend/app.py
   ```

6. Open `http://localhost:8501` in your browser and start chatting!
