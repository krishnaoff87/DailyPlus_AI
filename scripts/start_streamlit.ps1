# Streamlit Startup Script with Port Management (PowerShell)
# Automatically handles port conflicts and launches Streamlit

param(
    [int]$Port = 8501,
    [string]$AppPath = "app/main.py",
    [switch]$NoKill,
    [switch]$NoBrowser,
    [switch]$Help
)

# Display help
if ($Help) {
    Write-Host @"
Streamlit Startup Script with Port Management

USAGE:
    .\start_streamlit.ps1 [-Port <port>] [-AppPath <path>] [-NoKill] [-NoBrowser] [-Help]

OPTIONS:
    -Port <port>        Port to use (default: 8501)
    -AppPath <path>     Path to Streamlit app (default: app/main.py)
    -NoKill             Don't kill existing processes on the port
    -NoBrowser          Run in headless mode (don't open browser)
    -Help               Show this help message

EXAMPLES:
    .\start_streamlit.ps1
    .\start_streamlit.ps1 -Port 8502
    .\start_streamlit.ps1 -NoKill
    .\start_streamlit.ps1 -Port 8501 -NoBrowser

"@
    exit 0
}

# Color output functions
function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
}

# Function to check if port is in use
function Test-PortInUse {
    param([int]$PortNumber)
    
    try {
        $connection = Get-NetTCPConnection -LocalPort $PortNumber -ErrorAction SilentlyContinue
        return $null -ne $connection
    }
    catch {
        return $false
    }
}

# Function to get process using port
function Get-ProcessOnPort {
    param([int]$PortNumber)
    
    try {
        $connection = Get-NetTCPConnection -LocalPort $PortNumber -ErrorAction SilentlyContinue
        if ($connection) {
            $processId = $connection.OwningProcess
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            return @{
                PID = $processId
                Name = $process.ProcessName
                Process = $process
            }
        }
        return $null
    }
    catch {
        return $null
    }
}

# Function to kill process on port
function Stop-ProcessOnPort {
    param(
        [int]$PortNumber,
        [int]$MaxRetries = 3
    )
    
    $retries = 0
    while ($retries -lt $MaxRetries) {
        $processInfo = Get-ProcessOnPort -PortNumber $PortNumber
        
        if ($null -eq $processInfo) {
            Write-Success "Port $PortNumber is now free"
            return $true
        }
        
        Write-Warning "Port $PortNumber is in use by $($processInfo.Name) (PID: $($processInfo.PID))"
        Write-Info "Attempting to stop process... (Attempt $($retries + 1)/$MaxRetries)"
        
        try {
            Stop-Process -Id $processInfo.PID -Force -ErrorAction Stop
            Start-Sleep -Seconds 2
            
            # Verify port is free
            if (-not (Test-PortInUse -PortNumber $PortNumber)) {
                Write-Success "Successfully stopped process on port $PortNumber"
                return $true
            }
        }
        catch {
            Write-Warning "Failed to stop process: $_"
        }
        
        $retries++
        Start-Sleep -Seconds 1
    }
    
    Write-Error "Failed to free port $PortNumber after $MaxRetries attempts"
    return $false
}

# Function to find available port
function Find-AvailablePort {
    param(
        [int]$StartPort,
        [int]$MaxAttempts = 10
    )
    
    for ($i = 0; $i -lt $MaxAttempts; $i++) {
        $testPort = $StartPort + $i
        if (-not (Test-PortInUse -PortNumber $testPort)) {
            Write-Success "Found available port: $testPort"
            return $testPort
        }
    }
    
    return $null
}

# Main script
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  🚀 Streamlit Application Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Validate app path
$appFullPath = Join-Path $PSScriptRoot ".." $AppPath
if (-not (Test-Path $appFullPath)) {
    Write-Error "Error: Streamlit app not found at: $appFullPath"
    exit 1
}

Write-Info "App Path: $AppPath"
Write-Info "Target Port: $Port"
Write-Host ""

# Check if port is in use
$portInUse = Test-PortInUse -PortNumber $Port

if ($portInUse) {
    $processInfo = Get-ProcessOnPort -PortNumber $Port
    Write-Warning "Port $Port is currently in use"
    
    if ($processInfo) {
        Write-Info "Process: $($processInfo.Name) (PID: $($processInfo.PID))"
    }
    
    if (-not $NoKill) {
        Write-Info "Attempting to free port $Port..."
        $freed = Stop-ProcessOnPort -PortNumber $Port
        
        if (-not $freed) {
            Write-Warning "Could not free port $Port, searching for alternative..."
            $alternativePort = Find-AvailablePort -StartPort ($Port + 1)
            
            if ($null -eq $alternativePort) {
                Write-Error "No available ports found"
                exit 1
            }
            
            $Port = $alternativePort
            Write-Info "Using alternative port: $Port"
        }
    }
    else {
        Write-Info "Searching for alternative port (NoKill flag set)..."
        $alternativePort = Find-AvailablePort -StartPort ($Port + 1)
        
        if ($null -eq $alternativePort) {
            Write-Error "No available ports found"
            exit 1
        }
        
        $Port = $alternativePort
        Write-Info "Using alternative port: $Port"
    }
}
else {
    Write-Success "Port $Port is available"
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Starting Streamlit on port $Port" -ForegroundColor Green
Write-Host "  URL: http://localhost:$Port" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

# Build Streamlit command
$streamlitArgs = @(
    "run",
    $AppPath,
    "--server.port", $Port
)

if ($NoBrowser) {
    $streamlitArgs += "--server.headless", "true"
}

# Change to workspace directory
$workspaceDir = Join-Path $PSScriptRoot ".."
Set-Location $workspaceDir

# Launch Streamlit
try {
    Write-Info "Launching Streamlit..."
    Write-Info "Command: python -m streamlit $($streamlitArgs -join ' ')"
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    
    & python -m streamlit @streamlitArgs
    
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Success "`nStreamlit stopped successfully"
    }
    else {
        Write-Warning "`nStreamlit exited with code: $exitCode"
    }
    
    exit $exitCode
}
catch {
    Write-Error "Failed to launch Streamlit: $_"
    exit 1
}

# Made with Bob
