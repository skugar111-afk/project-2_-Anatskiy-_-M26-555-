def _parse_literal(raw):

    raw = raw.strip()
    if not raw:
        raise ValueError(raw)

    # Строка в кавычках
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        return raw[1:-1]

    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False

    try:
        return int(raw)
    except ValueError:
        pass

    raise ValueError(raw)


def parse_where(clause):
    if "=" not in clause:
        raise ValueError(clause)

    field, value = clause.split("=", 1)
    field = field.strip()
    if not field:
        raise ValueError(clause)

    return {field: _parse_literal(value)}


def parse_set(clause):
    result = {}
    parts = [p.strip() for p in clause.split(",") if p.strip()]
    if not parts:
        raise ValueError(clause)

    for part in parts:
        result.update(parse_where(part))
    return result
