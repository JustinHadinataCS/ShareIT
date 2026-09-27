from pathlib import PurePath

from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.types import Scope


class SPAStaticFiles(StaticFiles):
    """Serves the built React app, with index.html for routes that only exist in React.

    A share link like /share/{id} has no file behind it, so it gets index.html instead
    of a 404. StaticFiles already refuses paths that resolve outside the static
    directory, and unknown /api/ paths keep their 404 so API clients never get HTML.
    """

    async def get_response(self, path: str, scope: Scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            if exc.status_code != 404 or PurePath(path).parts[:1] == ("api",):
                raise
            return await super().get_response("index.html", scope)
