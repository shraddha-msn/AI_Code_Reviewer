import os
import httpx
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Setup the Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_working_model():
    """Finds the correct model name for your account."""
    print("--- Searching for available models ---")
    try:
        # The new SDK uses a simple list()
        models = client.models.list()
        for m in models:
            # We look for the flash model
            if "flash" in m.name:
                print(f"Found candidate: {m.name}")
                return m.name
    except Exception as e:
        print(f"Error listing models: {e}")
    
    # Fallback to the absolute standard name if listing fails
    return "gemini-1.5-flash"

def fetch_github_file(repo_url):
    raw_url = repo_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    response = httpx.get(raw_url)
    return response.text

def get_code_review(code, model_name):
    prompt = f"""
    You are a senior software engineer. Review this code for bugs and quality.
    Return ONLY a JSON object with these keys: 
    "score" (1-10), "bugs" (list of strings), "improvements" (list of strings).
    
    Code:
    {code}
    """
    
    # Passing the model name we found
    response = client.models.generate_content(
        model=model_name, 
        contents=prompt
    )
    return response.text

if __name__ == "__main__":
    # 1. Dynamically find the right model name
    active_model = get_working_model()
    print(f"Using model: {active_model}\n")
    
    target_url = "https://github.com/psf/requests/blob/main/src/requests/api.py"
    
    print("Step 1: Fetching code...")
    try:
        code_content = fetch_github_file(target_url)
        
        print("Step 2: Analyzing code...")
        review = get_code_review(code_content, active_model)
        
        print("\n--- CODE REVIEW RESULT ---")
        print(review)
    except Exception as e:
        print(f"\nAn error occurred: {e}")