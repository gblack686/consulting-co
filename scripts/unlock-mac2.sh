#!/bin/zsh
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"

# Wake screen first with a mouse move + click
steer click --x 960 --y 540
sleep 2

# Check current state via screenshot
echo "=== STATE 1 ==="
steer see --json 2>&1 | python3 ~/parse-steer.py

# Maybe we need to move mouse to wake from screensaver first
# Press space to wake, then wait
steer hotkey space
sleep 3

echo "=== STATE 2 ==="
steer see --json 2>&1 | python3 ~/parse-steer.py

# Now type password char by char using hotkeys
# Password: B!gb0y92
steer hotkey shift+b
sleep 0.2
steer hotkey shift+1
sleep 0.2
steer hotkey g
sleep 0.2
steer hotkey b
sleep 0.2
steer hotkey 0
sleep 0.2
steer hotkey y
sleep 0.2
steer hotkey 9
sleep 0.2
steer hotkey 2
sleep 1

echo "=== STATE 3 (after typing) ==="
steer see --json 2>&1 | python3 ~/parse-steer.py

# Press enter
steer hotkey return
sleep 5

echo "=== STATE 4 (after enter) ==="
steer see --json 2>&1 | python3 ~/parse-steer.py
