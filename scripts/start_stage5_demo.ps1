[CmdletBinding()]
param(
    [string]$PythonExe
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$demoBatteryId = 'STAGE5-DEMO'
$apiBase = 'http://127.0.0.1:8000'

function Stop-Demo([string]$Message) {
    Write-Error "Stage 5 demo launcher: $Message"
    exit 1
}

# Use an explicitly supplied executable when requested. Otherwise preserve
# the active environment, worktree environments, and PATH fallback order.
$selectedPythonExe = $null
if ($PSBoundParameters.ContainsKey('PythonExe')) {
    if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
        Stop-Demo "The supplied Python executable was not found: '$PythonExe'."
    }
    $selectedPythonExe = (Resolve-Path -LiteralPath $PythonExe).Path
} else {
    if ($env:VIRTUAL_ENV) {
        $candidate = Join-Path $env:VIRTUAL_ENV 'Scripts/python.exe'
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            $selectedPythonExe = $candidate
        } else {
            Stop-Demo "VIRTUAL_ENV is set, but its Python executable was not found at '$candidate'."
        }
    }

    if (-not $selectedPythonExe) {
        foreach ($environmentName in @('.venv', '.venv311')) {
            $candidate = Join-Path $repoRoot "$environmentName/Scripts/python.exe"
            if (Test-Path -LiteralPath $candidate -PathType Leaf) {
                $selectedPythonExe = $candidate
                break
            }
        }
    }

    if (-not $selectedPythonExe) {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCommand) {
            Stop-Demo 'No Python executable was found. Activate the project environment or install Python on PATH.'
        }
        $selectedPythonExe = $pythonCommand.Source
    }
}
$pythonExe = $selectedPythonExe

# Refuse to attach the demo to any already running API process. If the demo ID
# is present, report that explicitly; otherwise report the port conflict.
$portCheck = [System.Net.Sockets.TcpClient]::new()
try {
    $connect = $portCheck.BeginConnect('127.0.0.1', 8000, $null, $null)
    if ($connect.AsyncWaitHandle.WaitOne(300) -and $portCheck.Connected) {
        try {
            $null = Invoke-RestMethod -Method Get -Uri "$apiBase/twin/$demoBatteryId/state" -TimeoutSec 2
            Stop-Demo "Battery Twin '$demoBatteryId' is already registered on port 8000. No Twin was changed. Stop that API or choose a new demo ID."
        } catch {
            if ($_.Exception.Message -like 'Stage 5 demo launcher:*') { throw }
            $statusCode = $null
            if ($_.Exception.Response) {
                try { $statusCode = [int]$_.Exception.Response.StatusCode } catch { }
            }
            if ($statusCode -eq 404) {
                Stop-Demo "Port 8000 is already serving an API and '$demoBatteryId' is not registered there. Refusing to use or replace that process; stop it before launching this demo."
            }
            Stop-Demo "Port 8000 is occupied, but '$demoBatteryId' registration could not be verified ($($_.Exception.Message)). No process was started."
        }
    }
} finally {
    $portCheck.Dispose()
}

$adaptiveEnvironmentNames = @(
    'VOLTTWIN_ADAPTIVE_MINIMUM_GAP',
    'VOLTTWIN_ADAPTIVE_EPSILON_SOH',
    'VOLTTWIN_ADAPTIVE_POLICY_VERSION',
    'VOLTTWIN_ADAPTIVE_DB_PATH'
)
$originalAdaptiveEnvironment = @{}
foreach ($name in $adaptiveEnvironmentNames) {
    $originalAdaptiveEnvironment[$name] = [System.Environment]::GetEnvironmentVariable(
        $name,
        [System.EnvironmentVariableTarget]::Process
    )
}
Push-Location $repoRoot
try {
    $pythonVersion = & $pythonExe --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Stop-Demo "Could not run the selected Python executable '$pythonExe': $pythonVersion"
    }
    $uvicornVersion = & $pythonExe -m uvicorn --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Stop-Demo "Uvicorn is unavailable in '$pythonExe'. Activate the existing VoltTwin environment and retry. Details: $uvicornVersion"
    }

    $adaptiveDb = Join-Path $repoRoot 'data/stage5-demo/adaptive_evaluation.db'
    $env:VOLTTWIN_ADAPTIVE_MINIMUM_GAP = '3'
    $env:VOLTTWIN_ADAPTIVE_EPSILON_SOH = '0.01'
    $env:VOLTTWIN_ADAPTIVE_POLICY_VERSION = 'volttwin-demo-v1'
    $env:VOLTTWIN_ADAPTIVE_DB_PATH = $adaptiveDb

    Write-Host 'Starting VoltTwin Stage 5 demonstration backend.'
    Write-Host "Worktree: $repoRoot"
    Write-Host "Python: $pythonExe ($pythonVersion)"
    Write-Host "Demo battery ID: $demoBatteryId"
    Write-Host 'The new process will start with a fresh in-memory TwinRegistry.'
    Write-Host 'Adaptive demo values: minimum gap=3; epsilon SOH=0.01; policy=volttwin-demo-v1.'
    Write-Host 'These are illustrative demo values, not calibrated or operationally approved thresholds.'
    Write-Host "Adaptive database: $adaptiveDb"
    Write-Host 'Starting exactly one Uvicorn worker. Press Ctrl+C to stop the backend.'

    & $pythonExe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --workers 1
    $serverExitCode = $LASTEXITCODE
    if ($serverExitCode -ne 0) {
        Stop-Demo "Uvicorn exited with code $serverExitCode. Review the backend output above for startup/configuration details."
    }
} catch {
    if ($_.Exception.Message -like 'Stage 5 demo launcher:*') { throw }
    Stop-Demo "Startup/configuration failed: $($_.Exception.Message)"
} finally {
    try {
        foreach ($name in $adaptiveEnvironmentNames) {
            [System.Environment]::SetEnvironmentVariable(
                $name,
                $originalAdaptiveEnvironment[$name],
                [System.EnvironmentVariableTarget]::Process
            )
        }
    } finally {
        Pop-Location
    }
}
