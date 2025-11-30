def parse_characteristics(chars_str: str) -> dict:
    if not chars_str or not isinstance(chars_str, str):
        return {}

    pairs = [pair.strip() for pair in chars_str.split(";") if pair.strip()]
    result = {}

    for pair in pairs:
        if ":" in pair:
            key, value = pair.split(":", 1)
            result[key.strip()] = value.strip()

    return result
