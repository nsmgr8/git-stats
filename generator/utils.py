import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(HERE)


def run(cmd: str) -> subprocess.CompletedProcess:
    """
    A convenient wrapper around subprocess.run()
    """
    return subprocess.run(cmd, check=True, shell=True, cwd=PROJECT_DIR,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True)


def run_git(workdir, repo, cmd):
    """
    Run a git command in a repo inside the workdir
    """
    return run(f'cd {workdir}/repos/{repo} && git {cmd}')
