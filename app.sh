#!/bin/bash
gunicorn datalakecadg.wsgi:application --workers=12 --threads=2 --bind=0.0.0.0:8080 -t 180 --log-file -
