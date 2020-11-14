from .main import Main

def run(_dir:str, globalSettings:dict) -> dict:
    e = Main(_dir, globalSettings)
    return e.run()
