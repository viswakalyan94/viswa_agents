import re

def extract_object_name(sql_text):
    patterns = [
        r'CREATE\s+OR\s+REPLACE\s+PROCEDURE\s+(\w+)',
        r'CREATE\s+OR\s+REPLACE\s+FUNCTION\s+(\w+)',
        r'CREATE\s+OR\s+REPLACE\s+PACKAGE\s+(\w+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, sql_text, re.IGNORECASE)
        if match:
            return match.group(1)

    return "UNKNOWN_OBJECT"