[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

$ProjectDir = $PSScriptRoot
$BootstrapBin = Join-Path $ProjectDir ".bootstrap\bin"
$VenvDir = Join-Path $ProjectDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$ServerFile = Join-Path $ProjectDir "backend\server.py"
$RequirementsFile = Join-Path $ProjectDir "requirements.txt"
$LogDir = Join-Path $ProjectDir "logs"
$AppPort = 8000
$AppUrl = "http://127.0.0.1:$AppPort"
$HealthUrl = "$AppUrl/api/health"
$OllamaUrl = if ($env:OLLAMA_BASE_URL) { $env:OLLAMA_BASE_URL.TrimEnd("/") } else { "http://127.0.0.1:11434" }
$ChatModel = if ($env:CBT_ASSISTANT_CHAT_MODEL) { $env:CBT_ASSISTANT_CHAT_MODEL } else { "qwen3:8b" }
$EmbedModel = "qwen3-embedding:4b"

function Write-Step {
    param([Parameter(Mandatory = $true)][string]$Message)

    Write-Host ""
    Write-Host "[CBT Assistant] $Message" -ForegroundColor Magenta
}

function Test-Url {
    param([Parameter(Mandatory = $true)][string]$Url)

    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 300
    }
    catch {
        return $false
    }
}

function Wait-ForUrl {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $true)][int]$Attempts
    )

    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        if (Test-Url -Url $Url) {
            return $true
        }
        Start-Sleep -Seconds 1
    }

    return $false
}

function Find-Uv {
    $command = Get-Command uv.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $localUv = Join-Path $BootstrapBin "uv.exe"
    if (Test-Path -LiteralPath $localUv -PathType Leaf) {
        return $localUv
    }

    return $null
}

function Install-Uv {
    $uvExe = Find-Uv
    if ($uvExe) {
        return $uvExe
    }

    Write-Step "Installing the local Python bootstrap (uv)..."
    New-Item -ItemType Directory -Path $BootstrapBin -Force | Out-Null

    $previousInstallDir = $env:UV_UNMANAGED_INSTALL
    try {
        $env:UV_UNMANAGED_INSTALL = $BootstrapBin
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    }
    finally {
        $env:UV_UNMANAGED_INSTALL = $previousInstallDir
    }

    $uvExe = Find-Uv
    if (-not $uvExe) {
        throw "uv was downloaded but uv.exe was not found in $BootstrapBin."
    }

    return $uvExe
}

function Initialize-PythonEnvironment {
    param([Parameter(Mandatory = $true)][string]$UvExe)

    Write-Step "Preparing Python 3.12 and the virtual environment..."

    $venvIsUsable = $false
    if (Test-Path -LiteralPath $VenvPython -PathType Leaf) {
        & $VenvPython -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" *> $null
        $venvIsUsable = $LASTEXITCODE -eq 0
    }

    if (-not $venvIsUsable) {
        & $UvExe venv --clear --python 3.12 $VenvDir
        if ($LASTEXITCODE -ne 0) {
            throw "uv could not create the Python virtual environment."
        }
    }

    Write-Step "Installing Python dependencies..."
    & $UvExe pip install --python $VenvPython --requirements $RequirementsFile
    if ($LASTEXITCODE -ne 0) {
        throw "Python dependency installation failed."
    }
}

function Find-Ollama {
    $command = Get-Command ollama.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidates = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"),
        (Join-Path $env:LOCALAPPDATA "Ollama\ollama.exe"),
        (Join-Path $env:ProgramFiles "Ollama\ollama.exe")
    )

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            return $candidate
        }
    }

    return $null
}

function Install-Ollama {
    $ollamaExe = Find-Ollama
    if ($ollamaExe) {
        return $ollamaExe
    }

    Write-Step "Ollama is not installed. Installing it from ollama.com..."
    Invoke-RestMethod https://ollama.com/install.ps1 | Invoke-Expression

    $ollamaExe = Find-Ollama
    if (-not $ollamaExe) {
        throw "Ollama installation finished, but ollama.exe is unavailable."
    }

    return $ollamaExe
}

function Start-OllamaIfNeeded {
    param([Parameter(Mandatory = $true)][string]$OllamaExe)

    if (Test-Url -Url "$OllamaUrl/api/version") {
        return
    }

    Write-Step "Starting Ollama..."
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

    $ollamaApp = Join-Path (Split-Path $OllamaExe -Parent) "ollama app.exe"
    if (Test-Path -LiteralPath $ollamaApp -PathType Leaf) {
        Start-Process -FilePath $ollamaApp -WindowStyle Hidden | Out-Null
    }

    if (-not (Wait-ForUrl -Url "$OllamaUrl/api/version" -Attempts 15)) {
        $ollamaStdout = Join-Path $LogDir "ollama-windows.stdout.log"
        $ollamaStderr = Join-Path $LogDir "ollama-windows.stderr.log"
        Start-Process -FilePath $OllamaExe -ArgumentList "serve" -WindowStyle Hidden -RedirectStandardOutput $ollamaStdout -RedirectStandardError $ollamaStderr | Out-Null
    }

    if (-not (Wait-ForUrl -Url "$OllamaUrl/api/version" -Attempts 90)) {
        throw "Ollama did not become ready. Check the log files in $LogDir."
    }
}

function Install-OllamaModel {
    param(
        [Parameter(Mandatory = $true)][string]$OllamaExe,
        [Parameter(Mandatory = $true)][string]$ModelName
    )

    & $OllamaExe show $ModelName *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[CBT Assistant] Model already installed: $ModelName"
        return
    }

    Write-Step "Downloading Ollama model: $ModelName"
    & $OllamaExe pull $ModelName
    if ($LASTEXITCODE -ne 0) {
        throw "Ollama could not download model $ModelName."
    }
}

function Stop-AppPortListener {
    $listeners = @(Get-NetTCPConnection -LocalPort $AppPort -State Listen -ErrorAction SilentlyContinue)
    if ($listeners.Count -eq 0) {
        return
    }

    Write-Step "Port $AppPort is busy. Stopping its current listener..."
    $processIds = @($listeners | Select-Object -ExpandProperty OwningProcess -Unique)

    foreach ($processId in $processIds) {
        if ($processId -le 0 -or $processId -eq $PID) {
            throw "Refusing to stop unexpected process ID $processId on port $AppPort."
        }

        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host ("{0,7} {1}" -f $processId, $process.ProcessName)
            Stop-Process -Id $processId -Force -ErrorAction Stop
        }
    }

    for ($attempt = 1; $attempt -le 10; $attempt++) {
        if (@(Get-NetTCPConnection -LocalPort $AppPort -State Listen -ErrorAction SilentlyContinue).Count -eq 0) {
            return
        }
        Start-Sleep -Seconds 1
    }

    throw "Port $AppPort is still busy."
}

function Start-CbtAssistant {
    $env:OLLAMA_BASE_URL = $OllamaUrl
    $env:OLLAMA_MODEL = $ChatModel

    Write-Step "Starting CBT Assistant..."
    $serverProcess = Start-Process -FilePath $VenvPython -ArgumentList @("`"$ServerFile`"") -WorkingDirectory $ProjectDir -NoNewWindow -PassThru

    if (-not (Wait-ForUrl -Url $HealthUrl -Attempts 300)) {
        if (-not $serverProcess.HasExited) {
            Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
        }
        throw "The server did not pass its health check within 300 seconds."
    }

    Write-Step "CBT Assistant is ready at $AppUrl"
    Start-Process $AppUrl | Out-Null
    Wait-Process -Id $serverProcess.Id
    $serverProcess.Refresh()

    if ($serverProcess.ExitCode -ne 0) {
        throw "CBT Assistant exited with code $($serverProcess.ExitCode)."
    }
}

try {
    if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
        throw "This launcher supports Windows only."
    }

    $windowsVersion = [System.Environment]::OSVersion.Version
    if ($windowsVersion.Major -lt 10 -or ($windowsVersion.Major -eq 10 -and $windowsVersion.Build -lt 19045)) {
        throw "Ollama requires Windows 10 22H2 (build 19045) or newer."
    }

    if (-not (Test-Path -LiteralPath $ServerFile -PathType Leaf)) {
        throw "Missing backend\server.py in $ProjectDir."
    }
    if (-not (Test-Path -LiteralPath $RequirementsFile -PathType Leaf)) {
        throw "Missing requirements.txt in $ProjectDir."
    }

    Set-Location $ProjectDir

    $uvExe = Install-Uv
    Initialize-PythonEnvironment -UvExe $uvExe

    $ollamaExe = Install-Ollama
    Start-OllamaIfNeeded -OllamaExe $ollamaExe
    Install-OllamaModel -OllamaExe $ollamaExe -ModelName $ChatModel
    Install-OllamaModel -OllamaExe $ollamaExe -ModelName $EmbedModel

    Stop-AppPortListener
    Start-CbtAssistant
}
catch {
    Write-Host ""
    Write-Host "[CBT Assistant] ERROR: $($_.Exception.Message)" -ForegroundColor Red

    try {
        Add-Type -AssemblyName PresentationFramework -ErrorAction Stop
        [System.Windows.MessageBox]::Show(
            $_.Exception.Message,
            "CBT Assistant",
            [System.Windows.MessageBoxButton]::OK,
            [System.Windows.MessageBoxImage]::Error
        ) | Out-Null
    }
    catch {
        # The console message above remains available if the desktop dialog cannot be shown.
    }

    exit 1
}
