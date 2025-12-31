from jsonschema import validate, ValidationError
import uuid


# --- Base Validation Function ---
def validate_payload(data: dict, schema: dict) -> tuple[bool, str | None]:
    """Validates data against schema

    Args:
        data (dict): Data to validate
        schema (dict): Schema from predefined

    Returns:
        tuple[bool, str | None]: (result of validation, error | None)
    """
    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        # Returns a clear message like "Additional properties are not allowed ('hack' was unexpected)"
        return False, e.message


# --- Schema Definitions ---

# Schema for Adding a Password
password_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "email": {"type": "string"},
        "login": {"type": "string"},
        "password": {"type": "string"},
        "domain": {"type": "string"},
        "tfa": {"type": "string"},
    },
    "required": ["email", "login", "password", "domain", "tfa"],
    "additionalProperties": False,  # Security: Rejects unknown fields
}

# Schema for Adding a Note
note_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "content": {"type": "string"},
    },
    "required": ["name", "content"],
    "additionalProperties": False,
}

# Schema for Adding a Credit Card
credit_card_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "bankName": {"type": "string"},
        "number": {"type": "string"},
        "brand": {"type": "string"},
        "cvv": {"type": "string"},
        "owner": {"type": "string"},
        "exp_date": {"type": "string"},  # Mapping JSON 'exp_date' -> DB 'expDate'
    },
    "required": ["bankName", "number", "brand", "cvv", "owner", "exp_date"],
    "additionalProperties": False,
}

# Schema for Adding an Identity
identity_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "surname": {"type": "string"},
        "country": {"type": "string"},
        "state": {"type": "string"},
        "city": {"type": "string"},
        "street": {"type": "string"},
        "number": {"type": "string"},
    },
    "required": [
        "name",
        "surname",
        "country",
        "state",
        "city",
        "street",
        "number",
    ],
    "additionalProperties": False,
}

# Schema for Adding a License
license_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        # 'diverse' is JSONB in DB, so we accept object OR string here
        "diverse": {"type": ["object", "string"]},
    },
    "required": ["name", "diverse"],
    "additionalProperties": False,
}


def validate_uuid4(uuid_string: str) -> bool:
    """Validates whether provided ID is in correct format of uuid4

    Args:
        uuid_string (str): ID to be validated

    Returns:
        bool: Result of validation
    """
    if not uuid_string:
        return False

    try:
        # strict=False allows some flexibility (like uppercase),
        # but version=4 enforces the correct UUID type.
        val = uuid.UUID(str(uuid_string), version=4)
    except ValueError:
        # Not a valid UUID hex string
        return False

    # Optional: If you want to force exact formatting (lowercase + hyphens),
    # verify that the input string matches the normalized version.
    return str(val) == str(uuid_string).lower()
