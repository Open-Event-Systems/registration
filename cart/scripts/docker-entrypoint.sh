#!/bin/sh
set -e

alembic upgrade head
exec oes-cart-service "$@"
