import fastapi
from starlette import status


class BadRequestException(fastapi.HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


class UnauthorizedException(fastapi.HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
        )


class ForbiddenException(fastapi.HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )


class NotFoundException(fastapi.HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )
