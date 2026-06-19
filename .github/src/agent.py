import os
from parser import extract_object_name
from analyzer import analyze_sql
from report_generator import generate_html_report
# from email_sender import send_email   # optional

SQL_FOLDER = "samples"
OUTPUT_FILE = "output/report.html"

def run_agent():
    results = []

    for file in os.listdir(SQL_FOLDER):
        if file.endswith(".sql"):
            path = os.path.join(SQL_FOLDER, file)

            with open(path, "r", encoding="utf-8") as f:
                sql_text = f.read()

            object_name = extract_object_name(sql_text)
            analysis = analyze_sql(sql_text)

            results.append({
                "object": object_name,
                "insert": analysis["insert"],
                "update": analysis["update"],
                "delete": analysis["delete"]
            })

    generate_html_report(results, OUTPUT_FILE)
    print(f"✅ Report generated: {OUTPUT_FILE}")

    # Optional email
    # send_email(sender, password, receiver, "SQL Report", OUTPUT_FILE)


if __name__ == "__main__":
    run_agent()