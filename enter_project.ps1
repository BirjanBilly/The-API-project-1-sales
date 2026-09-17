$PROJECT = "C:\Users\86156\Downloads\roofing_sales_intelligence_case_study\roofing_sales_intelligence_case_study"

Set-Location $PROJECT

$global:VENV_PY = (Resolve-Path ".\.venv\Scripts\python.exe").Path

Write-Host "Project:" (Get-Location)
Write-Host "VENV_PY:" $global:VENV_PY
