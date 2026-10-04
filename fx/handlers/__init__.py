"""
fx.handlers — exposes all handler lists for bot.py registration.
"""
from .auth    import handlers as auth_handlers
from .menu    import handlers as menu_handlers
from .profile import handlers as profile_handlers
from .signals import handlers as signal_handlers

__all__ = [
    "auth_handlers",
    "menu_handlers",
    "profile_handlers",
    "signal_handlers",
]
