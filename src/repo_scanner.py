import os
import shutil
from git import Repo, exc
from src.analysis.heuristics import check_line_with_heuristics
from src.analysis.llm_analyzer import get_llm_analysis
from src.utils import handle_rm_error
from src.config import NUMBER_OF_CONTEXT_LINES

def scan_repository(repo_path: str, n_commits: int, verbose: bool = False, ignore_files: list = [], ignore_llms: bool = False):
    repo = None
    temp_dir = None
    findings = []

    try:
        repo, temp_dir = get_repo(repo_path, verbose)
    except (exc.InvalidGitRepositoryError,exc.NoSuchPathError) as e:
        raise Exception(f"Not a valid git repository: {repo_path}")
    
    if not repo.head.is_valid():
            raise Exception("Repository contains no commits. Nothing to scan.")
    
    try:
        for commit in repo.iter_commits(max_count=n_commits):
            scan_msg = f"Scanning commit {commit.hexsha}"
            if verbose:
                scan_msg = scan_msg.center(80, '-')
            print(scan_msg)

            try:
                parent = commit.parents[0] if commit.parents else None
                diffs = commit.diff(parent, create_patch=True)
            except IndexError:  # Initial commit
                diffs = commit.tree.diff(None, create_patch=True)

            if verbose:
                print(f"Commit {commit.hexsha} has {len(diffs)} diffs")

            for diff in diffs:
                if not diff.diff:
                    continue
                file_path = diff.a_path or diff.b_path
                if file_path in ignore_files:
                    if verbose:
                        print(f"Skipping ignored file: {file_path}")
                    continue
                if verbose:
                    print(f"\n\tAnalyzing file: {file_path}\n")

                diff_text = decode_diff(diff, file_path)
                lines = diff_text.split('\n')
        
                llm_lines = []
                for i, line in enumerate(lines):
                    if not line.startswith('+'):
                        continue

                    base_finding, send_to_llm, heuristic_result = process_line(
                        line, commit.hexsha, file_path, ignore_llms, verbose)
                    
                    if base_finding is None:
                        continue

                    if send_to_llm:
                        llm_lines.append(i)
                    else:
                        base_finding.update(heuristic_result)
                        findings.append(base_finding)

                findings.extend(analyze_llm_snippets(lines, llm_lines, commit, file_path, verbose))

    except (exc.GitCommandError) as e:
        raise Exception(f"Error processing repository: {str(e)}")
    finally:
        if repo:
            repo.close()

        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, onerror=handle_rm_error)

    return findings

def get_repo(repo_path: str, verbose: bool = False):
    """Return a Repo object, cloning if necessary."""
    temp_dir = None
    repo = None

    if os.path.isdir(repo_path):
        repo = Repo(repo_path)
    else:
        temp_dir = "temp_repo"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, onerror=handle_rm_error)
        if verbose:
            print(f"Cloning {repo_path} into {temp_dir}...")
        repo = Repo.clone_from(repo_path, temp_dir)

    return repo, temp_dir

def process_line(line: str, commit_hash: str, file_path: str, ignore_llms: bool = False, verbose: bool = False):
    content = line[1:].strip()
    if not content:
        return None, False, []

    print(f"\nChecking line: {content[:50]}...")
    heuristic_result = check_line_with_heuristics(content)
    if not heuristic_result:
        if verbose:
            print("Heuristic: no potential secret found.")
        return None, False, []

    send_to_llm = heuristic_result.pop("requires_llm_check")
    if ignore_llms:
        send_to_llm = False

    base_finding = {
        "commit_hash": commit_hash,
        "file_path": file_path,
        "snippet": content,
    }

    if verbose:
        print(f"Heuristic result: {heuristic_result}")
        if send_to_llm:
            print("Heuristic: send to LLM for further analysis.")
        else:
            print("Heuristic: strong enough, adding directly.")

    return base_finding, send_to_llm, heuristic_result

def merge_llm_ranges(line_indices: list, total_lines: int) -> list:
    """Merge nearby line indices into ranges for LLM analysis."""
    if not line_indices:
        return []

    line_indices.sort()
    merged_ranges = []
    start = end = line_indices[0]

    for idx in line_indices[1:]:
        if idx <= end + NUMBER_OF_CONTEXT_LINES:
            end = idx
        else:
            merged_ranges.append((max(0, start-NUMBER_OF_CONTEXT_LINES),
                                  min(total_lines, end+NUMBER_OF_CONTEXT_LINES)))
            start = end = idx
    merged_ranges.append((max(0, start-NUMBER_OF_CONTEXT_LINES),
                          min(total_lines, end+NUMBER_OF_CONTEXT_LINES)))
    return merged_ranges

def analyze_llm_snippets(lines: list, llm_lines: list, commit, file_path: str, verbose: bool = False) -> list:
    """Process merged LLM snippets and return findings from LLM."""
    findings = []
    merged_ranges = merge_llm_ranges(llm_lines, len(lines))
    for start, end in merged_ranges:
        snippet = "\n".join(lines[start:end])
        if verbose:
            print(f"\nLLM check required for snippet:\n{snippet[:200]}...\n")
        llm_result = get_llm_analysis(snippet, commit.message, file_path)
        if llm_result:
            if verbose:
                print(f"LLM analysis result: {llm_result}\n")
            findings.append({
                "commit_hash": commit.hexsha,
                "file_path": file_path,
                "snippet": snippet,
                **llm_result
            })
        else:
            if verbose:
                print("LLM analysis: no secret found.\n")
    return findings

def decode_diff(diff: str, file_path: str) -> str:
    try:
        return diff.diff.decode('utf-8', errors='ignore')
    except Exception as e:
        raise Exception(f"Error decoding diff for {file_path}: {e}")