def row_to_dict(cursor, row):
    return {desc[0]: value for desc, value in zip(cursor.description, row)}
