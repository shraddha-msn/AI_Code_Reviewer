import os
import re
from typing import Optional

import httpx

GITHUB_API = "https://api.github.com"

CODE_EXTS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".go", ".rs", ".java", ".kt", ".scala",
    ".rb", ".php", ".cs", ".swift",
    ".c", ".cc", ".cpp", ".h", ".hpp",
    ".sh", ".bash", ".zsh",
    ".sql", ".lua", ".r",
}

MAX_FILE_BYTES = 50_000
MAX_TOTAL_BYTES = 200_000
MAX_FILES = 30


class GitHubError(Exception):
    pass


def parse_repo_url(url: str) -> tuple[str, str]:
    pattern = r"https?://github\.com/([^/\s]+)/([^/\s]+?)(?:\.git)?(?:/.*)?$"
    m = re.match(pattern, url.strip())
    if not m:
        raise ValueError("Invalid GitHub URL. Expected https://github.com/<owner>/<repo>")
    return m.group(1), m.group(2)


def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json", "User-Agent": "ai-code-reviewer"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


async def _get_default_branch(owner: str, repo: str, client: httpx.AsyncClient) -> str:
    r = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=_headers())
    if r.status_code == 404:
        raise GitHubError(f"Repository {owner}/{repo} not found or private")
    r.raise_for_status()
    return r.json().get("default_branch", "main")


async def _list_tree(owner: str, repo: str, branch: str, client: httpx.AsyncClient) -> list[dict]:
    r = await client.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
        headers=_headers(),
    )
    r.raise_for_status()
    data = r.json()
    if data.get("truncated"):
        # Tree was too large; we'll work with what we got
        pass
    return data.get("tree", [])


async def _fetch_raw(owner: str, repo: str, path: str, branch: str, client: httpx.AsyncClient) -> Optional[str]:
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    r = await client.get(raw_url)
    if r.status_code != 200:
        return None
    return r.text


def _is_code_file(path: str) -> bool:
    lower = path.lower()
    if any(part in lower for part in ("/node_modules/", "/dist/", "/build/", "/.git/", "/vendor/", "/__pycache__/")):
        return False
    return any(lower.endswith(ext) for ext in CODE_EXTS)


async def fetch_repo_code(repo_url: str) -> dict:
    owner, repo = parse_repo_url(repo_url)
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        branch = await _get_default_branch(owner, repo, client)
        tree = await _list_tree(owner, repo, branch, client)

        candidates = [
            entry for entry in tree
            if entry.get("type") == "blob"
            and _is_code_file(entry.get("path", ""))
            and entry.get("size", 0) <= MAX_FILE_BYTES
        ]
        candidates.sort(key=lambda e: e.get("size", 0))

        files: list[dict] = []
        total = 0
        for entry in candidates:
            if len(files) >= MAX_FILES or total >= MAX_TOTAL_BYTES:
                break
            path = entry["path"]
            content = await _fetch_raw(owner, repo, path, branch, client)
            if not content:
                continue
            size = len(content.encode("utf-8", errors="ignore"))
            if total + size > MAX_TOTAL_BYTES:
                continue
            files.append({"path": path, "content": content})
            total += size

        return {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "files": files,
            "total_bytes": total,
        }
