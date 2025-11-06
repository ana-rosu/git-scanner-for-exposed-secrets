import json

def save_report(findings, out_file):
    with open(out_file, 'w') as f:
        if not findings:
            f.write(json.dumps({"message": "No secrets found"}, indent=4))
        else:
            json.dump(findings, f, indent=4)
    