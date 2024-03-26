FROM alpine

RUN apk update
RUN apk add nginx nginx-mod-http-nchan nginx-mod-http-headers-more

EXPOSE 80 443
RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf
CMD ["nginx" , "-g" , "daemon off;"]