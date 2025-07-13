FROM postgres:14.18-bookworm
ADD scripts/postgres_db_init.sh /docker-entrypoint-initdb.d/
EXPOSE 5432