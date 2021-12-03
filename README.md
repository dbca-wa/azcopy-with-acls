# azcopy-with-acls
Container/Docker build of a utility to use azcopy to backup or restore a volume from a azure blob storage location with a sas token.

As the container is just a docker image, it can backup/restore any posix volume available to docker, to/from blob storage. This means you can e.g. backup a volume accessible to a local developer, and restore it to a managed kubernetes environment, or backup a production database in kubernetes and restore it locally using docker or similar for development.

Note that `SAS_TOKEN` is not required if `REMOTE_PATH` includes the sas token (i.e. is a full sas url).

## Backing up a volume
Using docker:
```bash
docker run -e REMOTE_PATH='https://<account>.blob.core.windows.net/<container>/2021-backups/myvol1.tar.lz4?sp=racwdl&st=2021-09-10T06:28:07Z&se=2021-09-11T14:28:07Z&spr=https&sv=2020-08-04&sr=c&sig=<secretsig>' -e ACTION=backup -v myvol1:/mnt/local ghcr.io/dbca-wa/azcopy-with-acls:main
```
Or using kubernetes, deploy the following job using kubectl or equivalent
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: backup-myvol1
spec:
  template:
    backoffLimit: 1
    spec:
      restartPolicy: Never
      containers:
        - name: backup-myvol1
          imagePullPolicy: Always
          image: 'ghcr.io/dbca-wa/azcopy-with-acls:main'
          env:
            - name: ACTION
              value: backup
            - name: REMOTE_PATH
              value: 'https://<account>.blob.core.windows.net/<container>/2021-backups/myvol1.tar.lz4?sp=racwdl&st=2021-09-10T06:28:07Z&se=2021-09-11T14:28:07Z&spr=https&sv=2020-08-04&sr=c&sig=<secretsig>'
          volumeMounts:
            - name: myvol1
              mountPath: /mnt/local
      volumes:
        - name: myvol1
          persistentVolumeClaim:
            claimName: pvc-myvol1
```

## Restoring a volume
Note by default will only restore to empty volumes. To force clobbering existing data set the action to `restore_clobber`.

Using docker
```bash
docker run -e REMOTE_PATH='https://<account>.blob.core.windows.net/<container>/2021-backups/myvol1.tar.lz4?sp=racwdl&st=2021-09-10T06:28:07Z&se=2021-09-11T14:28:07Z&spr=https&sv=2020-08-04&sr=c&sig=<secretsig>' -e ACTION=restore -v myvol1:/mnt/local ghcr.io/dbca-wa/azcopy-with-acls:main
```
Or using kubernetes, deploy the following pvc and job using kubectl or equivalent (set size sensibly based on your source, in this case source was 250Gi)
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-myvol1
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 300Gi
```
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: restore-myvol1
spec:
  template:
    backoffLimit: 1
    spec:
      restartPolicy: Never
      containers:
        - name: restore-myvol1
          imagePullPolicy: Always
          image: 'ghcr.io/dbca-wa/azcopy-with-acls:main'
          env:
            - name: ACTION
              value: restore
            - name: REMOTE_PATH
              value: 'https://<account>.blob.core.windows.net/<container>/2021-backups/myvol1.tar.lz4?sp=racwdl&st=2021-09-10T06:28:07Z&se=2021-09-11T14:28:07Z&spr=https&sv=2020-08-04&sr=c&sig=<secretsig>'
          volumeMounts:
            - name: myvol1
              mountPath: /mnt/local
      volumes:
      - name: myvol1
        persistentVolumeClaim:
          claimName: pvc-myvol1
```
