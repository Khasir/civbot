#!/bin/bash
export FLASK_ENV=production
python -um main "$1" "$2"
