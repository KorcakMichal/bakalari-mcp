# Define the name of the Claude Desktop application process
$processName = "Claude"  # Replace this with the actual process name for Claude Desktop if different

# Stop any running tasks related to Claude
Get-Process | Where-Object { $_.Name -like "*Claude*" } | ForEach-Object { $_.Kill() }

# Wait for a few seconds to ensure the tasks are fully terminated
Start-Sleep -Seconds 5

# Restart Claude Desktop (make sure the path to the app is correct)
$ClaudePath = "C:\Users\Michal\AppData\Local\AnthropicClaude\claude.exe"  # Replace with the actual path to the Claude app
Start-Process $ClaudePath

Write-Host "Claude has been restarted successfully."
