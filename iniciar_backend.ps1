Set-Location "D:\DemocracIA\backend"
.\venv\Scripts\activate.ps1
uvicorn app:app --reload --port 8000 --host 0.0.0.0
