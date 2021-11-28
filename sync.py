#!/usr/bin/env python3
import os
from subprocess import run, check_output
from sys import exit

local = os.path.abspath(os.environ.get("LOCAL_PATH", "/mnt/local"))
sas = os.environ["SAS_TOKEN"]
remote = os.environ["REMOTE_PATH"] + ".tar.lz4"
action = os.environ["ACTION"]
remoteurl = f'"{remote}?{sas}"'

os.chdir(local)

if action == "backup":
    print(f"Backing up '{local}' ({size}) to '{remote}'")
    size = check_output(["du", "-sh"]).split(" ")[0]
    run(f"tar -cf - . | pv --size {size} | lz4 | azcopy cp {remoteurl} --from-to=PipeBlob", shell=True)
elif action.startswith("restore"):
    # head request to a blob URL returns its size
    size = check_output(f"curl -s --head {remoteurl}" + " | awk '$1 == \"Content-Length:\" {print $2}' | tr -d '\r' | numfmt --to=iec", shell=True).split(" ")[0]
    print(f"Restoring '{remote}' ({size} compressed with lz4) to '{local}'")
    if os.path.exists("lost+found"): # handle new filesystems
        os.rmdir("lost+found")
    if any(os.scandir(local)) and action != "restore_clobber":
        run(["ls", "-lah"])
        exit(f"Files in local path {local}, refusing to restore")
    run(f"azcopy cp {remoteurl} --from-to=BlobPipe | pv --size {size} | tar -I lz4 -xvf -", shell=True)
else:
    exit("Please set ACTION (backup or restore), REMOTE_PATH (blob container url) and SAS_TOKEN to sync a volume.")
