#!/usr/bin/env bash

LOG_FILE="$HOME/logs/rubcalsync/sync.log"

MAX_SIZE=$((1024 * 1024)) # 1 MB

if [ -f "$LOG_FILE" ] && [ "$(stat -c%s "$LOG_FILE")" -gt "$MAX_SIZE" ]; then
    mv "$LOG_FILE" "${LOG_FILE}.$(date +%Y%m%d-%H%M%S)"
fi

{
    echo "========================================"
    echo "Started: $(date)"
    echo

    cd ~/Projects/RubCalSync
    source .venv/bin/activate

    echo "RUB → Google"
    rubcalsync \
        --source-provider RubSOGo \
        --source-calendar "Persönlicher Kalender" \
        --target-provider Google \
        --target-calendar "RUB Calendar"

    echo

    echo "Google → RUB"
    rubcalsync \
        --source-provider Google \
        --source-calendar "RUB Calendar" \
        --target-provider RubSOGo \
        --target-calendar "Persönlicher Kalender"

    echo
    echo "Finished: $(date)"
    echo "========================================"
    echo

} >> "$LOG_FILE" 2>&1

exit 0