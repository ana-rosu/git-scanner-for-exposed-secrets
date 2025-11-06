import json

def save_report(report_data, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)
