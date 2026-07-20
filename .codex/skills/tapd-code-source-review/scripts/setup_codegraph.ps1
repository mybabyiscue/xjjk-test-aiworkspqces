Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$existing = Get-Command codegraph -ErrorAction SilentlyContinue
$codegraphCommand = if ($null -ne $existing) { $existing.Source } else { "" }

if ([string]::IsNullOrWhiteSpace($codegraphCommand)) {
    $installerUrl = "https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1"
    $installerPath = Join-Path $env:TEMP ("codegraph-install-" + [guid]::NewGuid().ToString() + ".ps1")
    try {
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
        & $installerPath
    }
    finally {
        if (Test-Path -LiteralPath $installerPath) {
            Remove-Item -LiteralPath $installerPath -Force
        }
    }

    $bundledCommand = Join-Path $env:LOCALAPPDATA "codegraph\current\bin\codegraph.cmd"
    if (-not (Test-Path -LiteralPath $bundledCommand)) {
        throw "CodeGraph installation completed but the launcher was not found at $bundledCommand"
    }
    $codegraphCommand = $bundledCommand
}

& $codegraphCommand telemetry off
if ($LASTEXITCODE -ne 0) {
    throw "Failed to disable CodeGraph telemetry. Exit code: $LASTEXITCODE"
}

& $codegraphCommand install --target=codex --location=global --yes
if ($LASTEXITCODE -ne 0) {
    throw "Failed to register CodeGraph MCP for Codex. Exit code: $LASTEXITCODE"
}

& $codegraphCommand version
if ($LASTEXITCODE -ne 0) {
    throw "CodeGraph version verification failed. Exit code: $LASTEXITCODE"
}

Write-Host "CodeGraph CLI installation and Codex MCP registration completed."
Write-Host "Restart Codex before running tapd-code-source-review again."

