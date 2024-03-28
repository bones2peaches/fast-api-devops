FROM alpine

RUN apk update
RUN apk add nginx nginx-mod-http-nchan nginx-mod-http-headers-more apache2-utils

EXPOSE 80 443
RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


ENTRYPOINT ["/entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]