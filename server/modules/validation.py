from jsonschema import validate, ValidationError
import uuid


from jsonschema import validate, ValidationError

USER_EDITABLE_TABLES = [
    "Password",
    "Notes",
    "CreditCard",
    "Identity",
    "CreditCard",
    "License",
]


# --- Base Validation Function ---
def validate_payload(data, schema):
    """
    Validates data against the schema.
    Returns (True, None) if valid.
    Returns (False, error_message) if invalid.
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
        "email": {"type": "string"},
        "login": {"type": "string"},
        "password": {"type": "string"},
        "domain": {"type": "string"},
        "tfa": {"type": "string"},
        "favourite": {"type": "boolean"},
    },
    "required": ["email", "login", "password", "domain", "tfa"],
    "additionalProperties": False,  # Security: Rejects unknown fields
}

# Schema for Adding a Note
note_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "content": {"type": "string"},
        "favourite": {"type": "boolean"},
    },
    "required": ["name", "content"],
    "additionalProperties": False,
}

# Schema for Adding a Credit Card
credit_card_schema = {
    "type": "object",
    "properties": {
        "bankName": {"type": "string"},
        "number": {"type": "string"},
        "brand": {"type": "string"},
        "cvv": {"type": "string"},
        "owner": {"type": "string"},
        "exp_date": {"type": "string"},  # Mapping JSON 'exp_date' -> DB 'expDate'
        "favourite": {"type": "boolean"},
    },
    "required": ["bankName", "number", "brand", "cvv", "owner", "exp_date"],
    "additionalProperties": False,
}

# Schema for Adding an Identity
identity_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "surname": {"type": "string"},
        "country": {"type": "string"},
        "state": {"type": "string"},
        "city": {"type": "string"},
        "street": {"type": "string"},
        "number": {"type": "string"},
        "favourite": {"type": "boolean"},
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
        "name": {"type": "string"},
        # 'diverse' is JSONB in DB, so we accept object OR string here
        "diverse": {"type": ["object", "string"]},
        "favourite": {"type": "boolean"},
    },
    "required": ["name", "diverse"],
    "additionalProperties": False,
}


def validate_uuid4(uuid_string):
    """
    Returns True if uuid_string is a valid version 4 UUID.
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
