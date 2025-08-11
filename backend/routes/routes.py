from fastapi import APIRouter

from backend.api.exceptions import error_responses

api_router = APIRouter(responses=error_responses)
