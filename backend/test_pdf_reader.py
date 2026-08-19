from services.pdf_reader import extract_text_from_pdf


pdf_path = "../sample_documents/sample_payslip.pdf"

text = extract_text_from_pdf(pdf_path)

print("\n========== EXTRACTED TEXT ==========\n")
print(text)
print("\n====================================\n")