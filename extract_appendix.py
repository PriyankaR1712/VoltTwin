from pypdf import PdfReader

pdf_path = "reference/SOHbenchmark/SOHbenchmark - Appendix.pdf"
output_path = "reference/SOHbenchmark/appendix_extracted.txt"

reader = PdfReader(pdf_path)

with open(output_path, "w", encoding="utf-8") as file:
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        file.write(f"\n\n========== PAGE {i + 1} ==========\n")
        file.write(text)

print("Total pages:", len(reader.pages))
print("Extracted appendix saved to:", output_path)