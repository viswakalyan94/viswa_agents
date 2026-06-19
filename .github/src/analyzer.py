import re

def analyze_sql(sql_text):
    result = {
        "insert": len(re.findall(r'\bINSERT\b', sql_text, re.IGNORECASE)),
        "update": len(re.findall(r'\bUPDATE\b', sql_text, re.IGNORECASE)),
        "delete": len(re.findall(r'\bDELETE\b', sql_text, re.IGNORECASE))
    }
    return result