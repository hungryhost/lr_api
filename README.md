# Серверное приложение для веб-приложения Сервиса аренды помещений 

# Основная информация
## Стек проекта
- Python
- Django
- Django Rest Framework
- Redis
- S3 хранилище файлов
- Docker

## Архитектура базы данных
Архитектура базы данных в программном варианте рассредоточена в файлах models.py каждого модуля приложения.
Описание функций каждой из моделей приведено в комментарии к классу модели.

# Развёртывание на сервере
Развёртывание на сервере состоит из двух этапов.
## Этап первый - заполнение переменных среды
```
DEBUG=<on/off - режим работы>
SQL_DEBUG=<True/False - режим отладки запросов к БД>
ALLOWED_HOSTS=<внутренняя настройка Django, см. документацию Django Framework>
SECRET_KEY=<внутренняя настройка Django, см. документацию Django Framework>
CORS_ORIGIN_ALLOW_ALL=<внутренняя настройка Django, см. документацию Django Framework>
CORS_ALLOWED_ORIGINS=<внутренняя настройка Django, см. документацию Django Framework>

LOG_ROOT=<путь к папке для хранения log-файлов>
DB_NAME=<название базы данных>
DB_HOST=<адрес базы данных>
DB_PORT=<порт базы данных>
DB_USER=<пользователь базы данных>
DB_PASSWORD=<пароль базы данных>
DEV_DATABASE_URL=<адрес локальной БД для разработки, пример: sqlite:////C:/web-294/web-294/rentAccess/db.sqlite3> 

EMAIL_HOST=<адрес mail-сервера>
EMAIL_HOST_USER=<адрес отправки сообщений по умолчанию>
EMAIL_HOST_PASSWORD=<пароль для пользователя почты>
EMAIL_PORT=<порт mail-сервера>

CACHE_URL_1=<адрес БД для кэша (REDIS)>

CELERY_BROKER_URL=<адрес брокера сообщений CELERY>
CELERY_RESULT_BACKEND=<адрес брокера сообщений CELERY>

USE_POSTGRES=<True/False, выбор БД для использования>
USE_S3=<True/False, выбор хранилища для использования>
USE_REDIS_CACHE=<True/False, выбор REDIS для кэша>
LOCK_ENCRYPTION_KEYS=<base64 ключ для шифрования кодов замка>
KEY_HASH=<хэш ключ для шифрования кодов замка>
CARD_HASH=<хэщ ключ для шифрования карт замка>
```
