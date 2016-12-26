#!/bin/bash
set -e

psql -h $POSTGRES_HOST -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" <<-EOSQL
	DROP DATABASE bigleague;
	CREATE DATABASE bigleague;
EOSQL
