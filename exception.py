class InvalidPINError(Exception):
    pass


class CardBlockedError(Exception):
    pass


class InsufficientBalanceError(Exception):
    pass


class InsufficientATMFundsError(Exception):
    pass


class InvalidAmountError(Exception):
    pass


class AccountInactiveError(Exception):
    pass


class DailyLimitExceededError(Exception):
    pass


class InvalidAccountError(Exception):
    pass