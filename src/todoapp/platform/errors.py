class DomainError(Exception):
    """Base class for business-rule violations raised from a service layer."""


class NotFoundError(DomainError):
    pass


class ValidationError(DomainError):
    pass
