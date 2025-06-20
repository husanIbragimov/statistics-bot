#!/bin/bash

# .env fayldan o'qish
export $(grep -v '^#' .env.local | xargs)

# Backup buyrug‘i
pg_dump -c -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_NAME \
> backups/dump_$(date +%d-%m-%Y"_"%H_%M_%S).sql

echo "✅ Backup fayl yaratildi."
