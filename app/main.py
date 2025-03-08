from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes import customer, nlp, orders, products


app = FastAPI(title=settings.APP_NAME)

app.include_router(orders.router)
app.include_router(nlp.router)
app.include_router(products.router)
app.include_router(customer.router)


# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Custom error handler to return only the first validation error message.
    """
    first_error = exc.errors()[0]  # Get the first error
    message = first_error["msg"].replace("Value error, ", "")  # Clean message

    return JSONResponse(status_code=422, content={"detail": message})


@app.exception_handler(Exception)
async def internal_server_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handles unexpected 500 errors and returns a clean message"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong. Please try again later."},
    )

@app.get("/")
def health_check():
    """Returns a simple health check message"""
    return {"status": "ok"}
