# 🎯 TalentScout - AI Hiring Assistant

An intelligent conversational chatbot for initial candidate screening in tech recruitment. Built with **Streamlit** and powered by **OpenAI**, **Google Gemini**, or **Groq**.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Technical Details](#technical-details)
- [Prompt Design](#prompt-design)
- [Data Privacy & GDPR](#data-privacy--gdpr)
- [Project Structure](#project-structure)
- [Challenges & Solutions](#challenges--solutions)
- [Future Enhancements](#future-enhancements)

## Overview

TalentScout is an AI-powered hiring assistant designed to streamline the initial screening process for technology recruitment. The chatbot conducts natural conversations with candidates, gathering essential information and generating tailored technical questions based on their declared tech stack.

### Key Capabilities

- 🤝 **Friendly Greeting** - Professional welcome with clear process explanation
- 📝 **Information Gathering** - Structured collection of candidate details
- 💻 **Tech Stack Analysis** - Identification and parsing of technologies
- ❓ **Dynamic Question Generation** - 3-5 technical questions per technology
- 🔄 **Context Awareness** - Maintains conversation flow and handles follow-ups
- 🛡️ **Fallback Handling** - Graceful responses for unexpected inputs
- 👋 **Graceful Exit** - Proper conversation closure with next steps

## Features

### Conversation Flow

1. **Greeting Phase** - Introduces the screening process
2. **Information Collection**:
   - Full Name
   - Email Address
   - Phone Number
   - Years of Experience
   - Desired Position(s)
   - Current Location
   - Tech Stack (languages, frameworks, databases, tools)
3. **Technical Assessment** - Generates relevant questions based on declared technologies
4. **Closing** - Thanks the candidate and explains next steps

### UI Features

- Modern dark theme with glassmorphism effects
- Real-time candidate info display in sidebar
- Progress tracking for collected information
- Session management with reset capability
- Responsive design

## Installation

### Prerequisites

- Python 3.9 or higher
- At least one API key from:
  - **OpenAI** ([Get API key](https://platform.openai.com/api-keys))
  - **Google Gemini** ([Get API key](https://makersuite.google.com/app/apikey))
  - **Groq** ([Get API key](https://console.groq.com/keys))

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd assign
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key**
   ```bash
   # Copy the example env file
   copy .env.example .env   # Windows
   cp .env.example .env     # macOS/Linux
   
   # Edit .env and add your API key(s) - you only need one!
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key_here
   # OR Gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   # OR Groq
   GROQ_API_KEY=your_groq_api_key_here
   
   # Set default provider (optional)
   DEFAULT_PROVIDER=groq  # or openai, gemini
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   - Navigate to `http://localhost:8501`

## Usage

1. **Start the Application** - Launch with `streamlit run app.py`
2. **Begin Screening** - Click "Start Screening" on the welcome screen
3. **Respond to Questions** - Answer the chatbot's questions naturally
4. **Technical Assessment** - After providing your tech stack, answer technical questions
5. **End Conversation** - Say "bye", "goodbye", "exit", or "thank you" to conclude

### Exit Keywords

The chatbot recognizes these keywords to end the conversation:
- `bye`, `goodbye`, `exit`, `quit`, `end`, `stop`
- `thank you`, `thanks`, `done`, `finish`, `end conversation`

## Technical Details

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Chat UI    │  │  Sidebar    │  │  Session State      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      Utils Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ LLM Handler  │  │  Validators  │  │  Data Handler    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│               LLM Provider (Select One)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   OpenAI     │  │   Gemini     │  │      Groq        │  │
│  │   GPT-4o     │  │   1.5 Flash  │  │   Llama 3.3     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Libraries Used

| Library | Version | Purpose |
|---------|---------|---------|
| `streamlit` | ≥1.28.0 | Web application framework |
| `openai` | ≥1.0.0 | OpenAI API integration |
| `google-generativeai` | ≥0.3.0 | Gemini API integration |
| `groq` | ≥0.4.0 | Groq API integration |
| `python-dotenv` | ≥1.0.0 | Environment variable management |
| `pydantic` | ≥2.0.0 | Data validation |

### Model Configuration

| Provider | Default Model | Alternatives |
|----------|--------------|---------------|
| OpenAI | `gpt-4o-mini` | `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo` |
| Gemini | `gemini-1.5-flash` | `gemini-1.5-pro`, `gemini-pro` |
| Groq | `llama-3.3-70b-versatile` | `llama-3.1-8b-instant`, `mixtral-8x7b-32768` |

**Common Settings:**
- **Temperature**: 0.7 (balanced creativity/consistency)
- **Max tokens**: 1024

## Prompt Design

### System Prompt Strategy

The chatbot uses a comprehensive system prompt that defines:

1. **Persona** - Professional, friendly AI Hiring Assistant
2. **Responsibilities** - Clear list of tasks to perform
3. **Information Collection Order** - Structured sequence for gathering data
4. **Guidelines** - Rules for natural conversation flow
5. **Off-Topic Handling** - Strategies to redirect conversation

### Key Prompt Engineering Techniques

#### 1. Role-Based Prompting
```
"You are TalentScout's AI Hiring Assistant, a professional and 
friendly chatbot designed to conduct initial candidate screenings 
for technology positions."
```

#### 2. Structured Task Definition
The prompt explicitly lists what information to collect and in what order, ensuring consistent data gathering.

#### 3. Context Injection
Each message includes current state:
```python
context = f"Information already collected:\n{collected}\n"
context += f"Still need to collect: {missing}\n"
```

#### 4. Dynamic Question Generation
Technical questions are calibrated based on experience:
- **0-2 years**: Beginner to intermediate, fundamental concepts
- **2-5 years**: Intermediate, practical problem-solving
- **5+ years**: Advanced, architecture and optimization

#### 5. Guardrails
The prompt includes explicit instructions to:
- Stay on topic
- Handle off-topic inputs gracefully
- Maintain professional tone
- Ask one question at a time

## Data Privacy & GDPR

### Compliance Measures

1. **Data Minimization** - Only essential information collected
2. **Consent** - Users informed about data collection
3. **Retention Limits** - 90-day automatic data expiration
4. **Right to Erasure** - `delete_candidate_data()` function available
5. **Anonymization** - Email/phone partially masked in logs
6. **Local Storage** - Data stored locally in JSON (gitignored)

### Security Features

- Sensitive data files excluded from git
- Input sanitization to prevent injection
- No external data transmission (except to selected LLM provider)

## Project Structure

```
assign/
├── app.py                  # Main Streamlit application
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md               # This documentation
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore rules
├── utils/
│   ├── __init__.py         # Package initialization
│   ├── llm_handler.py      # Multi-provider LLM integration
│   ├── prompts.py          # Prompt templates
│   ├── validators.py       # Input validation
│   └── data_handler.py     # Data storage & GDPR
├── data/
│   └── candidates.json     # Candidate data (gitignored)
└── assets/
    └── styles.css          # Custom CSS styling
```

## Challenges & Solutions

### 1. Context Management
**Challenge**: Maintaining conversation context across multiple exchanges.

**Solution**: Implemented context injection that includes:
- Already collected information
- Missing fields
- Dynamic prompt augmentation based on conversation state

### 2. Information Extraction
**Challenge**: Accurately extracting structured data from natural language.

**Solution**: Combined approach:
- Regex patterns for email, phone, experience
- Context-based heuristics (analyzing last assistant message)
- LLM inference for remaining fields

### 3. Tech Stack Diversity
**Challenge**: Generating relevant questions for any technology combination.

**Solution**: Dynamic prompt generation that:
- Calibrates difficulty based on experience
- Instructs LLM to focus on specific technologies
- Requests 3-5 questions per technology

### 4. Off-Topic Handling
**Challenge**: Keeping conversation focused on recruitment.

**Solution**: System prompt includes:
- Explicit off-topic handling instructions
- Polite redirection templates
- Professional acknowledgment patterns

### 5. UI/UX Design
**Challenge**: Creating an engaging interface with Streamlit's constraints.

**Solution**: Custom CSS with:
- Glassmorphism effects
- Gradient accents
- Dark theme optimized for extended use
- Inline styles for elements not accessible via CSS

## Future Enhancements

### Planned Features

- [ ] **Sentiment Analysis** - Gauge candidate emotions during conversation
- [ ] **Multilingual Support** - Support for multiple languages
- [ ] **Resume Parsing** - Extract info from uploaded resumes
- [ ] **Interview Scheduling** - Integration with calendar APIs
- [ ] **Analytics Dashboard** - Insights on candidate metrics

### Performance Optimizations

- [ ] Response streaming for faster perceived performance
- [ ] Caching for repeated technical questions
- [ ] Async API calls for better concurrency

### Deployment Options

- [ ] Docker containerization
- [ ] Cloud deployment (GCP, AWS, Azure)
- [ ] CI/CD pipeline setup

---

## License

This project is licensed under the MIT License.

## Author

Developed as part of a technical assessment for AI-powered recruitment solutions.

---

<p align="center">
  <strong>🎯 TalentScout</strong><br>
  <em>AI-Powered Hiring Assistant</em>
</p>
