#!/usr/bin/env python3
import os
from subprocess import run
from sys import exit

local = os.environ.get("LOCAL_PATH", "/mnt/local")
sas = os.environ["SAS_TOKEN"]
remote = os.environ["REMOTE_PATH"]
action = os.environ["ACTION"]

if action == "backup":
    run(["getfacl", "-R", local, f"{local}.acls"])
    run(["azcopy", "sync", local, f"{remote}?{sas}", "--mirror-mode", "--recursive", "--delete-destination", "--put-md5"])
    run(["azcopy", "copy", f"{local}.acls", f"{remote}.acls?{sas}", "--overwrite"])
elif action == "restore":
    if any(os.scandir(local)):
        exit(f"Files in local path {local}, refusing to restore")
    run(["azcopy", "copy", f"{remote}.acls?{sas}", f"{local}.acls", "--overwrite"])
    run(["azcopy", "sync", f"{remote}?{sas}", local])
    os.chdir(local)
    run(["setfacl", f"--restore={local}.acls"])
else:
    exit("Please set ACTION (backup or restore), REMOTE_PATH (blob container url) and SAS_TOKEN to sync a volume.")
