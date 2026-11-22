FROM caddy:2-alpine

WORKDIR /srv
COPY index.html portrait.jpeg /srv/

EXPOSE 8080

CMD ["caddy", "file-server", "--root", "/srv", "--listen", ":8080"]
