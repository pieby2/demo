"""
TalentScout Hiring Assistant - Main Streamlit Application

A conversational AI chatbot for initial candidate screening in tech recruitment.
Built with Streamlit and Google Gemini.
"""

import streamlit as st
from pathlib import Path
import time

from config import Config
from utils.llm_handler import LLMHandler
from utils.data_handler import DataHandler
from utils.validators import sanitize_input


# Page configuration
st.set_page_config(
    page_title="TalentScout - AI Hiring Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_custom_css():
    """Load custom CSS styling."""
    css_file = Path(__file__).parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Additional inline CSS for elements not easily styled via external CSS
    st.markdown("""
        <style>
        /* Override Streamlit defaults for dark theme */
        .stApp {
            background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        }
        
        /* Ensure text visibility */
        .stMarkdown, .stText, p, span, label {
            color: #e0e0e0 !important;
        }
        
        /* Chat input container */
        .stChatInputContainer {
            background-color: rgba(30, 30, 48, 0.8) !important;
            border-radius: 16px !important;
            padding: 0.5rem !important;
            border: 1px solid rgba(124, 58, 237, 0.3) !important;
        }
        
        /* Logo/Title area */
        .title-container {
            text-align: center;
            padding: 1rem 0 2rem 0;
        }
        
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #00d4ff, #7c3aed, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            color: #888;
            font-size: 1rem;
        }
        
        /* Info badges */
        .info-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: rgba(124, 58, 237, 0.2);
            border-radius: 20px;
            color: #00d4ff;
            font-size: 0.85rem;
            margin: 0.25rem;
        }
        
        /* Sidebar section headers */
        .sidebar-header {
            color: #00d4ff;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid rgba(0, 212, 255, 0.3);
            padding-bottom: 0.5rem;
        }
        
        /* Collected info display */
        .info-item {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            margin: 0.25rem 0;
            border-left: 2px solid #7c3aed;
        }
        
        .info-label {
            color: #888;
            font-size: 0.75rem;
            text-transform: uppercase;
        }
        
        .info-value {
            color: #fff;
            font-size: 0.9rem;
        }
        
        /* Welcome banner */
        .welcome-banner {
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(0, 212, 255, 0.2));
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 2rem;
            border: 1px solid rgba(124, 58, 237, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "candidate_info" not in st.session_state:
        st.session_state.candidate_info = {
            "full_name": "",
            "email": "",
            "phone": "",
            "years_of_experience": "",
            "desired_positions": "",
            "current_location": "",
            "tech_stack": "",
            "_technical_questions_started": False,
            "_tech_question_count": 0
        }
    
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False
    
    if "conversation_ended" not in st.session_state:
        st.session_state.conversation_ended = False
    
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    
    if "provider" not in st.session_state:
        st.session_state.provider = Config.DEFAULT_PROVIDER
    
    if "model" not in st.session_state:
        st.session_state.model = Config.get_default_model(st.session_state.provider)
    
    if "llm_handler" not in st.session_state:
        st.session_state.llm_handler = None
    
    if "data_handler" not in st.session_state:
        st.session_state.data_handler = DataHandler()


def render_sidebar():
    """Render the sidebar with candidate information and API key input."""
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🎯 TalentScout</div>', unsafe_allow_html=True)
        st.markdown("**AI Hiring Assistant**")
        
        st.divider()
        
        # API Key Input Section
        st.markdown('<div class="sidebar-header">🔑 API Configuration</div>', unsafe_allow_html=True)
        
        # Provider selection
        provider_options = {
            "openai": "🤖 OpenAI (GPT-4o, GPT-4)",
            "gemini": "✨ Google Gemini",
            "groq": "⚡ Groq (Llama 3)"
        }
        
        selected_provider = st.selectbox(
            "Select LLM Provider",
            options=list(provider_options.keys()),
            format_func=lambda x: provider_options[x],
            index=list(provider_options.keys()).index(st.session_state.provider),
            help="Choose your preferred AI provider"
        )
        
        # Update provider if changed
        if selected_provider != st.session_state.provider:
            st.session_state.provider = selected_provider
            st.session_state.model = Config.get_default_model(selected_provider)
            st.session_state.llm_handler = None  # Reset handler
            st.rerun()
        
        # Model selection
        model_options = Config.get_model_options(st.session_state.provider)
        if model_options:
            selected_model = st.selectbox(
                "Select Model",
                options=model_options,
                index=model_options.index(st.session_state.model) if st.session_state.model in model_options else 0,
                help=f"Available models for {st.session_state.provider.upper()}"
            )
            if selected_model != st.session_state.model:
                st.session_state.model = selected_model
                st.session_state.llm_handler = None
        
        # API key links per provider
        api_key_links = {
            "openai": "[Get OpenAI API key →](https://platform.openai.com/api-keys)",
            "gemini": "[Get Gemini API key →](https://makersuite.google.com/app/apikey)",
            "groq": "[Get Groq API key →](https://console.groq.com/keys)"
        }
        
        api_key_input = st.text_input(
            f"{st.session_state.provider.upper()} API Key",
            type="password",
            value=st.session_state.api_key,
            placeholder=f"Enter your {st.session_state.provider.upper()} API key...",
            help=f"Get your API key from the provider's console"
        )
        
        # Update API key and reinitialize LLM handler if changed
        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input
            if api_key_input:
                st.session_state.llm_handler = LLMHandler(
                    api_key=api_key_input,
                    provider=st.session_state.provider,
                    model=st.session_state.model
                )
                st.toast(f"✅ {st.session_state.provider.upper()} API key updated!")
        
        if st.session_state.api_key:
            st.success(f"✅ {st.session_state.provider.upper()} configured")
        else:
            st.warning("⚠️ Enter API key to start")
            st.markdown(api_key_links.get(st.session_state.provider, ""))
        
        st.divider()
        
        # Status indicator
        if st.session_state.conversation_ended:
            st.success("✅ Screening Complete")
        elif st.session_state.conversation_started:
            st.info("🔄 Screening in Progress")
        else:
            st.info("👋 Ready to Start")
        
        st.divider()
        
        # Collected Information
        st.markdown('<div class="sidebar-header">📋 Candidate Info</div>', unsafe_allow_html=True)
        
        info = st.session_state.candidate_info
        
        # Display collected fields
        fields = [
            ("full_name", "👤 Name"),
            ("email", "📧 Email"),
            ("phone", "📱 Phone"),
            ("years_of_experience", "📅 Experience"),
            ("desired_positions", "💼 Position"),
            ("current_location", "📍 Location"),
            ("tech_stack", "💻 Tech Stack")
        ]
        
        collected_count = 0
        for field_key, field_label in fields:
            value = info.get(field_key, "")
            if value:
                collected_count += 1
                st.markdown(f"""
                    <div class="info-item">
                        <div class="info-label">{field_label}</div>
                        <div class="info-value">{value}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="info-item" style="opacity: 0.5;">
                        <div class="info-label">{field_label}</div>
                        <div class="info-value">Not provided yet</div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Progress indicator
        st.divider()
        progress = collected_count / len(fields)
        st.progress(progress)
        st.caption(f"{collected_count}/{len(fields)} fields collected")
        
        # Reset button
        st.divider()
        if st.button("🔄 Start New Session", use_container_width=True):
            reset_session()
            st.rerun()


def reset_session():
    """Reset the session state for a new conversation."""
    st.session_state.messages = []
    st.session_state.candidate_info = {
        "full_name": "",
        "email": "",
        "phone": "",
        "years_of_experience": "",
        "desired_positions": "",
        "current_location": "",
        "tech_stack": "",
        "_technical_questions_started": False,
        "_tech_question_count": 0
    }
    st.session_state.conversation_started = False
    st.session_state.conversation_ended = False
    # Reinitialize LLM handler with existing API key
    if st.session_state.api_key:
        st.session_state.llm_handler = LLMHandler(
            api_key=st.session_state.api_key,
            provider=st.session_state.provider,
            model=st.session_state.model
        )


def render_header():
    """Render the main header."""
    st.markdown("""
        <div class="title-container">
            <div class="main-title">🎯 TalentScout</div>
            <div class="subtitle">AI-Powered Hiring Assistant for Tech Recruitment</div>
        </div>
    """, unsafe_allow_html=True)


def render_chat_interface():
    """Render the main chat interface."""
    # Check API configuration
    if not st.session_state.api_key:
        st.markdown("""
            <div class="welcome-banner">
                <h2>🔑 API Key Required</h2>
                <p>Please enter your Gemini API key in the sidebar to get started.</p>
                <p>Don't have one? <a href="https://makersuite.google.com/app/apikey" target="_blank">Get your free API key here →</a></p>
            </div>
        """, unsafe_allow_html=True)
        return
    
    # Welcome message for new sessions
    if not st.session_state.conversation_started:
        st.markdown("""
            <div class="welcome-banner">
                <h2>👋 Welcome to TalentScout!</h2>
                <p>I'm your AI Hiring Assistant, here to help with your initial screening.</p>
                <p>Click the button below to begin your application process.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Start Screening", use_container_width=True):
                start_conversation()
                st.rerun()
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if not st.session_state.conversation_ended:
        if prompt := st.chat_input("Type your response here..."):
            process_user_input(prompt)
    else:
        st.info("📝 This screening session has ended. Click 'Start New Session' in the sidebar to begin again.")


def start_conversation():
    """Initialize a new conversation with the greeting."""
    st.session_state.conversation_started = True
    
    # Check if LLM handler is properly initialized
    if st.session_state.llm_handler is None:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "⚠️ Error: Please enter your API key in the sidebar first."
        })
        return
    
    # Get initial greeting from LLM
    try:
        greeting = st.session_state.llm_handler.start_conversation()
    except Exception as e:
        greeting = f"⚠️ Error starting conversation: {str(e)}"
    
    # Add to message history
    st.session_state.messages.append({
        "role": "assistant",
        "content": greeting
    })


def process_user_input(user_input: str):
    """Process user input and generate response."""
    # Sanitize input
    sanitized_input = sanitize_input(user_input)
    
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": sanitized_input
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(sanitized_input)
    
    # Extract any information from the message
    extracted_info = st.session_state.llm_handler.extract_candidate_info(
        sanitized_input,
        st.session_state.candidate_info
    )
    print(f"DEBUG: Input: '{sanitized_input}'")
    print(f"DEBUG: Extracted Info: {extracted_info}")
    
    # Check if we should rerun to update sidebar
    should_rerun = False
    if extracted_info != st.session_state.candidate_info:
        should_rerun = True
        st.session_state.candidate_info = extracted_info
        print(f"DEBUG: Updated Session State: {st.session_state.candidate_info}")
    
    # Update candidate info based on context (legacy hook)
    update_candidate_info_from_context(sanitized_input)
    
    if should_rerun:
        st.rerun()
    
    # Check if LLM handler is properly initialized
    if st.session_state.llm_handler is None:
        with st.chat_message("assistant"):
            st.error("⚠️ Please enter your API key in the sidebar first.")
        return
    
    # Get LLM response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response, is_ended = st.session_state.llm_handler.send_message(
                    sanitized_input,
                    st.session_state.candidate_info
                )
            except Exception as e:
                response = f"⚠️ Error: {str(e)}"
                is_ended = False
        
        st.markdown(response)
    
    # Add assistant message to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
    
    # Handle conversation end
    if is_ended:
        st.session_state.conversation_ended = True
        save_candidate_data()


def update_candidate_info_from_context(user_input: str):
    """
    Update candidate information based on conversation context.
    Note: Most extraction is now handled by llm_handler.extract_candidate_info().
    This function is kept for any additional context-based updates.
    """
    # The comprehensive extraction is now done in llm_handler.extract_candidate_info()
    # This function is kept as a hook for any additional processing if needed
    pass


def save_candidate_data():
    """Save candidate data when conversation ends."""
    try:
        session_id = st.session_state.data_handler.save_candidate(
            st.session_state.candidate_info,
            st.session_state.messages
        )
        st.toast(f"✅ Data saved successfully! Session ID: {session_id[:8]}...")
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")


def main():
    """Main application entry point."""
    # Load custom styles
    load_custom_css()
    
    # Initialize session
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    render_header()
    
    # Chat interface
    render_chat_interface()
    
    # Footer
    st.divider()
    st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
            <p>🔒 Your data is handled in compliance with GDPR standards.</p>
            <p>TalentScout AI Hiring Assistant v1.0 | Powered by OpenAI, Gemini & Groq</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
