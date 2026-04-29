# handlers/__init__.py
from .start import router as start_router
from .search_film import (router as search_film_router)
from .manage_numbers import router as manage_numbers_router
from .help import router as help_router

__all__ = [
    'start_router',
    'search_film_router',
    'manage_numbers_router',
    'help_router',
]