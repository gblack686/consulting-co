#!/bin/zsh
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"

# Wake from screensaver with mouse movement
steer drag --from-x 100 --from-y 100 --to-x 960 --to-y 540
sleep 3

echo "=== AFTER WAKE ==="
SHOT1=$(steer see --json 2>&1 | python3 ~/parse-steer.py)
echo "$SHOT1"

# Save screenshot
steer see --json 2>&1 | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d['screenshot'])" > /tmp/wake-shot.txt

sleep 2

# Now click to make sure password field is focused
steer click --x 960 --y 540
sleep 2

echo "=== AFTER CLICK ==="
steer see --json 2>&1 | python3 ~/parse-steer.py

# Type password char by char
steer hotkey shift+b
sleep 0.1
steer hotkey shift+1
sleep 0.1
steer hotkey g
sleep 0.1
steer hotkey b
sleep 0.1
steer hotkey 0
sleep 0.1
steer hotkey y
sleep 0.1
steer hotkey 9
sleep 0.1
steer hotkey 2
sleep 1

steer hotkey return
sleep 5

echo "=== AFTER LOGIN ==="
steer see --json 2>&1 | python3 ~/parse-steer.py
