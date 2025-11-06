import json

def save_report(findings, out_file):
    with open(out_file, 'w') as f:
        json.dump(findings, f, indent=4)
    print(f"\nScan complete. Report saved to {out_file}")