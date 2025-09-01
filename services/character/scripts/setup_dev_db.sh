#!/bin/bash

# Create PostgreSQL user and database
sudo -u postgres psql << EOF
CREATE USER postgres WITH PASSWORD 'postgres';
ALTER USER postgres WITH SUPERUSER;
DROP DATABASE IF EXISTS character_service;
CREATE DATABASE character_service OWNER postgres;
EOF
