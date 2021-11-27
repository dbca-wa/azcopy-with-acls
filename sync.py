#!/usr/bin/env python3
import os
from subprocess import run
from sys import exit

local = os.path.abspath(os.environ.get("LOCAL_PATH", "/mnt/local"))
sas = os.environ["SAS_TOKEN"]
remote = os.environ["REMOTE_PATH"] + ".tar.lz4"
action = os.environ["ACTION"]

os.chdir(local)

if action == "backup":
    run(f"tar -I lz4 -cvf - . | azcopy cp \"{remote}?{sas}\" --from-to=PipeBlob", shell=True)
elif action.startswith("restore"):
    if os.path.exists("lost+found"): # handle new filesystems
        os.rmdir("lost+found")
    if any(os.scandir(local)) and action != "restore_clobber":
        run(["ls", "-lah"])
        exit(f"Files in local path {local}, refusing to restore")
    run(f"azcopy cp \"{remote}?{sas}\"  --from-to=BlobPipe | tar -I lz4 -xvf -", shell=True)
else:
    exit("Please set ACTION (backup or restore), REMOTE_PATH (blob container url) and SAS_TOKEN to sync a volume.")
