FROM postgres:13.3

COPY compose/outside_db/sms_item_init.sql /docker-entrypoint_init.d/

EXPOSE 5432/tcp