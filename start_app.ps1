$PROJECT = "C:\Users\86156\Downloads\roofing_sales_intelligence_case_study\roofing_sales_intelligence_case_study"

Set-Location $PROJECT

$VENV_PY = (Resolve-Path ".\.venv\Scripts\python.exe").Path

Write-Host "Project ready:" (Get-Location)
Write-Host "Virtual-environment Python:" $VENV_PY

& $VENV_PY -m streamlit run .\app.py `
    --server.address 127.0.0.1 `
    --server.port 8501 `
    --browser.gatherUsageStats false
