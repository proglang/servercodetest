from .main import Main

def run(_dir, globalSettings) -> dict:
    e = Main(_dir, globalSettings)
    return e.run()
