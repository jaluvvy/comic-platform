$nodeDir = 'C:\Users\Nam.le\AppData\Local\Temp\kilo\nodejs\node-v22.15.0-win-x64'
$env:PATH = "$nodeDir;$env:PATH"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Write-Host "Node.js environment ready:"
node --version
npm --version
