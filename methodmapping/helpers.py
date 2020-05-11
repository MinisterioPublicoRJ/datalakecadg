def header_to_schema(header: str) -> dict:
    header = header.split(",")
    fields = []
    for field in header:
        fields.append(dict(name=field))

    return dict(fields=fields)
