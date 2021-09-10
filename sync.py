#!/usr/bin/env python3
import os
from subprocess import run
from sys import exit

local = os.path.abspath(os.environ.get("LOCAL_PATH", "/mnt/local"))
sas = os.environ["SAS_TOKEN"]
remote = os.environ["REMOTE_PATH"]
action = os.environ["ACTION"]

os.chdir(local)

if action == "backup":
    run(f"getfacl -R . > {local}.acls", shell=True)
    run(["azcopy", "sync", local, f"{remote}?{sas}", "--mirror-mode", "--recursive", "--delete-destination", "true", "--put-md5"])
    run(["azcopy", "copy", f"{local}.acls", f"{remote}.acls?{sas}", "--overwrite", "true"])
elif action.startswith("restore"):
    if os.path.exists("lost+found"): # handle new filesystems
        os.rmdir("lost+found")
    if any(os.scandir(local)) and action != "restore_clobber":
        run(["ls", "-lah"])
        exit(f"Files in local path {local}, refusing to restore")
    run(["azcopy", "copy", f"{remote}.acls?{sas}", f"{local}.acls", "--overwrite", "true"])
    run(["azcopy", "sync", f"{remote}?{sas}", local, "--mirror-mode", "--recursive", "--delete-destination", "true"])
    run(["setfacl", f"--restore={local}.acls"])
else:
    exit("Please set ACTION (backup or restore), REMOTE_PATH (blob container url) and SAS_TOKEN to sync a volume.")
