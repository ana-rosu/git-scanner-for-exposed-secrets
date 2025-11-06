import os
import shutil
from git import Repo, exc
from src.analysis.heuristics import check_line_with_heuristics
from src.analysis.llm_analyzer import get_llm_analysis
from src.utils import handle_rm_error
from src.config import NUMBER_OF_CONTEXT_LINES

def scan_repository(repo_path, n_commits, verbose=False, ignore_files=[], ignore_llms=False):
    repo = None
    temp_dir = None
    findings = []

    try:
        if os.path.isdir(repo_path):
            repo = Repo(repo_path)
        else:
            temp_dir = "temp_repo"
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, onerror=handle_rm_error)
            if verbose:
                print(f"Cloning {repo_path}...")
            repo = Repo.clone_from(repo_path, temp_dir)
    except (exc.InvalidGitRepositoryError,exc.NoSuchPathError) as e:
        raise Exception(f"Not a valid git repository: {repo_path}")
    
    try:      
        if not repo.head.is_valid():
            raise Exception("Repository contains no commits. Nothing to scan.")

        for commit in repo.iter_commits(max_count=n_commits):
            print(f"Scanning commit {commit.hexsha}...")
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
                    print(f"\nAnalyzing file: {file_path}")

                try:
                    diff_text = diff.diff.decode('utf-8', errors='ignore')
                except Exception as e:
                    raise Exception(f"Error decoding diff for {file_path}: {e}")

                lines = diff_text.split('\n')
        
                llm_lines = []
                for i, line in enumerate(lines):
                    if line.startswith('+'):
                        content = line[1:].strip()
                        if not content:
                            continue

                        if verbose:
                            print(f"\nChecking line {i+1}: {content[:80]}...")

                        heuristic_result = check_line_with_heuristics(content)
                        if not heuristic_result:
                            if verbose:
                                print("Heuristic: no potential secret found.")
                            continue

                        # If regex matched and no LLM needed, add directly
                        send_to_llm = heuristic_result.pop("requires_llm_check")
                        if ignore_llms:
                            send_to_llm = False

                        if verbose:
                            print(f"Heuristic result: {heuristic_result}")
                            if send_to_llm:
                                print("Heuristic: send to LLM for further analysis.")
                            else:
                                print("Heuristic: strong enough, adding directly.")

                        base_finding = {
                            "commit_hash": commit.hexsha,
                            "file_path": file_path,
                            "snippet": content,
                        }

                        if not send_to_llm:
                            base_finding.update(heuristic_result)
                            findings.append(base_finding)
                        else:
                            llm_lines.append(i)

                # Merge overlapping LLM line ranges and analyze once per merged snippet
                if llm_lines:
                    llm_lines.sort()
                    merged_ranges = []
                    start = llm_lines[0]
                    end = llm_lines[0]

                    for idx in llm_lines[1:]:
                        if idx <= end + NUMBER_OF_CONTEXT_LINES:  
                            end = idx
                        else:
                            merged_ranges.append((max(0, start-NUMBER_OF_CONTEXT_LINES), min(len(lines), end+NUMBER_OF_CONTEXT_LINES)))
                            start = end = idx
                    merged_ranges.append((max(0, start-NUMBER_OF_CONTEXT_LINES), min(len(lines), end+NUMBER_OF_CONTEXT_LINES)))

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

    except (exc.GitCommandError) as e:
        raise Exception(f"Error processing repository: {str(e)}")
    finally:
        if repo:
            repo.close()

        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, onerror=handle_rm_error)

    return findings