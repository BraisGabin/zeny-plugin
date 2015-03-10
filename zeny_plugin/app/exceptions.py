from rest_framework import status
from rest_framework.exceptions import ValidationError


class ConflictError(ValidationError):
    status_code = status.HTTP_409_CONFLICT
