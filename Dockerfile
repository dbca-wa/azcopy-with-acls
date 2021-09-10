FROM alpine
LABEL org.opencontainers.image.source https://github.dev/dbca-wa/azcopy-with-acls

RUN apk --no-cache add curl acl 
RUN curl -LO https://aka.ms/downloadazcopy-v10-linux && tar xvzf azcopy*.tar.gz --strip-components=1 && mv azcopy /usr/local/bin

COPY sync.sh /usr/local/bin/sync.sh
CMD ["/usr/local/bin/sync.sh"]