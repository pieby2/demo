"""Script to list available models for different LLM providers."""
import sys


def list_openai_models(api_key: str):
    """List available OpenAI models."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        print("\n🤖 OpenAI Available Models:")
        print("-" * 50)
        
        # List common chat models
        common_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
        models = client.models.list()
        
        for model in models.data:
            if any(cm in model.id for cm in common_models):
                print(f"  {model.id}")
                
    except Exception as e:
        print(f"Error listing OpenAI models: {e}")


def list_gemini_models(api_key: str):
    """List available Gemini models."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        print("\n✨ Google Gemini Available Models:")
        print("-" * 50)
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  {model.name}")
                
    except Exception as e:
        print(f"Error listing Gemini models: {e}")


def list_groq_models(api_key: str):
    """List available Groq models."""
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        print("\n⚡ Groq Available Models:")
        print("-" * 50)
        
        models = client.models.list()
        for model in models.data:
            print(f"  {model.id}")
            
    except Exception as e:
        print(f"Error listing Groq models: {e}")


def main():
    """Main function to list models for selected provider."""
    print("\n🎯 TalentScout - LLM Model Lister")
    print("=" * 50)
    
    print("\nSelect provider:")
    print("1. OpenAI")
    print("2. Google Gemini")
    print("3. Groq")
    print("4. All providers")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        api_key = input("Enter your OpenAI API key: ")
        list_openai_models(api_key)
    elif choice == "2":
        api_key = input("Enter your Gemini API key: ")
        list_gemini_models(api_key)
    elif choice == "3":
        api_key = input("Enter your Groq API key: ")
        list_groq_models(api_key)
    elif choice == "4":
        openai_key = input("Enter your OpenAI API key (or press Enter to skip): ")
        gemini_key = input("Enter your Gemini API key (or press Enter to skip): ")
        groq_key = input("Enter your Groq API key (or press Enter to skip): ")
        
        if openai_key:
            list_openai_models(openai_key)
        if gemini_key:
            list_gemini_models(gemini_key)
        if groq_key:
            list_groq_models(groq_key)
    else:
        print("Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    main()
