from backend.agents.risk.integration_service import process_application


APPLICATION_ID = "M4-INTEGRATION-TEST-003"


result = process_application(APPLICATION_ID)


print("\n=== FINAL MEMBER 5 RESULT ===")
print(result)