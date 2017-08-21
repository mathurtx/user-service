#!/bin/bash

rabbitmq-start &
python3.6 manage.py test tests
