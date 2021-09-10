FROM alpine
LABEL org.opencontainers.image.source https://github.dev/dbca-wa/azcopy-with-acls

WORKDIR /usr/local/bin
RUN apk --no-cache add curl acl 
RUN curl -L https://aka.ms/downloadazcopy-v10-linux -o azcopy.tar.gz && tar xvzf azcopy.tar.gz --strip-components=1 && rm azcopy.tar.gz

COPY sync.sh sync.sh
RUN chmod +x sync.sh
CMD ["/usr/local/bin/sync.sh"]