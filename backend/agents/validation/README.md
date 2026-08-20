# Member 4 — Validation & Fraud Detection Module

This module implements the deterministic consistency checks and fraud detection for LoanIQ AI. It consumes the structured extraction results from Member 3, performs validation cross-checks across multiple documents, and determines a fraud score ready for consumption by Member 5's Risk Engine.

## 1. Responsibilities

- **Receive application ID**: Fetch Member 3's extracted structured data in-process.
- **Cross-document consistency**: Compare critical fields (Name, Date of Birth, PAN, Address) across all uploaded files.
- **Salary cross-checks**: Verify monthly take-home salary against bank statement credits and ITR annual income (using configurable tolerances).
- **Format checks**: Perform deterministic regex checks on PAN and IFSC formats.
- **Required document verification**: Ensure necessary files (PAN card, Payslip, Bank Statement) are present.
- **Expiry check**: Inspect document expiration dates.
- **Fraud scoring**: Assign a deterministic, explainable fraud score and risk level.

## 2. API Endpoints

### Run Validation
`POST /validate`
- **Request Payload**:
  ```json
  {
    "application_id": "APP-12345"
  }
  ```
- **Description**: Recalculates and replaces the validation and fraud report in-memory for the application.

### Get Validation Report
`GET /validation/{application_id}`
- **Description**: Retrieves the previously generated validation and fraud report. Returns `404` if validation has not been run.

## 3. Validation Rules (Deterministic)

1. **PAN Format**: Matches `^[A-Z]{5}[0-9]{4}[A-Z]$`.
2. **IFSC Format**: Matches `^[A-Z]{4}0[A-Z0-9]{6}$`.
3. **Name Match**: Tokenizes and matches words pairwise across all available documents. A match passes if Jaccard similarity of words is $\ge 0.60$ or if one name is a subset of the other.
4. **DOB Match**: Normalizes dates (`DD/MM/YYYY`, `YYYY-MM-DD`, `DD-MM-YYYY`) and checks for exact equality.
5. **Address Match**: Tokenizes addresses pairwise and compares them using Jaccard word similarity. A match passes if similarity is $\ge 0.35$ (accounting for address structure variations).
6. **Salary Cross-Check**:
   - Monthly net salary vs. Bank Statement credits (within $10\%$ tolerance).
   - Monthly salary $\times$ 12 vs. ITR Annual Income (within $20\%$ tolerance).
7. **Required Documents**: Verifies presence of `pan_card`, `payslip`, and `bank_statement`.
8. **Expiry check**: Parses expiration dates and compares them to UTC today.
9. **Conflicting PANs**: Checks if multiple distinct PAN cards/numbers exist across the uploads.

## 4. Fraud Scoring and Severity

Failed validation checks trigger fraud findings according to their severity. The weights are:
- **INFO**: $0$
- **LOW**: $5$
- **MEDIUM**: $15$
- **HIGH**: $30$
- **CRITICAL**: $50$

The cumulative score is capped at $100$ and mapped to a fraud level:
- **LOW**: Score $< 15$
- **MEDIUM**: $15 \le \text{Score} < 40$
- **HIGH**: $40 \le \text{Score} < 75$
- **CRITICAL**: $\text{Score} \ge 75$

All weights and thresholds are configured in [rules.py](file:///e:/cogni/loan-iq-ai/backend/agents/fraud/rules.py).

## 5. Running Tests

To run the validation test suite containing unit tests and API integration tests:
```powershell
python backend/agents/validation/test_validation.py
```
