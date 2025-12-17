import os
import json
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from agents.llm_agent import LLMExtractionAgent
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import...")
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "llm_agent",
        os.path.join(src_dir, "agents", "llm_agent.py")
    )
    llm_agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(llm_agent_module)
    LLMExtractionAgent = llm_agent_module.LLMExtractionAgent

from paddleocr import PaddleOCR


class CompletePipeline:
    def __init__(self):
        """Initialize OCR and LLM components."""
        # Initialize OCR
        try:
            self.ocr_engine = PaddleOCR(use_textline_orientation=True, lang='en')
        except ValueError:
            self.ocr_engine = PaddleOCR(use_angle_cls=False, lang='en')


        self.llm_agent = LLMExtractionAgent()

    def process_image(self, image_path):
        """Process a single image: OCR → LLM → Structured data."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        print(f"📷 Processing: {os.path.basename(image_path)}")

        # Step 1: OCR
        result = self.ocr_engine.predict(image_path)
        if not result:
            return []

        ocr_result = result[0]
        rec_texts = ocr_result.get('rec_texts', [])

        if not rec_texts:
            return []

        # Combine OCR text
        ocr_text = "\n".join(rec_texts)
        print(f"   Extracted {len(rec_texts)} text boxes")

        # Step 2: LLM Structuring
        products = self.llm_agent.extract_products(ocr_text)
        print(f"   Structured into {len(products)} products")

        return products

    def process_multiple_images(self, image_paths):
        """Process multiple images and combine results."""
        all_products = []

        for image_path in image_paths:
            products = self.process_image(image_path)
            all_products.extend(products)

        return all_products

    def save_output(self, products, output_dir="data/output"):
        """Save products to JSON files."""
        os.makedirs(output_dir, exist_ok=True)

        #Save as data.json in PROJECT ROOT (assessment requirement)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels

        # Save to project root
        data_json_path = os.path.join(project_root, "data.json")

        with open(data_json_path, "w") as f:
            json.dump(products, f, indent=2)

        print(f"\n📁 Output saved to:")
        print(f"   • {data_json_path} (✅ ASSESSMENT REQUIREMENT)")

        return data_json_path
def run_complete_pipeline():
    """Run the complete pipeline on assessment images."""

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels

    image_paths = [
        os.path.join(project_root, "I&M_Image_2.jpg"),
        os.path.join(project_root, "I_and_m_image4.jpg")
    ]

    print("=" * 60)
    print("COMPLETE AI PIPELINE: Leaflet Product Extraction")
    print("=" * 60)

    # Initialize and run pipeline
    pipeline = CompletePipeline()
    products = pipeline.process_multiple_images(image_paths)

    print(f"\n✅ PIPELINE COMPLETE")
    print(f"   Total products extracted: {len(products)}")

    # Display summary
    for idx, product in enumerate(products, 1):
        name = product.get('product_name', 'Unknown')
        price = product.get('price', 'N/A')
        weight = product.get('weight_volume', '')
        if weight:
            print(f"   {idx:2d}. {name} ({weight}) - {price}")
        else:
            print(f"   {idx:2d}. {name} - {price}")

    # Save output
    output_path = pipeline.save_output(products)

    print("\n" + "=" * 60)
    print("Ready for frontend/API development.")
    print(f"Products available in: {output_path}")

    return products


if __name__ == "__main__":
    run_complete_pipeline()

