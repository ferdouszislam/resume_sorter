from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
import os
import time
import traceback


def convert_pdfs_to_markdown(pdf_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    print("Loading models... This may take a while on first run.")

    # Retry logic for model loading
    max_retries = 3
    for attempt in range(max_retries):
        try:
            converter = PdfConverter(artifact_dict=create_model_dict())
            print("Models loaded successfully!")
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            traceback.print_exc()
            if attempt < max_retries - 1:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise e

    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    print(f"Found {len(pdf_files)} PDF files to convert")

    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        print(f"Converting {i}/{len(pdf_files)}: {pdf_file}")

        try:
            rendered = converter(pdf_path)
            markdown, _, _ = text_from_rendered(rendered)
            output_file = os.path.join(output_dir, os.path.splitext(pdf_file)[0] + ".md")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown)
            print(f"✓ Successfully converted: {pdf_file}")

        except Exception as e:
            print(f"✗ Error converting {pdf_file}: {e}")
            traceback.print_exc()
            continue

    print("Conversion process completed!")
