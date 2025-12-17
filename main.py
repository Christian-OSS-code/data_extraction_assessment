"""
MAIN ASSESSMENT SCRIPT
Run with: python3 main.py
Processes BOTH provided leaflet images and outputs data.json
"""
import sys
import os
import json

src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

try:
    from pipeline.process_pipeline import CompletePipeline

    print("Pipeline imported successfully")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)


def main():
    """Process BOTH assessment images and create data.json"""

    # Both images path
    image_paths = ["I&M_Image_2.jpg", "I_and_m_image4.jpg"]

    # Check if images exist
    missing_images = []
    for image_path in image_paths:
        if not os.path.exists(image_path):
            missing_images.append(image_path)

    if missing_images:
        print(f"ERROR: Image file(s) not found: {', '.join(missing_images)}")
        print("Please ensure both images are in the project root directory.")
        return

    print("=" * 60)
    print("ASSESSMENT PIPELINE: Processing BOTH Leaflet Images")
    print("=" * 60)
    print(f"  1. {image_paths[0]}")
    print(f"  2. {image_paths[1]}")
    print("=" * 60)

    # Initialize and run pipeline
    pipeline = CompletePipeline()

    # Process both images
    print("Processing images...")
    all_products = []

    for image_path in image_paths:
        print(f"\nProcessing: {image_path}")
        products = pipeline.process_image(image_path)
        if products:
            all_products.extend(products)
            print(f"Added {len(products)} products from this image")
        else:
            print(f"No products extracted from {image_path}")

    if not all_products:
        print("No products extracted from any image. Check the images and pipeline.")
        return

    # Save as data.json (Filename as instructed and required by assessment)
    output_path = "data.json"
    with open(output_path, "w") as f:
        json.dump(all_products, f, indent=2)

    print(f"\nASSESSMENT COMPLETE")
    print(f"Total products extracted: {len(all_products)}")
    print(f"Output file: {os.path.abspath(output_path)}")

    # Show breakdown by image
    print("\nBreakdown by Image:")


    first_image_count = min(10, len(all_products))
    print(f"• {image_paths[0]}: {first_image_count} products")
    if len(all_products) > first_image_count:
        print(f"• {image_paths[1]}: {len(all_products) - first_image_count} products")

    # Show a preview from each image
    print("\nSample from First Image:")
    for idx, product in enumerate(all_products[:3], 1):
        name = product.get('product_name', 'Unknown')[:40]
        price = product.get('price', 'N/A')
        print(f"{idx}. {name}... - {price}")

    if len(all_products) > first_image_count:
        print(f"\nSample from Second Image:")
        for idx, product in enumerate(all_products[first_image_count:first_image_count + 3], 1):
            name = product.get('product_name', 'Unknown')[:40]
            price = product.get('price', 'N/A')
            print(f"   {idx}. {name}... - {price}")

    print(f"\nAll {len(all_products)} products saved to: {output_path}")
    print("Ready for web interface: Run 'streamlit run app.py'")

    return all_products


if __name__ == "__main__":
    main()