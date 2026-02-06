import re

def extract_candidate_info(message: str, current_info: dict) -> dict:
    """
    Extract candidate information from their message using pattern matching.
    Handles all-at-once format like: 'jane gw@kk.in 1234567896 2 frontend delhi react'
    """
    updated_info = current_info.copy()
    
    # Clean up the message
    message_clean = message.strip()
    print(f"DEBUG: message_clean = '{message_clean}'")
    
    # Email extraction using regex
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, message_clean)
    if email_match:
        print(f"DEBUG: Found email: {email_match.group()}")
        if not updated_info.get("email"):
            updated_info["email"] = email_match.group()
            # Remove email from message for further processing
            message_clean = message_clean.replace(email_match.group(), ' ')
    else:
        print("DEBUG: No email found")
    
    # Phone extraction using regex (10+ digit numbers)
    phone_pattern = r'\b(\d{10,})\b'
    phone_match = re.search(phone_pattern, message_clean)
    if phone_match:
        print(f"DEBUG: Found phone: {phone_match.group(1)}")
        if not updated_info.get("phone"):
            updated_info["phone"] = phone_match.group(1)
            # Remove phone from message for further processing
            message_clean = message_clean.replace(phone_match.group(), ' ')
    else:
        print("DEBUG: No phone found")
    
    # Years of experience extraction (single or double digit number followed by optional 'years')
    exp_patterns = [
        r'\b(\d{1,2})\s*(?:\+)?\s*years?\b',
        r'\bexperience[:\s]+(\d{1,2})\b',
        r'\b(\d{1,2})\s*yrs?\b',
        r'\b(\d{1,2})\b'  # Standalone small number (likely years)
    ]
    for pattern in exp_patterns:
        exp_match = re.search(pattern, message_clean.lower())
        if exp_match:
            print(f"DEBUG: Found experience candidate with pattern '{pattern}': {exp_match.group(1)}")
            if not updated_info.get("years_of_experience"):
                years = exp_match.group(1)
                if int(years) <= 50:  # Reasonable years of experience
                    updated_info["years_of_experience"] = years
                    # Remove from message
                    message_clean = re.sub(r'\b' + years + r'\b', ' ', message_clean, count=1)
                    break
    
    # Split remaining message into words
    words = message_clean.split()
    print(f"DEBUG: Remaining words: {words}")
    
    # Try to extract name (first 1-3 words that look like names - no digits, not tech terms)
    tech_keywords = ['react', 'node', 'python', 'java', 'javascript', 'typescript', 'angular', 
                    'vue', 'django', 'flask', 'spring', 'docker', 'kubernetes', 'aws', 'sql',
                    'postgresql', 'mongodb', 'redis', 'frontend', 'backend', 'fullstack',
                    'developer', 'engineer', 'senior', 'junior', 'lead', 'manager']
    
    name_words = []
    remaining_words = []
    for i, word in enumerate(words):
        word_lower = word.lower().strip()
        # Skip empty or single char words
        if len(word_lower) < 2:
            continue
        # If it looks like a name (no digits, not a tech term, appears early)
        if (not any(c.isdigit() for c in word) and 
            word_lower not in tech_keywords and 
            len(name_words) < 3 and
            i < 4):
            name_words.append(word)
        else:
            remaining_words.append(word)
    
    print(f"DEBUG: Name words found: {name_words}")
    if name_words and not updated_info.get("full_name"):
        updated_info["full_name"] = ' '.join(name_words).title()
    
    # From remaining words, try to identify position, location, tech stack
    remaining_text = ' '.join(remaining_words).lower()
    
    # Position keywords
    position_keywords = ['frontend', 'backend', 'fullstack', 'full stack', 'devops', 'developer', 
                       'engineer', 'senior', 'junior', 'lead', 'manager', 'architect', 'qa', 
                       'tester', 'data', 'ml', 'ai', 'mobile', 'ios', 'android', 'web']
    
    # Check for position
    for word in remaining_words:
        if word.lower() in position_keywords and not updated_info.get("desired_positions"):
            # Find related position words
            pos_words = [w for w in remaining_words if w.lower() in position_keywords]
            updated_info["desired_positions"] = ' '.join(pos_words).title()
            print(f"DEBUG: Found position: {updated_info['desired_positions']}")
            break
    
    # Tech stack - common technologies
    tech_stack_keywords = ['react', 'node', 'nodejs', 'python', 'java', 'javascript', 'typescript',
                          'angular', 'vue', 'django', 'flask', 'spring', 'docker', 'kubernetes',
                          'aws', 'azure', 'gcp', 'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
                          'graphql', 'rest', 'express', 'next', 'nextjs', 'nuxt', 'svelte',
                          'tailwind', 'css', 'html', 'go', 'golang', 'rust', 'c++', 'cpp', 'c#',
                          'ruby', 'rails', 'php', 'laravel', 'swift', 'kotlin', 'flutter', 'dart']
    
    tech_found = []
    for word in remaining_words:
        if word.lower() in tech_stack_keywords:
            tech_found.append(word.title())
    
    if tech_found and not updated_info.get("tech_stack"):
        updated_info["tech_stack"] = ', '.join(tech_found)
        print(f"DEBUG: Found tech stack: {updated_info['tech_stack']}")
    
    # Location - try to identify city names (what's left after removing tech and position)
    location_candidates = [w for w in remaining_words 
                          if w.lower() not in tech_stack_keywords 
                          and w.lower() not in position_keywords
                          and len(w) > 2
                          and not any(c.isdigit() for c in w)]
    
    if location_candidates and not updated_info.get("current_location"):
        updated_info["current_location"] = ' '.join(location_candidates).title()
        print(f"DEBUG: Found location: {updated_info['current_location']}")
    
    return updated_info

# Test Case
message = "jane gw@kk.in 1234567896 2 frontend delhi react"
current_info = {}
print(f"\n--- Testing message: '{message}' ---")
result = extract_candidate_info(message, current_info)
print("\n--- Result ---")
print(result)
