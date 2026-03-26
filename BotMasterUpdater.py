# -*- coding: utf-8 -*-
"""
Utilitaire de mise à jour : télécharge le nouvel exe à la place de BotMaster.exe
et relance l'application. Lancé par BotMaster.exe après confirmation utilisateur.
Packaging conseillé : pyinstaller --onefile --windowed --name BotMasterUpdater BotMasterUpdater.py
"""
import argparse
import os
import sys
import time
import urllib.request


def _windows_detach_flags():
    import subprocess

    flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    if hasattr(subprocess, "CREATE_BREAKAWAY_FROM_JOB"):
        flags |= subprocess.CREATE_BREAKAWAY_FROM_JOB
    return flags


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target-exe", required=True, help="Chemin absolu de BotMaster.exe à remplacer")
    p.add_argument("--download-url", required=True)
    p.add_argument("--version", default="", help="Libellé de version (informationnel)")
    args = p.parse_args()

    target = os.path.abspath(args.target_exe)
    exe_dir = os.path.dirname(target)
    base = os.path.basename(target)
    tmp_dl = os.path.join(exe_dir, f".{base}.part")
    bak = target + ".old"

    time.sleep(1.2)

    req = urllib.request.Request(
        args.download_url,
        headers={"User-Agent": "BotMasterUpdater/1.0"},
    )
    with urllib.request.urlopen(req, timeout=900) as resp:
        data = resp.read()

    with open(tmp_dl, "wb") as f:
        f.write(data)

    for _ in range(120):
        try:
            if os.path.isfile(bak):
                os.remove(bak)
            break
        except OSError:
            time.sleep(0.25)

    if os.path.isfile(target):
        for _ in range(120):
            try:
                os.replace(target, bak)
                break
            except OSError:
                time.sleep(0.25)
        else:
            sys.exit(1)

    for _ in range(120):
        try:
            os.replace(tmp_dl, target)
            break
        except OSError:
            time.sleep(0.25)
    else:
        sys.exit(2)

    if sys.platform == "win32":
        import subprocess

        subprocess.Popen(
            [target],
            cwd=exe_dir,
            creationflags=_windows_detach_flags(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
    else:
        import subprocess

        subprocess.Popen([target], cwd=exe_dir, close_fds=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
