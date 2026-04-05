#!/bin/zsh
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"

# Clear any previous failed attempt
steer hotkey escape
sleep 1

# Write password to clipboard (the ! won't be escaped in a script)
steer clipboard write 'B!gb0y92'
sleep 1

# Click the password field area
steer click --x 960 --y 600
sleep 1

# Paste password
steer hotkey cmd+v
sleep 1

# Press enter to unlock
steer hotkey return
sleep 5

# Check if we unlocked
steer see --json 2>&1 | python3 ~/parse-steer.py
