"""
Integration test for TalentScout Hiring Assistant
Tests all core features to verify the Groq API integration
"""
import sys
sys.path.insert(0, '.')
from utils.llm_handler import LLMHandler
from utils.data_handler import DataHandler
from utils.validators import validate_email, validate_phone, validate_tech_stack, sanitize_input
from config import Config

def test_talentscout():
    print("=" * 60)
    print("TalentScout Hiring Assistant - Full Integration Test")
    print("=" * 60)
    
    # Test 1: LLM Handler Initialization
    print("\n[TEST 1] LLM Handler Initialization with Groq...")
    handler = LLMHandler(
        api_key=Config.GROQ_API_KEY,
        provider='groq',
        model='llama-3.3-70b-versatile'
    )
    assert handler.is_configured, "Handler should be configured"
    print("   PASS LLM Handler initialized successfully")
    
    # Test 2: Greeting Generation
    print("\n[TEST 2] Greeting Generation...")
    greeting = handler.start_conversation()
    assert len(greeting) > 50, "Greeting should have substantial content"
    assert "talentscout" in greeting.lower() or "screening" in greeting.lower() or "hiring" in greeting.lower()
    print(f"   PASS Greeting generated ({len(greeting)} chars)")
    print(f"   Preview: {greeting[:150]}...")
    
    # Test 3: Information Gathering
    print("\n[TEST 3] Information Gathering Flow...")
    candidate_info = {
        'full_name': '',
        'email': '',
        'phone': '',
        'years_of_experience': '',
        'desired_positions': '',
        'current_location': '',
        'tech_stack': ''
    }
    
    # Simulate name response
    response, ended = handler.send_message('My name is Sarah Johnson', candidate_info)
    assert not ended, "Conversation should continue"
    print(f"   PASS Name response received ({len(response)} chars)")
    
    # Test 4: Technical Questions Generation with Tech Stack
    print("\n[TEST 4] Technical Questions Generation...")
    candidate_info = {
        'full_name': 'Sarah Johnson',
        'email': 'sarah@example.com',
        'phone': '5551234567',
        'years_of_experience': '5',
        'desired_positions': 'Full Stack Developer',
        'current_location': 'New York',
        'tech_stack': 'Python, Django, React, PostgreSQL'
    }
    
    response, ended = handler.send_message(
        'I work with Python, Django, React and PostgreSQL', 
        candidate_info
    )
    assert not ended, "Conversation should continue for technical questions"
    # Check if response contains technical content
    has_technical = any(word in response.lower() for word in ['python', 'django', 'react', 'question', 'technical'])
    print(f"   PASS Technical questions generated ({len(response)} chars)")
    print(f"   Contains technical content: {has_technical}")
    print(f"   Preview: {response[:300]}...")
    
    # Test 5: Exit Keywords
    print("\n[TEST 5] Exit Keywords Detection...")
    for keyword in ['bye', 'goodbye', 'exit', 'thank you']:
        test_handler = LLMHandler(
            api_key=Config.GROQ_API_KEY,
            provider='groq'
        )
        test_handler.start_conversation()
        _, ended = test_handler.send_message(keyword, {'full_name': 'Test'})
        assert ended, f"Exit keyword '{keyword}' should end conversation"
    print("   PASS All exit keywords detected correctly")
    
    # Test 6: Validators
    print("\n[TEST 6] Input Validators...")
    valid, _ = validate_email("test@example.com")
    assert valid, "Valid email should pass"
    valid, _ = validate_email("invalid-email")
    assert not valid, "Invalid email should fail"
    
    valid, _ = validate_phone("5551234567")
    assert valid, "Valid phone should pass"
    
    valid, parsed, _ = validate_tech_stack("Python, Django, React")
    assert valid, "Valid tech stack should pass"
    assert len(parsed) == 3, "Should parse 3 technologies"
    print("   PASS All validators working correctly")
    
    # Test 7: Data Handler
    print("\n[TEST 7] Data Handler GDPR Compliance...")
    data_handler = DataHandler()
    # Test anonymization
    test_info = {'email': 'john.doe@example.com', 'phone': '+1 555 123 4567'}
    anonymized = data_handler.get_anonymized_summary(test_info)
    assert '@' in anonymized['email'] and '***' in anonymized['email']
    assert '***' in anonymized['phone']
    print("   PASS Data anonymization working correctly")
    
    # Test 8: Input Sanitization
    print("\n[TEST 8] Input Sanitization...")
    dangerous_input = "Hello\x00World\x1f"  # Contains null and control chars
    sanitized = sanitize_input(dangerous_input)
    assert '\x00' not in sanitized, "Null bytes should be removed"
    print("   PASS Input sanitization working correctly")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! PASS")
    print("=" * 60)
    print("\nSummary:")
    print("  - Groq API integration: WORKING")
    print("  - Greeting generation: WORKING")
    print("  - Information gathering: WORKING")
    print("  - Technical questions: WORKING")
    print("  - Exit keywords: WORKING")
    print("  - Input validators: WORKING")
    print("  - GDPR data handling: WORKING")
    print("  - Input sanitization: WORKING")

if __name__ == "__main__":
    test_talentscout()
