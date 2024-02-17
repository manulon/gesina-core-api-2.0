def validate_fields(body, required_fields):
    missing_fields = [field for field in required_fields if field not in body or body.get(field) is None]
    return missing_fields