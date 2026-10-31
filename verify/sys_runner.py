"""Run bash scripts in a real Linux (a WSL Debian distro, or Docker) as an ordinary user.

Used to record the real command output shown on Systems Mastery pages and to verify the lab scripts.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import uuid

WSL_DISTRO = os.environ.get("SYS_WSL_DISTRO", "Debian")


def _wsl_has_distro():
    try:
        r = subprocess.run(["wsl", "-l", "-q"], capture_output=True, timeout=30)
        names = r.stdout.decode("utf-16-le", "ignore").replace("\x00", "").split()
        return WSL_DISTRO in names
    except Exception:
        return False


def backend():
    if sys.platform != "win32":
        return "local"
    return "wsl" if _wsl_has_distro() else None


def _to_wsl(path):
    drive, rest = os.path.splitdrive(os.path.abspath(path))
    return "/mnt/" + drive[0].lower() + rest.replace("\\", "/")


def run_bash(files, entry, timeout=240):
    """Write files (name -> text) into a temp folder and run `bash entry` there. Returns (returncode, output)."""
    be = backend()
    if be is None:
        raise RuntimeError("no Linux backend (install a WSL Debian distro: wsl --install -d Debian)")
    base = os.path.join(tempfile.gettempdir(), "sysrec")
    os.makedirs(base, exist_ok=True)
    d = os.path.join(base, uuid.uuid4().hex[:8])
    os.makedirs(d)
    try:
        for name, text in files.items():
            with open(os.path.join(d, name), "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        if be == "wsl":
            cmd = ["wsl", "-d", WSL_DISTRO, "-u", "learner", "--cd", "/tmp", "--", "bash", _to_wsl(os.path.join(d, entry))]
        else:
            cmd = ["bash", os.path.join(d, entry)]
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL)
        out = (r.stdout + r.stderr).decode("utf-8", "replace").replace("\x00", "")
        return r.returncode, out
    finally:
        shutil.rmtree(d, ignore_errors=True)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()
