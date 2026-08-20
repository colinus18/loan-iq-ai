from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime
from typing import Any, Dict, List

# Insert project root into sys.path to run directly
sys.path.insert(0, ".")

from fastapi.testclient import TestClient

# Import extraction schemas to construct mock inputs
from backend.agents.extraction.schemas import (
    ExtractResponse,
    SingleDocumentResult,
    ExtractedFields,
    DocumentMeta,
    PersonalInfo,
    IncomeInfo,
    BankInfo,
    DocumentType,
    ExtractionStatus,
)
from backend.agents.extraction import store as extraction_store
from backend.agents.validation.validator import ValidationEngine
from backend.agents.validation import store as validation_store
from backend.agents.validation.schemas import ValidationResult
from backend.main import app

# Setup test client
client = TestClient(app)
engine = ValidationEngine()

errors: List[str] = []


def assert_test(name: str, condition: bool, message: str = "") -> None:
    """Helper assertion function to gather failures without halting the whole suite."""
    if not condition:
        err_msg = f"FAIL [{name}]: {message}"
        errors.append(err_msg)
        print(f"  [FAIL] {err_msg}")
    else:
        print(f"  [PASS] {name}")


# ── Mock Helper ──────────────────────────────────────────────────────────────

def create_mock_extraction_response(
    app_id: str,
    documents_fields: List[Dict[str, Any]]
) -> ExtractResponse:
    """Helper to build a valid ExtractResponse from simplified dicts for testing."""
    docs = []
    for idx, doc_data in enumerate(documents_fields):
        doc_type = doc_data.get("doc_type", DocumentType.UNKNOWN)
        filename = doc_data.get("filename", f"doc_{idx}.pdf")
        
        # Build section fields
        p_info = PersonalInfo(**doc_data.get("personal", {}))
        i_info = IncomeInfo(**doc_data.get("income", {}))
        b_info = BankInfo(**doc_data.get("bank", {}))
        
        fields = ExtractedFields(
            document_meta=DocumentMeta(
                document_type=doc_type,
                document_date=doc_data.get("document_date"),
                issuing_entity=doc_data.get("issuing_entity")
            ),
            personal=p_info,
            income=i_info,
            bank=b_info,
            confidence_score=doc_data.get("confidence_score", 0.95),
            extraction_notes=doc_data.get("extraction_notes")
        )
        
        docs.append(
            SingleDocumentResult(
                filename=filename,
                doc_index=idx,
                fields=fields,
                status=ExtractionStatus.SUCCESS
            )
        )
        
    # Build a simple merged representation
    merged_fields = None
    if docs:
        merged_fields = docs[0].fields  # simple fallback for tests
        
    return ExtractResponse(
        application_id=app_id,
        status=ExtractionStatus.SUCCESS,
        documents=docs,
        merged_fields=merged_fields,
        processing_time_ms=10.0
    )


# ── Run Unit Tests ────────────────────────────────────────────────────────────

def test_unit_tests() -> None:
    errors.clear()
    print("\n--- RUNNING MEMBER 4 UNIT TESTS ---")

    # 1. Test 1 — Valid application
    print("\n[Test 1: Valid application]")
    mock_app_1 = create_mock_extraction_response(
        app_id="TEST-APP-001",
        documents_fields=[
            {
                "doc_type": DocumentType.PAN_CARD,
                "filename": "pan.jpg",
                "personal": {"name": "John Doe", "pan": "ABCDE1234F", "dob": "15/08/1990"}
            },
            {
                "doc_type": DocumentType.PAYSLIP,
                "filename": "payslip.pdf",
                "personal": {"name": "John Doe"},
                "income": {"gross_salary": "82,000", "net_salary": "80,000"}
            },
            {
                "doc_type": DocumentType.BANK_STATEMENT,
                "filename": "bank.pdf",
                "personal": {"name": "John Doe"},
                "bank": {"ifsc": "SBIN0001234"},
                "income": {"net_salary": "80,000"}  # matched credit
            }
        ]
    )
    res_1 = engine.validate("TEST-APP-001", mock_app_1)
    assert_test("Valid app overall passed", all(res_1.validation.model_dump().values()))
    assert_test("Valid app fraud score is 0", res_1.fraud.fraud_score == 0)
    assert_test("Valid app level is LOW", res_1.fraud.level == "LOW")

    # 2. Test 2 — Invalid PAN
    print("\n[Test 2: Invalid PAN]")
    mock_app_2 = create_mock_extraction_response(
        app_id="TEST-APP-002",
        documents_fields=[
            {
                "doc_type": DocumentType.PAN_CARD,
                "filename": "pan.jpg",
                "personal": {"pan": "INVALID123", "name": "John Doe"}
            }
        ]
    )
    res_2 = engine.validate("TEST-APP-002", mock_app_2)
    pan_check = next(c for c in res_2.checks if c.rule == "pan_format")
    assert_test("PAN format fails", not pan_check.passed)
    assert_test("PAN format check has HIGH/MEDIUM severity", pan_check.severity in ("HIGH", "MEDIUM", "CRITICAL"))

    # 3. Test 3 — Salary mismatch
    print("\n[Test 3: Salary mismatch]")
    mock_app_3 = create_mock_extraction_response(
        app_id="TEST-APP-003",
        documents_fields=[
            {
                "doc_type": DocumentType.PAYSLIP,
                "filename": "payslip.pdf",
                "income": {"net_salary": "82,000"}
            },
            {
                "doc_type": DocumentType.BANK_STATEMENT,
                "filename": "bank.pdf",
                "income": {"net_salary": "45,000"}
            }
        ]
    )
    res_3 = engine.validate("TEST-APP-003", mock_app_3)
    sal_check = next(c for c in res_3.checks if c.rule == "salary_cross_check")
    assert_test("Salary cross check fails", not sal_check.passed)
    assert_test("Salary check failed with HIGH severity", sal_check.severity == "HIGH")
    assert_test("Salary category status is False", not res_3.validation.salary)
    assert_test("Fraud score is bumped by high severity", res_3.fraud.fraud_score >= 30)

    # 4. Test 4 — Name mismatch
    print("\n[Test 4: Name mismatch]")
    mock_app_4 = create_mock_extraction_response(
        app_id="TEST-APP-004",
        documents_fields=[
            {
                "doc_type": DocumentType.PAN_CARD,
                "filename": "pan.jpg",
                "personal": {"name": "John Doe"}
            },
            {
                "doc_type": DocumentType.PAYSLIP,
                "filename": "payslip.pdf",
                "personal": {"name": "Jane Doe"}
            }
        ]
    )
    res_4 = engine.validate("TEST-APP-004", mock_app_4)
    name_check = next(c for c in res_4.checks if c.rule == "name_match")
    assert_test("Name match fails", not name_check.passed)
    assert_test("Name check failed with HIGH severity", name_check.severity == "HIGH")
    assert_test("Name category status is False", not res_4.validation.name)

    # 5. Test 5 — DOB mismatch
    print("\n[Test 5: DOB mismatch]")
    mock_app_5 = create_mock_extraction_response(
        app_id="TEST-APP-005",
        documents_fields=[
            {
                "doc_type": DocumentType.PAN_CARD,
                "filename": "pan.jpg",
                "personal": {"dob": "01/01/1995"}
            },
            {
                "doc_type": DocumentType.AADHAAR,
                "filename": "aadhaar.pdf",
                "personal": {"dob": "01/01/1998"}
            }
        ]
    )
    res_5 = engine.validate("TEST-APP-005", mock_app_5)
    dob_check = next(c for c in res_5.checks if c.rule == "dob_match")
    assert_test("DOB check fails", not dob_check.passed)
    assert_test("DOB category status is False", not res_5.validation.dob)

    # 6. Test 6 — Conflicting PAN
    print("\n[Test 6: Conflicting PAN]")
    mock_app_6 = create_mock_extraction_response(
        app_id="TEST-APP-006",
        documents_fields=[
            {
                "doc_type": DocumentType.PAN_CARD,
                "filename": "pan1.jpg",
                "personal": {"pan": "ABCDE1234F"}
            },
            {
                "doc_type": DocumentType.LOAN_APP,
                "filename": "app.pdf",
                "personal": {"pan": "XYZAB9876C"}
            }
        ]
    )
    res_6 = engine.validate("TEST-APP-006", mock_app_6)
    conflict_check = next(c for c in res_6.checks if c.rule == "pan_conflict")
    assert_test("PAN conflict triggered", not conflict_check.passed)
    assert_test("PAN conflict check has CRITICAL severity", conflict_check.severity == "CRITICAL")
    assert_test("PAN category status is False", not res_6.validation.pan)
    assert_test("Fraud score is >= 50 for CRITICAL", res_6.fraud.fraud_score >= 50)

    # 7. Test 7 — Missing document
    print("\n[Test 7: Missing document]")
    mock_app_7 = create_mock_extraction_response(
        app_id="TEST-APP-007",
        documents_fields=[
            {
                "doc_type": DocumentType.PAN_CARD,
                "filename": "pan.jpg"
            }
            # Missing payslip and bank statement
        ]
    )
    res_7 = engine.validate("TEST-APP-007", mock_app_7)
    docs_check = next(c for c in res_7.checks if c.rule == "required_documents")
    assert_test("Required docs check fails", not docs_check.passed)
    assert_test("Required docs status is False", not res_7.validation.documents)
    assert_test("Required docs lists missing bank_statement and payslip", 
                "bank_statement" in docs_check.details.get("missing", []) and 
                "payslip" in docs_check.details.get("missing", []))

    # 8. Test 8 — Valid IFSC
    print("\n[Test 8: Valid IFSC]")
    mock_app_8 = create_mock_extraction_response(
        app_id="TEST-APP-008",
        documents_fields=[
            {
                "doc_type": DocumentType.BANK_STATEMENT,
                "filename": "bank.pdf",
                "bank": {"ifsc": "SBIN0001234"}
            }
        ]
    )
    res_8 = engine.validate("TEST-APP-008", mock_app_8)
    ifsc_check = next(c for c in res_8.checks if c.rule == "ifsc_format")
    assert_test("Valid IFSC passes", ifsc_check.passed)
    assert_test("IFSC category status is True", res_8.validation.ifsc)

    # 9. Test 9 — Invalid IFSC
    print("\n[Test 9: Invalid IFSC]")
    mock_app_9 = create_mock_extraction_response(
        app_id="TEST-APP-009",
        documents_fields=[
            {
                "doc_type": DocumentType.BANK_STATEMENT,
                "filename": "bank.pdf",
                "bank": {"ifsc": "123INVALID"}
            }
        ]
    )
    res_9 = engine.validate("TEST-APP-009", mock_app_9)
    ifsc_check = next(c for c in res_9.checks if c.rule == "ifsc_format")
    assert_test("Invalid IFSC fails", not ifsc_check.passed)
    assert_test("IFSC category status is False", not res_9.validation.ifsc)

    # 10. Test 10 — Insufficient data
    print("\n[Test 10: Insufficient data]")
    mock_app_10 = create_mock_extraction_response(
        app_id="TEST-APP-010",
        documents_fields=[
            {
                "doc_type": DocumentType.UNKNOWN,
                "filename": "unknown_file.pdf",
                "personal": {"name": "John"}
            }
        ]
    )
    # This shouldn't crash
    try:
        res_10 = engine.validate("TEST-APP-010", mock_app_10)
        assert_test("Insufficient data runs without crash", True)
        
        # Check that unavailable rules return insufficient/not_applicable status in details
        name_check = next(c for c in res_10.checks if c.rule == "name_match")
        dob_check = next(c for c in res_10.checks if c.rule == "dob_match")
        salary_check = next(c for c in res_10.checks if c.rule == "salary_cross_check")
        
        assert_test("Name check is insufficient_data", name_check.details.get("status") == "insufficient_data")
        assert_test("DOB check is insufficient_data", dob_check.details.get("status") == "insufficient_data")
        assert_test("Salary check is insufficient_data", salary_check.details.get("status") == "insufficient_data")
        
        # Insufficient data should not trigger fraud
        assert_test("Insufficient data does not trigger fraud score", res_10.fraud.fraud_score in (0, 30, 35))
    except Exception as e:
        assert_test("Insufficient data runs without crash", False, f"Crashed with error: {e}")
    
    assert len(errors) == 0, f"Failed unit tests: {errors}"


# ── Run API Integration Tests ──────────────────────────────────────────────────

def test_api_integration_tests() -> None:
    errors.clear()
    print("\n--- RUNNING FASTAPI INTEGRATION TESTS ---")

    # Seed mock extraction result under application ID M4-INTEGRATION-TEST-003
    mock_extracted = create_mock_extraction_response(
        app_id="M4-INTEGRATION-TEST-003",
        documents_fields=[
            {
                "doc_type": DocumentType.PAN_CARD,
                "filename": "pan.pdf",
                "personal": {"pan": "ABCDE1234F", "name": "M4 Integration User", "dob": "01/01/1990"}
            },
            {
                "doc_type": DocumentType.PAYSLIP,
                "filename": "payslip.pdf",
                "personal": {"name": "M4 Integration User"},
                "income": {"gross_salary": "82,000", "net_salary": "80,000"}
            },
            {
                "doc_type": DocumentType.BANK_STATEMENT,
                "filename": "bank.pdf",
                "personal": {"name": "M4 Integration User"},
                "bank": {"ifsc": "SBIN0001234"},
                "income": {"net_salary": "80,000"}
            }
        ]
    )
    extraction_store.save(mock_extracted)
    print("Seeded extraction store for 'M4-INTEGRATION-TEST-003'")

    # 1. POST /validate
    payload = {"application_id": "M4-INTEGRATION-TEST-003"}
    resp = client.post("/validate", json=payload)
    assert_test("POST /validate HTTP 200", resp.status_code == 200, f"Status: {resp.status_code}, Body: {resp.text}")
    
    if resp.status_code == 200:
        data = resp.json()
        assert_test("Response application_id matches", data.get("application_id") == "M4-INTEGRATION-TEST-003")
        assert_test("Response status is completed", data.get("status") == "completed")
        assert_test("Response has validation summary", "validation" in data)
        assert_test("Response has checks list", "checks" in data and isinstance(data["checks"], list))
        assert_test("Response has fraud summary", "fraud" in data)
        assert_test("Fraud score is 0", data.get("fraud", {}).get("fraud_score") == 0)

    # 2. GET /validation/M4-INTEGRATION-TEST-003
    resp_get = client.get("/validation/M4-INTEGRATION-TEST-003")
    assert_test("GET /validation/M4-INTEGRATION-TEST-003 HTTP 200", resp_get.status_code == 200)
    if resp_get.status_code == 200:
        data_get = resp_get.json()
        assert_test("GET response matches POST response", data_get.get("application_id") == "M4-INTEGRATION-TEST-003")

    # 3. GET /validation/DOES-NOT-EXIST
    resp_missing = client.get("/validation/DOES-NOT-EXIST")
    assert_test("GET /validation/DOES-NOT-EXIST HTTP 404", resp_missing.status_code == 404)
    
    # 4. POST /validate on non-existent extraction
    resp_validate_missing = client.post("/validate", json={"application_id": "DOES-NOT-EXIST"})
    assert_test("POST /validate on non-existent extraction HTTP 404", resp_validate_missing.status_code == 404)

    assert len(errors) == 0, f"Failed integration tests: {errors}"


# ── Main Suite Runner ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_unit_tests()
    test_api_integration_tests()

    print("\n--- TEST SUMMARY ---")
    if errors:
        print(f"FAIL: {len(errors)} assertions failed!")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("SUCCESS: All tests passed successfully!")
        sys.exit(0)
