import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from .agent_prompt import DATA_EXTRACTION_PROMPT


current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
env_path = os.path.join(project_root, '.env')

print(f"Looking for .env file at: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

# Load .env file
load_dotenv(dotenv_path=env_path)

# Debug: Check what was loaded
print(f"OPENAI_API_KEY loaded: {'YES' if os.getenv('OPENAI_API_KEY') else 'NO'}")
if os.getenv('OPENAI_API_KEY'):

    # Show first 10 chars only for security
    key_preview = os.getenv('OPENAI_API_KEY')[:10] + "..."
    print(f"   Key preview: {key_preview}")


class LLMExtractionAgent:
    def __init__(self, api_key=None):
        """Initialize with OpenAI client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            print("❌ DEBUG INFO:")
            print(f"   Project root: {project_root}")
            print(f"   .env path attempted: {env_path}")
            print(f"   File exists: {os.path.exists(env_path)}")
            print(f"   All environment variables: {list(os.environ.keys())}")
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

        print("✅ OpenAI API key loaded successfully")
        self.client = OpenAI(api_key=self.api_key)

    def extract_products(self, raw_ocr_text):
        """Send OCR text to LLM and return structured JSON."""

        prompt = DATA_EXTRACTION_PROMPT.format(raw_text=raw_ocr_text)

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4" for better accuracy
                messages=[
                    {"role": "system", "content": "You are a precise data extraction assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent, structured output
                max_tokens=2000
            )

            # Extract the JSON from the response
            result_text = response.choices[0].message.content.strip()

            if result_text.startswith("```json"):
                result_text = result_text[7:-3]
            elif result_text.startswith("```"):
                result_text = result_text[3:-3]

            # Parse JSON
            products = json.loads(result_text)
            return products

        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Raw response was: {result_text}")
            return []
        except Exception as e:
            print(f"LLM API error: {e}")
            return []


def test_llm_agent():
    """Test the LLM agent with a sample of your OCR text."""


    # Read your combined OCR text
    with open("data/output/combined_ocr_text.txt", "r") as f:
        sample_text = f.read()

    # Use only first 2000 chars for testing to save tokens
    test_text = sample_text[:2000]

    agent = LLMExtractionAgent()
    products = agent.extract_products(test_text)

    print(f"Extracted {len(products)} products:")
    for idx, product in enumerate(products, 1):
        print(f"{idx}. {product.get('product_name')} - {product.get('price')}")

    # Save to JSON file
    with open("data/output/extracted_products.json", "w") as f:
        json.dump(products, f, indent=2)
    print("\nSaved to data/output/extracted_products.json")


if __name__ == "__main__":
    test_llm_agent()