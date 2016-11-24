#!/bin/bash


if [ -z "$1" ]; then
    arg='some_date'
else
    arg=$1
fi

echo $arg
