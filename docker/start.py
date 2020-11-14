import os
import time
import re
import subprocess
import logging

import MySQLdb  # pylint: disable=import-error

import settings



log = logging.getLogger("sct_start")
logging.basicConfig()
log.setLevel(logging.INFO)

def CheckConnection():
    log.info("Checking connection")
    dbs = settings.DATABASES
    for (name, db_data) in dbs.items():
        connected = False
        for i in range(30):
            try:
                res = MySQLdb.connect(
                    host=db_data["HOST"],
                    port=db_data["PORT"],
                    user=db_data["USER"],
                    passwd=db_data["PASSWORD"],
                    db=db_data["NAME"],
                )
                res.close()
                connected = True
                break
            except MySQLdb._exceptions.OperationalError:
                log.info(f"Couldn't connect to database {name} ({i+1}). Retrying....")
                time.sleep(1)
                continue
        if not connected:
            log.error(f"Could not connect to database {name}")
            return False
    return True


def Process(data):
    process = subprocess.Popen(
        data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    (output, err) = process.communicate()
    return (process.returncode, output, err)


def CreateStatic():
    Process(["python", "manage.py", "collectstatic", "--noinput"])
    return True


def CreateSuperUser():
    log.info("Creating Superuser...")
    if settings.GU_SUPERUSER_PASSWORD == None:
        log.warning("You need to define a password (GU_SUPERUSER_PASSWORD)")
        return
    os.environ["DJANGO_SUPERUSER_PASSWORD"] = settings.GU_SUPERUSER_PASSWORD
    Process(
        [
            "python",
            "manage.py",
            "createsuperuser",
            "--noinput",
            "--username",
            settings.GU_SUPERUSER,
            "--email",
            settings.GU_SUPERUSER_EMAIL,
        ]
    )
    del os.environ["DJANGO_SUPERUSER_PASSWORD"]
    return True

def MakeMigrations():
    for x in [None, "app"]:
        _d = ["python", "manage.py", "makemigrations"]
        if x != None:
            _d.append(x)
        (code, data, err) = Process(_d)
        if code != 0:
            raise ValueError(f"Creation of Migrations failed  ({code})...{data} {err}")
        ret = re.findall(r".*/migrations/([0-9]+)_[a-z]+\.py.*", data)
        if len(ret) != 1:
            continue
        _d[2] = "sqlmigrate"
        _d.append(ret[0])
        (code, data, err) = Process(_d)
        if code != 0:
            raise ValueError(f"Migration failed ({code})...{data}, {err}")
    (code, data, err) = Process(["python", "manage.py", "migrate"])
    if code != 0:
        raise IOError("couldn't migrate database")
    return True

def run_nginx():
    with open("/usr/src/nginx.conf", "r") as file:
        data = file.read()
    text = ""
    url = settings.DJANGO_BASE_URL_PATH
    if url != "":
        text = f"rewrite  ^{url}/(.*) /$1 break;"
    data = data.replace("<SET_PATH>", text)
    with open("/etc/nginx/nginx.conf", "w") as file:
        file.write(data)
    os.system("nginx")


def run_gunicorn():
    _w = "-w %d" % settings.GU_PROCESSES
    __threads = "--threads %d" % settings.GU_THREADS
    _u = "-u %d" % settings.GU_USER_ID
    __timeout = "--timeout %d" % settings.TIMEOUT
    __bind = "--bind 0.0.0.0"
    __preload = "--preload"  # required for shared locks between process purposes
    app = "servercodetest.wsgi:application"

    os.system(f"gunicorn {_w} {_u} {__threads} {__timeout} {__bind} {__preload} {app}")


def main():
    os.chdir("/usr/src/app")
    if not CheckConnection():
        return
    if not MakeMigrations():
        return
    if not CreateStatic():
        return
    if not CreateSuperUser():
        return
    run_nginx()
    run_gunicorn()


if __name__ == "__main__":
    log.info("Startup...")
    try:
        main()
    except Exception as e:
        log.error("An Exception occured %s: %s", type(e).__name__, str(e))
    log.info("Program finished")

