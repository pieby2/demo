# Message Similarity Finder 🔍

Hey there! This is a simple Python tool I built to find similar messages using cosine similarity. It takes your input, converts it into a vector (using `sentence-transformers` locally), and finds the best matches from our hardcoded list of messages.

No external APIs needed—everything runs right on your machine.

## How it Works
1. **Embeddings**: We use the `all-MiniLM-L6-v2` model to turn text into numbers (vectors).
2. **Comparison**: We calculate the cosine similarity between your input vector and our message vectors.
3. **ranking**: We just sort them by score and show you the top ones.

## Getting Started

### Prerequisites
You'll need Python 3.8+ installed.

### Setup
1. Clone the repo.
2. Create a virtual env (recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The first time you run it, it'll download the model ~80MB. Subsequent runs are instant.)*

## Usage

You can run it in interactive mode:
```bash
python main.py
```

Or pass your query directly:
```bash
python main.py "locked out of my account"
```

### Options
* `--top` or `-k`: How many results you want (default is 3).
* `--category` or `-c`: Filter by category (e.g., `tech_support`, `greetings`).
* `--add`: Add a temporary message to the list for testing.

### Examples

**Basic search:**
```bash
python main.py "hey how are you"
```

**Filter by category:**
```bash
python main.py "pricing" -c product_inquiries
```

**Show top 5 results:**
```bash
python main.py "not working" -k 5
```

## Project Structure
* `main.py`: The entry point. Handles the CLI and prints results.
* `data/messages.py`: Contains our hardcoded list of messages.
* `embeddings/`: Helper class to load the model and generate embeddings.
* `utils/`: Math stuff (cosine similarity logic).
