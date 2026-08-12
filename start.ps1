# Start Flask backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python app.py"

# Start frontend server
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; python -m http.server 5500"

# Open the app in the default browser
Start-Sleep -Seconds 2
Start-Process "http://localhost:5500"