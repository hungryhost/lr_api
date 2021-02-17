# Backend для lockandrent.ru 

В данном репозитории хранится backend часть проекта lockandrent.ru

Использованные технологии:

- Django + DRF
- Redis (для кэша и как брокер сообщений для celery)
- PostgreSQL (на проде) 
- AMAZON S3 (или DigitalOcean Spaces) для хранения статики и медиа файлов
- Celery
- Cities Light
- Различные дополнительные модули для DRF или Django (фильтры, специальные поля и тп.)