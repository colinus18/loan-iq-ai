from services.ocr import extract_text_from_image


image_path = "../sample_documents/sample_payslip.png"

text = extract_text_from_image(image_path)

print("\n========== OCR TEXT ==========\n")
print(text)
print("\n==============================\n")