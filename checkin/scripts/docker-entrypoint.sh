#!/bin/sh
set -e

alembic upgrade head
exec oes-checkin-service "$@"
