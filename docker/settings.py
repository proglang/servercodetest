
# pylint: disable=import-error
# pylint: disable=no-name-in-module
from app.servercodetest.settings import TIMEOUT,DJANGO_BASE_URL_PATH, DATABASES
from app.servercodetest.util import env, etoi
# pylint: enable=import-error
# pylint: enable=no-name-in-module

def get_cpu_count():
    try:
        from multiprocessing import cpu_count
        return cpu_count()
    except:
        return 1

GU_SUPERUSER = env("GU_SUPERUSER", "root", delete=True)
GU_SUPERUSER_EMAIL = env("GU_SUPERUSER_EMAIL", "admin@localhost", delete=True)
GU_SUPERUSER_PASSWORD = env("GU_SUPERUSER_PASSWORD", delete=True)

GU_PROCESSES = etoi("GU_PROCESSES",2,1,get_cpu_count() * 2)
GU_THREADS = etoi("GU_THREADS",2,1,get_cpu_count() * 2)
GU_USER_ID = etoi("GU_USER_ID",0,0)
