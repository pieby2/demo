import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Titanic Chatbot API")

# Add CORS middleware to allow the Streamlit frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Ensure static directory exists
os.makedirs("backend/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Titanic Chatbot API is running!"}

# Load Titanic Dataset
try:
    df = pd.read_csv("data/titanic.csv")
except Exception as e:
    df = pd.DataFrame()
    print(f"Error loading Titanic dataset: {e}")

# Initialize LLM & Agent
# Make sure GEMINI_API_KEY is in your .env file
try:
    llm_default = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
except Exception as e:
    llm_default = None

INSTRUCTION_PROMPT = """
You are a helpful data analyst analyzing the Titanic dataset.
The dataset is provided as a pandas dataframe (`df`).

When asked a question, provide a clear text answer.
When asked to create a plot or visualization:
1. Create the plot using matplotlib or seaborn.
2. DO NOT use plt.show().
3. Save the plot to exactly this filepath: {filepath}
   Example: plt.savefig('{filepath}')
4. Close the plot with plt.close() after saving.
5. In your final text response, you MUST include the exact string "PLOT: {filename}" so that the frontend can display it.
"""

class QueryRequest(BaseModel):
    query: str
    api_key: str = None  # Optional API key from frontend

@app.post("/ask")
async def ask_question(request: QueryRequest):
    if df.empty:
        raise HTTPException(status_code=500, detail="Titanic dataset not loaded.")
        
    # Determine which LLM to use
    active_llm = llm_default
    if request.api_key:
        try:
             # Initialize a new LLM instance with the provided key
             active_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=request.api_key)
        except Exception as e:
             raise HTTPException(status_code=400, detail=f"Invalid API Key provided: {e}")
             
    if active_llm is None:
         raise HTTPException(status_code=500, detail="LLM not initialized. Please provide a GEMINI_API_KEY in the sidebar.")
         
    try:
        plot_filename = f"plot_{uuid.uuid4().hex}.png"
        plot_filepath = os.path.join("backend", "static", plot_filename)
        # Replacing backslashes for windows paths just in case python/langchain messes up the prompt string
        plot_filepath_str = plot_filepath.replace("\\", "/")
        
        prompt = f"User Query: {request.query}\n\n" + INSTRUCTION_PROMPT.format(filepath=plot_filepath_str, filename=plot_filename)
        
        agent = create_pandas_dataframe_agent(
            active_llm, 
            df, 
            verbose=True, 
            allow_dangerous_code=True, 
            agent_executor_kwargs={"handle_parsing_errors": True}
        )
        response = agent.invoke({"input": prompt})
        text_answer = response.get("output", "")
        
        plot_url = None
        if f"PLOT: {plot_filename}" in text_answer:
            if os.path.exists(plot_filepath):
                plot_url = f"/static/{plot_filename}"
                text_answer = text_answer.replace(f"PLOT: {plot_filename}", "").strip()
            
        return JSONResponse(content={"answer": text_answer, "plot_url": plot_url})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
