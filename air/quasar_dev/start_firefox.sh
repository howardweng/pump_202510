#!/bin/bash

# Show Zenity message immediately in the background
zenity --info --title="啟動中" --text="<span font='30' weight='bold'>程式啟動中，請稍候...</span>" &
# Save Zenity's process ID (PID)
ZENITY_PID=$!

# Wait for 10 seconds to allow the system to fully boot
sleep 10

# Launch Firefox (maximized) pointing to http://localhost:3000
#/usr/bin/firefox --start-maximized http://localhost:3000 &
/usr/bin/firefox --new-window http://localhost:3000

# Kill Zenity when Firefox launches
kill $ZENITY_PID
