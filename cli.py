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
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="enable verbose output"
    )
    parser.add_argument(
        "--ignore-files",
        nargs='+',
        default=[],
        help="list of file paths or patterns to ignore during scanning"
    )
    parser.add_argument(
        "--ignore-llms",
        action="store_true",
        help="disable LLM analysis for secret detection"
    )

    args = parser.parse_args()

    try:
        findings = scan_repository(args.repo, args.n, verbose=args.verbose, ignore_files=args.ignore_files, ignore_llms=args.ignore_llms)
    except Exception as inst:
        print(str(inst))
        return

    save_report(findings, args.out)

    print(f"\nScan complete. Report saved to {args.out}.")
    if not findings:
        print("No secrets found.")

if __name__ == "__main__":
    main()