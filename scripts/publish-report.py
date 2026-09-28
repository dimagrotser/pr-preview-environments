#!/usr/bin/env python3
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "e2e" / "playwright-report"
BRANCH = "gh-pages"


def git(*args, cwd=ROOT, check=True):
    return subprocess.run(["git", *args], cwd=cwd, check=check, text=True)


def has_remote_branch():
    probe = subprocess.run(
        ["git", "ls-remote", "--exit-code", "--heads", "origin", BRANCH],
        cwd=ROOT,
        capture_output=True,
    )
    return probe.returncode == 0


def ensure_identity():
    for key, value in (
        ("user.name", "github-actions[bot]"),
        ("user.email", "41898282+github-actions[bot]@users.noreply.github.com"),
    ):
        if subprocess.run(["git", "config", key], cwd=ROOT, capture_output=True).returncode != 0:
            git("config", key, value)


def write_index(work):
    (work / ".nojekyll").touch()
    reports = sorted(
        (d.name for d in work.iterdir() if d.is_dir() and d.name.startswith("pr-")),
        key=lambda name: int(name.removeprefix("pr-")),
    )
    links = "\n".join(f'<li><a href="{name}/">{name}</a></li>' for name in reports)
    (work / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Playwright reports</title>\n'
        f"<h1>Playwright reports</h1><ul>\n{links}\n</ul>\n"
    )


def publish(pr, remove):
    work = Path(tempfile.mkdtemp())
    try:
        if has_remote_branch():
            git("fetch", "--depth=1", "origin", BRANCH)
            git("worktree", "add", "-B", BRANCH, str(work), "FETCH_HEAD")
        elif remove:
            print(f"no {BRANCH} branch, nothing to remove")
            return
        else:
            git("worktree", "add", "--detach", str(work))
            git("checkout", "--orphan", BRANCH, cwd=work)
            git("rm", "-rf", "--quiet", ".", cwd=work, check=False)

        shutil.rmtree(work / f"pr-{pr}", ignore_errors=True)
        if not remove:
            shutil.copytree(REPORT, work / f"pr-{pr}")
        write_index(work)

        git("add", "-A", cwd=work)
        if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=work).returncode == 0:
            print("nothing to publish")
            return
        git("commit", "-m", f"report: pr-{pr} {'removed' if remove else 'published'}", cwd=work)

        # Parallel pull requests push to the same branch, so retry on a lost race.
        for attempt in (1, 2, 3):
            if git("push", "origin", BRANCH, cwd=work, check=False).returncode == 0:
                return
            print(f"push retry {attempt}")
            git("pull", "--rebase", "origin", BRANCH, cwd=work)
        sys.exit("could not push the report")
    finally:
        git("worktree", "remove", "--force", str(work), check=False)


def main():
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        sys.exit("usage: publish-report.py <pr-number> [--remove]")
    ensure_identity()
    publish(sys.argv[1], "--remove" in sys.argv[2:])


if __name__ == "__main__":
    main()
