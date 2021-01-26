@ECHO off
ECHO In order to create a virtual environment you MUST have python3.8.6 present and called as python
ECHO If you have python3.8.6 called as python3, change the script to accomodate it 
ECHO PRESS CTRL + C IF YOU DO NOT HAVE PYTHON 3.8.6 AS DEFAULT AND RUN LATER
PAUSE
ECHO Installing virtualenv
python -m pip install virtualenv
ECHO virtualenv installed, continue
PAUSE
ECHO creating venv directory
mkdir venv
ECHO venv directory created 
PAUSE
set mypath=%cd%
ECHO setting up virtual environment
CALL virtualenv %mypath%\venv
ECHO virtual environment is being activated
CALL %mypath%\venv\Scripts\activate.bat
ECHO virtual environment is now set and activated, downloading packages
PAUSE
python -m pip install -r %mypath%\rentAccess\requirements.txt
ECHO setting up .env file
>  "%mypath%\rentAccess\rentAccess\.env" Echo;DEBUG=TRUE
 >> "%mypath%\rentAccess\rentAccess\.env" Echo;SECRET_KEY=#!h))0gh(jjswxelzryv9)mg)a=#-fe=8qd26+5yczb-_!@l8u
 >> "%mypath%\rentAccess\rentAccess\.env" Echo;EMAIL_HOST_USER=yuiborodin@miem.hse.ru
ECHO requirements are now satisfied, making migrations
python rentAccess\manage.py migrate
python rentAccess\manage.py makemigrations userAccount
python rentAccess\manage.py makemigrations common
python rentAccess\manage.py makemigrations properties
python rentAccess\manage.py migrate
ECHO migrations are made, creating test user
python rentAccess\manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')"
ECHO User Created
ECHO username: admin
ECHO password: adminpass
ECHO About to run the sever at localhost:8000
PAUSE
python rentAccess\manage.py runserver
