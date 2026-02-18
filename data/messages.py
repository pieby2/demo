"""
Just a simple in-memory list of messages to test our similarity search.
We categorize them so we can test the filtering feature later.
"""

# Categories
GREETINGS = "greetings"
TECH_SUPPORT = "tech_support"
PRODUCT_INFO = "product_inquiries"
COMPLAINTS = "complaints"

# Our "database" of messages
# Format: list of dicts with 'text' and 'category'
MESSAGES = [
    # --- Greetings ---
    {"text": "Hello, how are you?", "category": GREETINGS},
    {"text": "Good morning, can you help me?", "category": GREETINGS},
    {"text": "Hi there!", "category": GREETINGS},
    {"text": "Hey, what's up?", "category": GREETINGS},
    {"text": "Good evening, I have a quick question.", "category": GREETINGS},
    {"text": "Hi, nice to meet you!", "category": GREETINGS},
    {"text": "Hello! Is anyone available to chat?", "category": GREETINGS},
    {"text": "Good afternoon, hope you're doing well.", "category": GREETINGS},
    {"text": "Hey there, could you spare a moment?", "category": GREETINGS},

    # --- Tech Support stuff ---
    {"text": "I need help with my account.", "category": TECH_SUPPORT},
    {"text": "How do I reset my password?", "category": TECH_SUPPORT},
    {"text": "My app is not working.", "category": TECH_SUPPORT},
    {"text": "I'm having trouble logging into my account.", "category": TECH_SUPPORT},
    {"text": "Can you help me update my profile information?", "category": TECH_SUPPORT},
    {"text": "The website keeps crashing when I try to upload a file.", "category": TECH_SUPPORT},
    {"text": "I forgot my username, how can I recover it?", "category": TECH_SUPPORT},
    {"text": "Two-factor authentication is not sending me a code.", "category": TECH_SUPPORT},
    {"text": "My account got locked after too many login attempts.", "category": TECH_SUPPORT},

    # --- Product / Pricing ---
    {"text": "What features does the premium plan include?", "category": PRODUCT_INFO},
    {"text": "How much does the subscription cost?", "category": PRODUCT_INFO},
    {"text": "Can I upgrade my plan?", "category": PRODUCT_INFO},
    {"text": "Do you offer a free trial before purchasing?", "category": PRODUCT_INFO},
    {"text": "What payment methods do you accept?", "category": PRODUCT_INFO},
    {"text": "Is there a student discount available?", "category": PRODUCT_INFO},
    {"text": "Can I get a refund if I'm not satisfied?", "category": PRODUCT_INFO},
    {"text": "What's the difference between the basic and pro plans?", "category": PRODUCT_INFO},
    {"text": "Do you have an enterprise solution for large teams?", "category": PRODUCT_INFO},

    # --- Complaints :( ---
    {"text": "I'm not satisfied with the service.", "category": COMPLAINTS},
    {"text": "This product is not working as expected.", "category": COMPLAINTS},
    {"text": "I want to cancel my subscription.", "category": COMPLAINTS},
    {"text": "Your customer support is very slow.", "category": COMPLAINTS},
    {"text": "I was charged twice for the same order.", "category": COMPLAINTS},
    {"text": "The quality of the product has gone down recently.", "category": COMPLAINTS},
    {"text": "I've been waiting for a response for over a week.", "category": COMPLAINTS},
    {"text": "This is the worst experience I've ever had with a service.", "category": COMPLAINTS},
]


def get_all_messages():
    return MESSAGES

def get_categories():
    # Helper to get unique categories sorted
    return sorted({m["category"] for m in MESSAGES})

def get_messages_by_category(category):
    return [m for m in MESSAGES if m["category"] == category]
