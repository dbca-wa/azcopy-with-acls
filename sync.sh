#!/bin/bash
if [[ -z "${BACKUP_SASURL}" ]]; then
    getfacl -R /mnt/backup /mnt/backup.acls
    azcopy sync /mnt/backup "${BACKUP_SASURL}" --mirror-mode --recursive --delete-destination --put-md5
    azcopy copy /mnt/backup.acls "${BACKUP_SASURL}.acls" --overwrite
elif [[ -z "${RESTORE_SASURL}" ]]; then
    azcopy copy "${RESTORE_SASURL}.acls" /mnt/restore.acls --overwrite
    azcopy sync "${RESTORE_SASURL}" /mnt/restore
    cd /mnt/restore
    setfacl --restore=/mnt/restore.acls
else
  echo "Please set BACKUP_SASURL (to backup /mnt/backup) or RESTORE_SASURL (for restoring to /mnt/restore)"
fi
