set mypath=%cd%

ECHO virtual environment is being activated
CALL %mypath%\venv\Scripts\activate.bat
ECHO virtual environment is now set and activated
ECHO About to run the sever at localhost:8000
PAUSE
python rentAccess\manage.py runserver