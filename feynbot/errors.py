# IMPLEMENT errors `events.py` and `commands.py`


class InvalidKwarg(Exception):
    """Raised when an invalid keyword argument is passed to a function."""

    def __init__(self, kwargs) -> None:
        message = (
            "Invalid keyword argument(s) passed.  Consider checking any "
            + f"child object instantiation especially.\nInvalid Keys:\n{kwargs}"
        )
        super().__init__(message)
