import argparse
from src.repo_scanner import scan_repository
from src.reporting import save_report

def main():
    parser = argparse.ArgumentParser(
        description="Scans the last N commits of a Git repository for secrets."
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="path to local git repository or URL for remote repository"
    )
    parser.add_argument(
        "--n",
        type=int,
        default=10,
        help="number of recent commits to scan (default: 10)"
    )
    parser.add_argument(
        "--out",
        default="report.json",
        help="output JSON report file (default: report.json)"
    )
    args = parser.parse_args()

    try:
        findings = scan_repository(args.repo, args.n)
    except Exception as inst:
        print(str(inst))
        return

    if findings:
        save_report(findings, args.out)
        return 
    
    print("\nScan complete. No secrets found.")

if __name__ == "__main__":
    main()