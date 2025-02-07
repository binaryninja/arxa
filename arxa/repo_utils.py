import os
import re
import subprocess
import urllib.parse
from typing import Optional

def extract_github_url(content: str) -> Optional[str]:
    """
    Extract a GitHub URL from text.
    """
    import re
    pattern = r'https?://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9._-]+'
    match = re.search(pattern, content)
    if match:
        return match.group(0)
    return None

def clone_repo(github_url: str, output_dir: str) -> None:
    """
    Clone (or fork & clone) a GitHub repository using the gh CLI.
    """
    repo_name = github_url.rstrip("/").split("/")[-1]
    clone_destination = os.path.join(output_dir, repo_name)
    subprocess.run(["gh", "repo", "fork", github_url, "--clone"], cwd=output_dir, check=True)
    return clone_destination
