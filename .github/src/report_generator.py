def generate_html_report(data, output_file):
    html = """
    <html>
    <head>
        <style>
            table {border-collapse: collapse; width: 80%;}
            th, td {border: 1px solid black; padding: 8px; text-align: center;}
            th {background-color: #4CAF50; color: white;}
        </style>
    </head>
    <body>
        <h2>SQL Analysis Report</h2>
        <table>
            <tr>
                <th>Object Name</th>
                <th>INSERT Count</th>
                <th>UPDATE Count</th>
                <th>DELETE Count</th>
            </tr>
    """

    for row in data:
        html += f"""
        <tr>
            <td>{row['object']}</td>
            <td>{row['insert']}</td>
            <td>{row['update']}</td>
            <td>{row['delete']}</td>
        </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    with open(output_file, "w") as f:
        f.write(html)