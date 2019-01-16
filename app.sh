#!/bin/bash
gunicorn apilabcontas.wsgi:application --bind=0.0.0.0:8080 -t 180 --log-file -
