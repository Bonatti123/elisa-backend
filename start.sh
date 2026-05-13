#!/usr/bin/env bash
export LD_LIBRARY_PATH=/hdd1/postgres/usr/lib:/hdd1/postgres/usr/lib/postgresql:$LD_LIBRARY_PATH

case "${1:-}" in
  db)
    /hdd1/postgres/usr/bin/pg_ctl -D /hdd1/postgres/data -l /hdd1/postgres/pg.log start
    /hdd1/postgres/usr/bin/pg_ctl -D /hdd1/postgres/data status
    ;;
  stop)
    /hdd1/postgres/usr/bin/pg_ctl -D /hdd1/postgres/data stop
    ;;
  server)
    /hdd1/elisa-backend/venv/bin/uvicorn api.main:app --reload --port 8001
    ;;
  *)
    echo "Uso: $0 {db|stop|server}"
    echo ""
    echo "  $0 db      — Inicia PostgreSQL"
    echo "  $0 stop    — Detiene PostgreSQL"
    echo "  $0 server  — Inicia el servidor API en :8001"
    exit 1
    ;;
esac
