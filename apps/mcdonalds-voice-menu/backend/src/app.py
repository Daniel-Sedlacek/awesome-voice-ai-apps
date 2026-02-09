from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.static_files import StaticFilesConfig

from src.routes.audio import AudioController
from src.routes.menu import MenuController


# CORS configuration for frontend
cors_config = CORSConfig(
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app = Litestar(
    route_handlers=[AudioController, MenuController],
    cors_config=cors_config,
    static_files_config=[
        StaticFilesConfig(
            directories=["static"],
            path="/static",
        )
    ],
    debug=True,
)