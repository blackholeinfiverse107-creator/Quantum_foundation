param(
  [ValidateSet("All","Raj","Nilesh","Quick")]
  [string]$Suite,
  [string]$ReportPath,
  [switch]$Minimal
  ,
  [switch]$BadgeOnly
  ,
  [switch]$Pipeline
  ,
  [switch]$Demo
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $PSCommandPath
$root = Split-Path -Parent $scriptDir
Set-Location $root
$rajPath = Join-Path $root "Raj"
$nileshPath = Join-Path $root "Nilesh"
if (-not (Test-Path $rajPath)) {
  $altRaj = @("raj","Enforcement Engine")
  foreach ($cand in $altRaj) {
    $p = Join-Path $root $cand
    if (Test-Path $p) { $rajPath = $p; break }
  }
}
if (-not (Test-Path $nileshPath)) {
  $altNil = @("nilesh","Backend Stability Spine")
  foreach ($cand in $altNil) {
    $p = Join-Path $root $cand
    if (Test-Path $p) { $nileshPath = $p; break }
  }
}

if (-not $Suite) { $Suite = "All" }
if (-not $ReportPath) { $ReportPath = "ci/proof_status.json" }
if ($Minimal -and $ReportPath -eq "ci/proof_status.json") {
  if ($Suite -eq "Quick") { $ReportPath = "ci/proof_status_quick_min.json" } else { $ReportPath = "ci/proof_status_min.json" }
}

# Demo mode: start API + Streamlit, then run pipeline proofs
if ($Demo) {
  Write-Output "Starting FastAPI (uvicorn) on http://127.0.0.1:8000 ..."
  $apiDir = Join-Path $root "Enforcement Engine"
  Start-Process -FilePath "powershell" -ArgumentList "uvicorn enforcement_gateway:app --reload --port 8000" -WorkingDirectory $apiDir
  Write-Output "Starting Streamlit UI on http://localhost:8501 ..."
  Start-Process -FilePath "powershell" -ArgumentList "streamlit run streamlit_app.py" -WorkingDirectory $root
  Start-Sleep -Seconds 3
  Write-Output "Running pipeline proofs ..."
  $Pipeline = $true
}

# Pipeline mode: run all suites with minimal + badge-only
 
function Invoke-PyTest {
  param(
    [string]$WorkDir,
    [string[]]$Args
  )
  Push-Location $WorkDir
  try {
    $outLines = & pytest @Args 2>&1
    $code = $LASTEXITCODE
    $out = ($outLines -join "`n")
    $err = ""
    $passed = [int]([regex]::Match($out, "(?<num>\d+)\s+passed").Groups["num"].Value)
    $failedMatch = [regex]::Match($out, "(?<num>\d+)\s+failed")
    $failed = if ($failedMatch.Success) { [int]$failedMatch.Groups["num"].Value } else { 0 }
    $warningsMatch = [regex]::Match($out, "(?<num>\d+)\s+warnings?")
    $warnings = if ($warningsMatch.Success) { [int]$warningsMatch.Groups["num"].Value } else { 0 }
    return @{
      success = ($code -eq 0)
      exitCode = $code
      passed = $passed
      failed = $failed
      warnings = $warnings
      stdout = $out
      stderr = $err
    }
  } finally {
    Pop-Location
  }
}

# helper: summarize result when -Minimal is set
function ToSummary {
  param([hashtable]$Result)
  if ($null -eq $Result) { return $null }
  if ($Minimal) {
    return @{
      success = $Result.success
      exitCode = $Result.exitCode
      passed = $Result.passed
      failed = $Result.failed
      warnings = $Result.warnings
    }
  }
  return $Result
}

if ($Pipeline) {
  $suites = @("All","Raj","Nilesh","Quick")
  $allOk = $true
  $pipelineReport = @{
    generated_at = (Get-Date).ToString("o")
    status = "READY"
    suites = @{}
  }
  foreach ($s in $suites) {
    $minPath = "ci/proof_status_$($s.ToLower())_min.json"
    $stdPath = "ci/proof_status_$($s.ToLower()).json"
    $rajResult = $null
    $nileshResult = $null
    $env:PYTHONPATH = $rajPath
    if ($s -eq "Raj" -or $s -eq "All" -or $s -eq "Quick") {
      if ($s -eq "Quick") {
        $rajResult = Invoke-PyTest -WorkDir $rajPath -Args @("tests/test_enforcement_engine.py","tests/test_failure_resilience.py","tests/test_trust_alignment.py","-q")
      } else {
        $rajResult = Invoke-PyTest -WorkDir $rajPath -Args @("-q")
      }
      if (-not $rajResult.success) { $allOk = $false }
    }
    $env:API_KEY = "localtest"
    $env:PYTHONPATH = $nileshPath
    if ($s -eq "Nilesh" -or $s -eq "All" -or $s -eq "Quick") {
      if ($s -eq "Quick") {
        $nileshResult = Invoke-PyTest -WorkDir $nileshPath -Args @("tests/test_full_stack.py::test_assistant_endpoint_schema_and_arl_gate", "-q")
      } else {
        $nileshResult = Invoke-PyTest -WorkDir $nileshPath -Args @("tests/test_full_stack.py", "-q")
      }
      if (-not $nileshResult.success) { $allOk = $false }
    }
    $ready = if (
      ($s -eq "Raj" -and $rajResult.success) -or
      ($s -eq "Nilesh" -and $nileshResult.success) -or
      (($s -eq "All" -or $s -eq "Quick") -and ($rajResult -ne $null) -and ($nileshResult -ne $null) -and $rajResult.success -and $nileshResult.success)
    ) { "READY" } else { "NOT_READY" }
    $oldMinimal = $Minimal
    $Minimal = $true
    $minReport = @{ status = $ready; raj = (ToSummary $rajResult); nilesh = (ToSummary $nileshResult); generated_at = (Get-Date).ToString("o") }
    $Minimal = $oldMinimal
    $minReport | ConvertTo-Json -Depth 5 | Set-Content -Path $minPath
    $fullReport = @{ status = $ready; raj = $rajResult; nilesh = $nileshResult; generated_at = (Get-Date).ToString("o") }
    $fullReport | ConvertTo-Json -Depth 5 | Set-Content -Path $stdPath
    if ($ready -eq "READY") {
      $badge = @"
![ARL Proofs](https://img.shields.io/badge/ARL%20Proofs-READY-brightgreen)

Raj: $([int]($rajResult.passed)) passed, $([int]($rajResult.failed)) failed, $([int]($rajResult.warnings)) warnings
Nilesh: $([int]($nileshResult.passed)) passed, $([int]($nileshResult.failed)) failed, $([int]($nileshResult.warnings)) warnings
"@
      Set-Content -Path "ci/READY_BADGE.md" -Value $badge
    } else {
      Set-Content -Path "ci/READY_BADGE.md" -Value "# Status: NOT READY"
    }
    $pipelineReport.suites[$s] = @{
      status = $ready
      raj = $minReport.raj
      nilesh = $minReport.nilesh
    }
    if ($ready -ne "READY") { $pipelineReport.status = "NOT_READY" }
  }
  $pipelineReport | ConvertTo-Json -Depth 6 | Set-Content -Path "ci/pipeline_summary.json"
  if ($allOk) { Write-Output "PIPELINE: READY"; exit 0 } else { Write-Output "PIPELINE: NOT READY"; exit 1 }
}
# Run Raj tests
$rajResult = $null
if ($Suite -eq "All" -or $Suite -eq "Raj" -or $Suite -eq "Quick") {
  $env:PYTHONPATH = $rajPath
  if ($Suite -eq "Quick") {
    # run a fast subset of Raj tests
    $rajResult = Invoke-PyTest -WorkDir $rajPath -Args @("tests/test_enforcement_engine.py","tests/test_failure_resilience.py","tests/test_trust_alignment.py","-q")
  } else {
    $rajResult = Invoke-PyTest -WorkDir $rajPath -Args @("-q")
  }
  if (-not $rajResult.success) {
    Write-Output "Raj tests failed"
    if (-not $BadgeOnly) {
      $report = @{ status = "NOT_READY"; raj = (ToSummary $rajResult); nilesh = $null; generated_at = (Get-Date).ToString("o") }
      $report | ConvertTo-Json -Depth 5 | Set-Content -Path $ReportPath
    }
    Set-Content -Path "ci/READY_BADGE.md" -Value "# Status: NOT READY"
    exit 1
  }
}

# Run Nilesh tests
$nileshResult = $null
if ($Suite -eq "All" -or $Suite -eq "Nilesh" -or $Suite -eq "Quick") {
  $env:API_KEY = "localtest"
  $env:PYTHONPATH = $nileshPath
  if ($Suite -eq "Quick") {
    $nileshResult = Invoke-PyTest -WorkDir $nileshPath -Args @("tests/test_full_stack.py::test_assistant_endpoint_schema_and_arl_gate", "-q")
  } else {
    $nileshResult = Invoke-PyTest -WorkDir $nileshPath -Args @("tests/test_full_stack.py", "-q")
  }
  if (-not $nileshResult.success) {
    Write-Output "Nilesh tests failed"
    if (-not $BadgeOnly) {
      $report = @{ status = "NOT_READY"; raj = (ToSummary $rajResult); nilesh = (ToSummary $nileshResult); generated_at = (Get-Date).ToString("o") }
      $report | ConvertTo-Json -Depth 5 | Set-Content -Path $ReportPath
    }
    Set-Content -Path "ci/READY_BADGE.md" -Value "# Status: NOT READY"
    exit 1
  }
}

$finalStatus = if (
  ($Suite -eq "Raj" -and $rajResult.success) -or
  ($Suite -eq "Nilesh" -and $nileshResult.success) -or
  (($Suite -eq "All" -or $Suite -eq "Quick") -and $rajResult.success -and $nileshResult.success)
) { "READY" } else { "NOT_READY" }
if (-not $BadgeOnly) {
  $report = @{ status = $finalStatus; raj = (ToSummary $rajResult); nilesh = (ToSummary $nileshResult); generated_at = (Get-Date).ToString("o") }
  $report | ConvertTo-Json -Depth 5 | Set-Content -Path $ReportPath
}

if ($finalStatus -eq "READY") {
  $badge = @"
![ARL Proofs](https://img.shields.io/badge/ARL%20Proofs-READY-brightgreen)

Raj: $($rajResult.passed) passed, $($rajResult.failed) failed, $($rajResult.warnings) warnings
Nilesh: $($nileshResult.passed) passed, $($nileshResult.failed) failed, $($nileshResult.warnings) warnings
"@
  Set-Content -Path "ci/READY_BADGE.md" -Value $badge
  Write-Output "READY: proofs passed"
} else {
  Set-Content -Path "ci/READY_BADGE.md" -Value "# Status: NOT READY"
  Write-Output "NOT READY: proofs failed"
}
