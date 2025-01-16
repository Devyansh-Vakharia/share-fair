#!/bin/bash

if [ $1 == "start" ]
then
    poetry run python -m app.main
fi