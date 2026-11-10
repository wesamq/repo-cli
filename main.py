import argparse
import json
import sys

import httpx


def fetch_repos(username: str) -> list[dict]:
    """Ask GitHub for a user's public repos."""
    url = f"https://api.github.com/users/{username}/repos"
    response = httpx.get(url, params={"sort": "updated"}, timeout=10)
    response.raise_for_status()  # error on 404, 500, etc.
    return response.json()


def summarize(repo: dict) -> dict:
    """Keep only the fields we care about."""
    return {
        "name": repo["name"],
        "language": repo["language"] or "n/a",
        "stars": repo["stargazers_count"],
        "url": repo["html_url"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="List a GitHub user's repos.")
    parser.add_argument("username", help="GitHub username")
    parser.add_argument("--save", help="Save results to a JSON file")
    parser.add_argument("--language", help="Prog language")
    args = parser.parse_args()

    try:
        repos = fetch_repos(args.username)
    except httpx.HTTPStatusError as error:
        print(f"GitHub error: {error.response.status_code}")
        sys.exit(1)
    except httpx.RequestError:
        print("Network error. Check your connection.")
        sys.exit(1)

    summaries = [summarize(r) for r in repos if not r["fork"]]

    for repo in summaries:
        print(f"{repo['name']:<25} {repo['language']:<12} ⭐ {repo['stars']}")

    if args.save:
        with open(args.save, "w", encoding="utf-8") as f:
            json.dump(summaries, f, indent=2)
        print(f"\nSaved {len(summaries)} repos to {args.save}")


if __name__ == "__main__":
    main()