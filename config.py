import os

class Config:
    """Параметры для запуска сервера.
    
    Ищет параметры в переменных среды и, если не находит,
    берёт их прямо из кода.
    """
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'хз-что-это'
    DB_HOST = os.environ.get('DB_HOST') or '127.127.126.32'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    DB_NAME = os.environ.get('DB_NAME') or 'balda'