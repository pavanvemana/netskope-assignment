#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER netskope WITH PASSWORD 'nts12x';
	CREATE DATABASE customer_support;
	GRANT ALL PRIVILEGES ON DATABASE customer_support TO netskope;
EOSQL
