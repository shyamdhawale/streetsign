#!/bin/bash

convert "$1" -resize 300x "$1"

exit $?
