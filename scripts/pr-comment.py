#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
from pathlib import Path

API = "https://api.github.com"
# Hidden marker: it is how the next run finds this comment instead of adding one.
MARKER = "<!-- pr-preview-env -->"


def request(path, method="GET", payload=None):
    req = urllib.request.Request(API + path, method=method)
    req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    req.add_header("Accept", "application/vnd.github+json")
    body = None
    if payload is not None:
        body = json.dumps(payload).encode()
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, body) as res:
        return json.load(res)


def find_comment(repo, pr):
    page = 1
    while True:
        comments = request(f"/repos/{repo}/issues/{pr}/comments?per_page=100&page={page}")
        for comment in comments:
            if comment["body"].startswith(MARKER):
                return comment["id"]
        if len(comments) < 100:
            return None
        page += 1


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: pr-comment.py <pr-number> <body-file>")
    pr, body_file = sys.argv[1], sys.argv[2]
    repo = os.environ["GITHUB_REPOSITORY"]
    body = MARKER + "\n" + Path(body_file).read_text()

    comment_id = find_comment(repo, pr)
    if comment_id:
        request(f"/repos/{repo}/issues/comments/{comment_id}", "PATCH", {"body": body})
        print(f"updated comment {comment_id}")
    else:
        request(f"/repos/{repo}/issues/{pr}/comments", "POST", {"body": body})
        print("created comment")


if __name__ == "__main__":
    main()
