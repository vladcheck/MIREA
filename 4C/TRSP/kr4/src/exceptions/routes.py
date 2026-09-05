from typing import Dict

from fastapi import APIRouter, Request, exception_handlers
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ErrorResponse import ErrorResponse
from Exceptions import CustomExceptionA, CustomExceptionB
