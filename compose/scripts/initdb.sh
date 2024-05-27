#!/bin/sh
set -e

createdb -U registration -O registration auth
createdb -U registration -O registration cart
createdb -U registration -O registration payment
