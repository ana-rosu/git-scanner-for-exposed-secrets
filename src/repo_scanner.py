import os
import shutil
from git import Repo, exc
from src.analysis.heuristics import check_line_with_heuristics
from src.analysis.llm_analyzer import get_llm_analysis
from src.utils import handle_rm_error

def scan_repository(repo_path, n_commits):
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

            for diff in diffs:
                if not diff.diff:
                    continue

                diff_text = diff.diff.decode('utf-8', errors='ignore')
                for line in diff_text.split('\n'):
                    if line.startswith('+'):
                        content = line[1:].strip()
                        if not content:
                            continue

                        heuristic_result = check_line_with_heuristics(content)
                        if heuristic_result:
                            base_finding = {
                                "commit_hash": commit.hexsha,
                                "file_path": diff.a_path or diff.b_path,
                                "snippet": content,
                            }

                            if heuristic_result.pop("requires_llm_check", False):
                                llm_result = get_llm_analysis(content, commit.message, base_finding["file_path"])
                                if llm_result:
                                    base_finding.update(llm_result)
                                    findings.append(base_finding)
                            else:
                                # If a regex matched, add it directly
                                base_finding.update(heuristic_result)
                                findings.append(base_finding)

    except (exc.GitCommandError) as e:
        raise Exception(f"Error processing repository: {str(e)}")
    finally:
        if repo:
            repo.close()

        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, onerror=handle_rm_error)

    return findings