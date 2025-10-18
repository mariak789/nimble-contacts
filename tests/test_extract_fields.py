# tests/test_extract_fields.py
from app.sync_nimble import extract_fields

def test_extract_fields_handles_arrays_and_missing_values():
    nimble_contact = {
        "fields": {
            "first name": [{"value": "John"}],
            "last name":  [{"value": "Doe"}],
            "email":      [{"value": "john.doe@example.com"}],
            "description":[{"value": "Some notes"}],
        }
    }
    assert extract_fields(nimble_contact) == (
        "John", "Doe", "john.doe@example.com", "Some notes"
    )

def test_extract_fields_returns_none_for_empty():
    nimble_contact = {"fields": {"email": []}}
    first, last, email, desc = extract_fields(nimble_contact)
    assert first is None and last is None and email is None and desc is None