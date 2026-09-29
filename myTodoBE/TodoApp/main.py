from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from .dependencies import AUTH_COOKIE_NAME, CORS_ORIGINS
    from .routers.auth import router as auth_router
    from .routers.notes import router as notes_router
    from .routers.todo import router as todo_router
except ImportError:
    from dependencies import AUTH_COOKIE_NAME, CORS_ORIGINS
    from routers.auth import router as auth_router
    from routers.notes import router as notes_router
    from routers.todo import router as todo_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def protect_cookie_authenticated_mutations(request: Request, call_next):
    if (
        request.method in {"POST", "PUT", "PATCH", "DELETE"}
        and AUTH_COOKIE_NAME in request.cookies
        and request.headers.get("origin") not in CORS_ORIGINS
    ):
        return JSONResponse(status_code=403, content={"detail": "Invalid request origin."})

    return await call_next(request)

app.include_router(auth_router)
app.include_router(todo_router)
app.include_router(notes_router)