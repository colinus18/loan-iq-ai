from services.document_processor import process_document


pdf_path = "../sample_documents/sample_payslip.pdf"
image_path = "../sample_documents/sample_payslip.png"


print("\n========== PDF TEST ==========\n")

pdf_result = process_document(pdf_path)

print("File:", pdf_result["file_name"])
print("Type:", pdf_result["file_type"])
print("Method:", pdf_result["processing_method"])
print("Status:", pdf_result["status"])
print("Text:")
print(pdf_result["text"])


print("\n========== IMAGE TEST ==========\n")

image_result = process_document(image_path)

print("File:", image_result["file_name"])
print("Type:", image_result["file_type"])
print("Method:", image_result["processing_method"])
print("Status:", image_result["status"])
print("Text:")
print(image_result["text"])