# Third-party
from fastapi import FastAPI, Request
from fastapi.security import HTTPBasic
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

# Project
from logger import server_logger
import config as cf
from database import db
from .models import UserView, SettingsView

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=cf.server['secret_key'])
security = HTTPBasic()

admin = Admin(app=app, engine=db.engine)
[admin.add_view(view) for view in [UserView, SettingsView]]


@app.get('/')
async def home(request: Request):
    """
    Redirects users to the admin page.
    """
    return RedirectResponse('/admin')


@app.get('/admin')
async def admin_page(request: Request):
    """
    Renders the admin page.
    """
    return await admin.index(request)


@app.on_event("startup")
async def start_server():
    """
    Logs a message when the server starts.
    """
    server_logger.info(f'Server started at http://{cf.server["host"]}:{cf.server["port"]}')


async def start_panel():
    """
    Configures and starts the server.
    """
    from uvicorn import Config, Server
    config = Config(
        app=app,
        host='0.0.0.0',  # Do not change host, because it's running locally in docker container, not host machine
        port=int(cf.server['port'])
    )
    server = Server(config=config)
    await server.serve()
