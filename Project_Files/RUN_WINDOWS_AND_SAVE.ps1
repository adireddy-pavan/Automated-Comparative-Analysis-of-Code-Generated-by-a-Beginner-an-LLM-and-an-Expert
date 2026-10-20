# Tharun MSc Project - Windows 10/11 PowerShell 5.1+ verification runner.
# Results stay INSIDE this Project_Files folder. Original outputs are never overwritten.
# This script cannot authenticate authorship or perform an independent human evaluation.
param([switch]$ReuseExistingVenv)
$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$RunsRoot = Join-Path $Root 'verification\windows_runs'
New-Item -ItemType Directory -Force -Path $RunsRoot | Out-Null
$RunId = (Get-Date -Format 'yyyyMMdd_HHmmss') + '_' + ([guid]::NewGuid().ToString('N').Substring(0,6))
$RunDir = Join-Path $RunsRoot $RunId
$Workspace = Join-Path $RunDir 'workspace'
$Logs = Join-Path $RunDir 'logs'
New-Item -ItemType Directory -Force -Path $Workspace, $Logs | Out-Null
$ResultZip = Join-Path $RunsRoot ("RESULTS_" + $RunId + '.zip')
$Status = 'FAIL'
$Failure = ''
$CurrentStep = 'starting'
$StepRecords = New-Object 'System.Collections.Generic.List[object]'
$StartTime = (Get-Date).ToUniversalTime().ToString('o')
$Env:PYTHONUTF8 = '1'
$Env:PYTHONIOENCODING = 'utf-8'

function Invoke-Checked {
    param([string]$Name, [string]$Executable, [string[]]$Arguments, [string]$WorkingDir)
    $script:CurrentStep = $Name
    $log = Join-Path $Logs ($Name + '.log')
    Write-Host ("Running " + $Name + " ...") -ForegroundColor Cyan
    $start = (Get-Date).ToUniversalTime().ToString('o')
    Push-Location $WorkingDir
    $priorErrorPreference = $ErrorActionPreference
    try {
        # Native tools may emit nonfatal stderr. Decide success by their real exit code.
        $ErrorActionPreference = 'Continue'
        $global:LASTEXITCODE = 0
        & $Executable @Arguments *> $log
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $priorErrorPreference
        Pop-Location
    }
    $StepRecords.Add([pscustomobject]@{step=$Name; utc_started=$start; exit_code=$exitCode; log=("logs\\"+$Name+'.log')} )
    if ($exitCode -ne 0) {
        Write-Host ("FAILED at " + $Name + "; examine " + $log) -ForegroundColor Red
        Get-Content -Path $log -Tail 12 | Out-Host
        throw ("Step " + $Name + " returned exit code " + $exitCode)
    }
    Write-Host ("PASS: " + $Name) -ForegroundColor Green
}

function Locate-Python {
    foreach ($p in @(@{exe='py'; a=@('-3.11')}, @{exe='python';a=@()})) {
        $command = Get-Command $p.exe -ErrorAction SilentlyContinue
        if ($null -eq $command) { continue }
        try {
            $args = @($p.a) + @('-c', 'import sys; assert sys.version_info[:2] == (3, 11); print(sys.version)')
            $out = & $p.exe @args 2>$null
            if ($LASTEXITCODE -eq 0) { return $p }
        } catch { }
    }
    throw 'Python 3.11 was not detected. Install Python 3.11 (64-bit) from python.org, then reopen PowerShell.'
}

try {
    # Copy a separate analysis workspace. Do NOT run in the historical source tree.
    # Omit .git and virtual environments, and omit old nested runs to prevent recursive copying.
    Write-Host ('Project root: ' + $Root)
    Write-Host ('Results folder: ' + $RunDir) -ForegroundColor Yellow
    $CurrentStep = 'copy_workspace'
    foreach ($item in Get-ChildItem -LiteralPath $Root -Force) {
        if ($item.Name -in @('.git','.venv_friend','.venv','.venv_verify','__pycache__')) { continue }
        if ($item.Name -eq 'verification') {
            $verDst = Join-Path $Workspace 'verification'
            New-Item -ItemType Directory -Force -Path $verDst | Out-Null
            foreach ($v in Get-ChildItem -LiteralPath $item.FullName -Force) {
                if ($v.Name -eq 'windows_runs') { continue }
                Copy-Item -LiteralPath $v.FullName -Destination (Join-Path $verDst $v.Name) -Recurse -Force
            }
            continue
        }
        Copy-Item -LiteralPath $item.FullName -Destination (Join-Path $Workspace $item.Name) -Recurse -Force
    }
    $archived = Join-Path $Workspace 'outputs\metrics.csv'
    if (-not (Test-Path -LiteralPath $archived)) { throw 'Archived outputs\metrics.csv not found in extracted project' }
    Copy-Item -LiteralPath $archived -Destination (Join-Path $Workspace 'verification\archived_metrics_before_run.csv') -Force
    (Get-Date).ToUniversalTime().ToString('o') | Set-Content -Encoding UTF8 -Path (Join-Path $Workspace 'verification\windows_run_started_utc.txt')
    (Get-FileHash -Algorithm SHA256 -LiteralPath $archived).Hash | Set-Content -Encoding ASCII -Path (Join-Path $Logs 'archived_metrics_sha256.txt')

    # Save real original history identifiers when available (not a claim about original development).
    if ((Test-Path (Join-Path $Root '.git')) -and (Get-Command git -ErrorAction SilentlyContinue)) {
        Push-Location $Root
        try {
            & git rev-parse HEAD *> (Join-Path $Logs 'source_git_commit.txt')
            & git status --short *> (Join-Path $Logs 'source_git_status.txt')
        } finally { Pop-Location }
    }

    $launcher = Locate-Python
    Write-Host ('Python launcher: ' + $launcher.exe + ' ' + ($launcher.a -join ' '))
    $Venv = Join-Path $Root '.venv_friend'
    $VenvPython = Join-Path $Venv 'Scripts\python.exe'
    if (-not ($ReuseExistingVenv -and (Test-Path $VenvPython))) {
        Invoke-Checked -Name '01_create_venv' -Executable $launcher.exe -Arguments (@($launcher.a) + @('-m','venv',$Venv)) -WorkingDir $Root
    }
    if (-not (Test-Path $VenvPython)) { throw 'Python virtual environment was not created successfully' }
    Invoke-Checked '02_install_requirements' $VenvPython @('-m','pip','install','--disable-pip-version-check','-r','requirements.txt') $Workspace
    Invoke-Checked '03_pip_check' $VenvPython @('-m','pip','check') $Workspace
    Invoke-Checked '04_versions' $VenvPython @('-m','pip','freeze') $Workspace
    Copy-Item (Join-Path $Logs '04_versions.log') (Join-Path $Logs 'installed_packages.txt') -Force
    $Scripts = Join-Path $Venv 'Scripts'
    foreach ($tool in @('radon','pylint','bandit')) {
        if (-not (Test-Path (Join-Path $Scripts ($tool+'.exe')))) { throw ($tool+'.exe not found in the active virtual environment') }
        Invoke-Checked ('05_tool_'+$tool) (Join-Path $Scripts ($tool+'.exe')) @('--version') $Workspace
    }
    Invoke-Checked '06_archive_integrity' $VenvPython @('tools/audit_repro_evidence.py') $Workspace
    Invoke-Checked '07_source_manifest' $VenvPython @('tools/provenance_inventory.py') $Workspace
    Invoke-Checked '07b_archived_stats_independent_check' $VenvPython @('tools/archive_scientific_crosscheck.py') $Workspace
    Copy-Item (Join-Path $Workspace 'verification\archived_scientific_crosscheck.json') (Join-Path $Logs 'original_stats_independent_check.json') -Force
    Invoke-Checked '08_all_framework_tests' $VenvPython @('-m','pytest','tests/','-q') $Workspace
    Invoke-Checked '09_pylint_quality_gate' $VenvPython @('-m','pylint','--fail-under=10.0','src/','run_analysis.py','config.py') $Workspace
    Invoke-Checked '10_bandit_quality_gate' $VenvPython @('-m','bandit','-q','-c','pyproject.toml','-r','src/','run_analysis.py','config.py') $Workspace
    # The core analysis reruns all 210 functional cases and Radon/Pylint/Bandit metrics.
    Invoke-Checked '11_complete_analysis' $VenvPython @('run_analysis.py','--verbose') $Workspace
    Invoke-Checked '12_validate_new_outputs' $VenvPython @('tools/windows_review_summary.py') $Workspace
    Invoke-Checked '12b_fresh_stats_independent_check' $VenvPython @('tools/archive_scientific_crosscheck.py') $Workspace
    Copy-Item (Join-Path $Workspace 'verification\archived_scientific_crosscheck.json') (Join-Path $RunDir 'fresh_stats_independent_check.json') -Force
    Copy-Item (Join-Path $Workspace 'verification\windows_review_summary.json') (Join-Path $RunDir 'windows_review_summary.json') -Force
    # Record status of genuinely external requirements; missing reviewers remain PENDING.
    Invoke-Checked '13_iteration_history_inventory' $VenvPython @('tools/iteration_evidence_audit.py') $Workspace
    Invoke-Checked '14_external_reviewer_forms' $VenvPython @('tools/external_evidence_review.py') $Workspace
    Invoke-Checked '15_external_cases_validate_only' $VenvPython @('tools/run_external_validation.py') $Workspace
    Invoke-Checked '16_evidence_status' $VenvPython @('tools/evidence_completion_status.py') $Workspace
    $Status = 'PASS'
} catch {
    $Failure = $_.Exception.Message
    Write-Host ('VERIFICATION FAILED: ' + $Failure) -ForegroundColor Red
    Write-Host ('The FAILED run and all available evidence are saved at: ' + $RunDir)
} finally {
    $metadata = [ordered]@{
      status=$Status; technical_verification_only=$true; utc_started=$StartTime; utc_finished=(Get-Date).ToUniversalTime().ToString('o')
      project_path=$Root; results_path=$RunDir; failed_step=($(if ($Status -eq 'PASS') { $null } else { $CurrentStep }))
      error=$Failure; steps=@($StepRecords.ToArray())
      disclaimer='PASS proves this copy of the historical benchmark ran on this machine. It does not authenticate original LLM identity, blinded tests, actual human participants, or historical student development.'
    }
    $metadata | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path (Join-Path $RunDir 'WINDOWS_STATUS.json')
    @(
      'THARUN WINDOWS VERIFICATION RESULTS'
      ('Status: ' + $Status)
      ('Run folder: ' + $RunDir)
      ('Completed UTC: ' + (Get-Date).ToUniversalTime().ToString('o'))
      ('Failure if any: ' + $Failure)
      'Read WINDOWS_STATUS.json and logs/ for exact evidence.'
      'If PASS, read windows_review_summary.json, fresh_stats_independent_check.json and workspace/outputs/stats.md.'
      'A static_metric_drift_count greater than zero requires manual dissertation reconciliation.'
      'Outputs are under workspace/outputs, workspace/report, workspace/figures, workspace/evidence.'
      'Original Project_Files outputs and evidence are untouched.'
      'External independent reviewer assessments and original API records remain separate tasks. Read workspace/verification/evidence_completion_status.json.'
    ) | Set-Content -Encoding UTF8 (Join-Path $RunDir 'README_RESULTS.txt')
    try {
        Write-Host 'Packaging entire run folder for return review (may take a few minutes)...'
        Compress-Archive -LiteralPath $RunDir -DestinationPath $ResultZip -CompressionLevel Optimal -Force
        Write-Host ('RESULTS ZIP: ' + $ResultZip) -ForegroundColor Yellow
    } catch {
        Write-Host ('Could not package ZIP automatically: '+$_.Exception.Message) -ForegroundColor Red
        Write-Host ('You can right-click and zip the folder: ' + $RunDir)
    }
    Write-Host ('RESULT STATUS: ' + $Status)
    if ($Status -ne 'PASS') { exit 1 }
    exit 0
}
