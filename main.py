from app.init_app import app
from app.router import routers

app.include_router(routers)
