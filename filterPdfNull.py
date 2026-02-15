import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(os.getcwd())

def prepare_pdf_dataset(input_file, output_file="filtered_pdf_without_nullpdf.json"):
    input_path = os.path.join(BASE_DIR, input_file)
    output_path = os.path.join(BASE_DIR, output_file)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    filtered = [
        item for item in data
        if item.get("pdf_link") and item.get("pdf_link") == "" or item.get("pdf_link") == None 
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print(f"Total pdf valid: {len(filtered)}")
    return filtered

prepare_pdf_dataset("./faq_pajak_raw.json")