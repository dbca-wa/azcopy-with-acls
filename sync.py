#!/usr/bin/env python3
import os
from subprocess import run, check_output
from sys import exit

action = os.environ["ACTION"]
local = os.path.abspath(os.environ.get("LOCAL_PATH", "/mnt/local"))
print(f"Local dir: {local}")
sas = os.environ.get("SAS_TOKEN", False)
remote = os.environ["REMOTE_PATH"]
if remote.find(".tar.lz4") < 0:
    if not remote.find("?"): # only autoadd suffix if not a full url
        remote += ".tar.lz4"
if sas:
    remoteurl = f'"{remote}?{sas}"'
else:
    remoteurl = f'"{remote}"'
print(f"Remote blob URL: {remoteurl}")

os.chdir(local)

if action == "backup":
    sbytes = check_output("du -sb | awk '{print $1}'", shell=True).decode("utf8").strip()
    size = check_output(f"echo {sbytes} | numfmt --to=iec", shell=True).decode("utf8").strip()
    print(f"Backing up '{local}' ({size}) to '{remote}'")
    run(f"tar -cf - . | pv -i 10 -s {sbytes} | lz4 | azcopy cp {remoteurl} --from-to=PipeBlob", shell=True)
elif action.startswith("restore"):
    # head request to a blob URL returns its size
    sbytes = check_output(f"curl -s --head {remoteurl}" + " | awk '$1 == \"Content-Length:\" {print $2}' | tr -d '\r'", shell=True).decode("utf8").strip()
    if not sbytes:
        exit(f"Remote blob '{remote}' does not exist...")
    size = check_output(f"echo {sbytes} | numfmt --to=iec", shell=True).decode("utf8").strip()
    print(f"Restoring '{remote}' ({size} tar.lz4) to '{local}'")
    if os.path.exists("lost+found"): # handle new filesystems
        os.rmdir("lost+found")
    if any(os.scandir(local)) and action != "restore_clobber":
        run(["ls", "-lah"])
        exit(f"Files in local path {local}, refusing to restore")
    run(f"azcopy cp {remoteurl} --from-to=BlobPipe | pv -i 10 -s {sbytes} | tar -I lz4 -xf -", shell=True)
else:
    exit("Please set ACTION (backup or restore), REMOTE_PATH (blob container url) and SAS_TOKEN to sync a volume.")
