from fastapi import FastAPI, status, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
import uvicorn


from src.routes import contacts
from src.routes import auth


app = FastAPI()
app.include_router(auth.router, prefix="/api")
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(contacts.router, prefix="/api")


templates = Jinja2Templates(directory="src/templates")


@app.get('/')
def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.exception_handler(ValidationError)
def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Invalid input data"}
    )


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.exception_handler(Exception)
def unexpected_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred"},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
