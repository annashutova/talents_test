#!/usr/bin/env bash

echo "Start service"

# migrate database
python alembic_wrapper.py upgrade head

# load fixtures
python scripts/load_data.py \
fixtures/talents/talents.trait.json \
fixtures/talents/talents.question.json \
fixtures/talents/talents.answer.json \
fixtures/talents/talents.interpretation.json

exec uvicorn webapp.main:create_app --host="$BIND_IP" --port="$BIND_PORT"
