import os


class Config:
    pr = os.environ.get("PR_NUMBER", "local")
    commit = os.environ.get("GIT_SHA", "dev")
    built_at = os.environ.get("BUILT_AT")


config = Config()
