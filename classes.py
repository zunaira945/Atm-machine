from abc import ABC, abstractmethod
from datetime import datetime, date

from exception import (
    InvalidPINError,
    CardBlockedError,
    InsufficientBalanceError,
    InsufficientATMFundsError,
    InvalidAmountError,
    AccountInactiveError,
    DailyLimitExceededError,
    InvalidAccountError
)


# ==========================================================
# TRANSACTION HIERARCHY
# ==========================================================

class Transaction(ABC):

    def __init__(self, amount, account):
        self.transaction_id = (
            "TXN-" + datetime.now().strftime("%Y%m%d%H%M%S%f")
        )
        self.amount = amount
        self.account = account
        self.date_time = datetime.now()
        self.status = "SUCCESS"

    @abstractmethod
    def get_type(self):
        pass


class DepositTransaction(Transaction):

    def get_type(self):
        return "DEPOSIT"


class WithdrawalTransaction(Transaction):

    def get_type(self):
        return "WITHDRAWAL"


class TransferTransaction(Transaction):

    def __init__(self, amount, account, receiver, transaction_kind):
        super().__init__(amount, account)
        self.receiver = receiver
        self.transaction_kind = transaction_kind

    def get_type(self):
        return "TRANSFER"


# ==========================================================
# ACCOUNT - ABSTRACT CLASS
# ==========================================================

class Account(ABC):

    def __init__(
        self,
        account_number,
        holder,
        pin,
        balance=0
    ):
        self.account_number = account_number
        self.holder = holder

        # Encapsulation
        self.__balance = float(balance)
        self.__pin = pin
        self.__status = "ACTIVE"

        self.transactions = []

        self.daily_withdrawal = 0
        self.daily_transfer = 0
        self.last_activity_date = date.today()

    # ------------------------------------------------------
    # BALANCE
    # ------------------------------------------------------

    def get_balance(self):
        return self.__balance

    def _add_balance(self, amount):
        self.__balance += amount

    def _subtract_balance(self, amount):
        self.__balance -= amount

    # ------------------------------------------------------
    # STATUS
    # ------------------------------------------------------

    def is_active(self):
        return self.__status == "ACTIVE"

    def block(self):
        self.__status = "BLOCKED"

    # ------------------------------------------------------
    # PIN
    # ------------------------------------------------------

    def verify_pin(self, pin):
        return self.__pin == pin

    def change_pin(self, old_pin, new_pin):

        if not self.verify_pin(old_pin):
            raise InvalidPINError("Old PIN is incorrect.")

        if not new_pin.isdigit() or len(new_pin) not in (4, 5):
            raise InvalidPINError(
                "PIN must contain 4 or 5 digits."
            )

        self.__pin = new_pin

    # ------------------------------------------------------
    # DAILY LIMIT RESET
    # ------------------------------------------------------

    def reset_daily_limits(self):

        if self.last_activity_date != date.today():
            self.daily_withdrawal = 0
            self.daily_transfer = 0
            self.last_activity_date = date.today()

    # ------------------------------------------------------
    # DEPOSIT
    # ------------------------------------------------------

    def deposit(self, amount):

        if not self.is_active():
            raise AccountInactiveError(
                "Account is inactive."
            )

        if amount <= 0:
            raise InvalidAmountError(
                "Deposit amount must be positive."
            )

        self._add_balance(amount)

        transaction = DepositTransaction(
            amount,
            self
        )

        self.transactions.append(transaction)

        return transaction

    # ------------------------------------------------------
    # WITHDRAW
    # ------------------------------------------------------

    def withdraw(self, amount, atm):

        if not self.is_active():
            raise AccountInactiveError(
                "Account is inactive."
            )

        if amount <= 0:
            raise InvalidAmountError(
                "Withdrawal amount must be positive."
            )

        if amount < 500:
            raise InvalidAmountError(
                "Minimum withdrawal is Rs.500."
            )

        if amount > self.calculate_withdrawal_limit():
            raise InvalidAmountError(
                "Maximum withdrawal per transaction is Rs.50,000."
            )

        self.reset_daily_limits()

        if self.daily_withdrawal + amount > 100000:
            raise DailyLimitExceededError(
                "Daily withdrawal limit is Rs.100,000."
            )

        if not self.can_withdraw(amount):
            raise InsufficientBalanceError(
                "Insufficient balance / overdraft limit."
            )

        notes = atm.calculate_notes(amount)

        if notes is None:
            raise InsufficientATMFundsError(
                "ATM cannot dispense this amount "
                "with available cash denominations."
            )

        self._subtract_balance(amount)

        self.daily_withdrawal += amount

        atm.dispense_cash(notes)

        transaction = WithdrawalTransaction(
            amount,
            self
        )

        self.transactions.append(transaction)

        return transaction, notes

    # ------------------------------------------------------
    # TRANSFER
    # ------------------------------------------------------

    def transfer(self, receiver, amount):

        if not self.is_active():
            raise AccountInactiveError(
                "Sender account is inactive."
            )

        if not receiver.is_active():
            raise AccountInactiveError(
                "Receiver account is inactive."
            )

        if self.account_number == receiver.account_number:
            raise InvalidAccountError(
                "Sender and receiver cannot be the same."
            )

        if amount <= 0:
            raise InvalidAmountError(
                "Transfer amount must be positive."
            )

        self.reset_daily_limits()

        if self.daily_transfer + amount > 200000:
            raise DailyLimitExceededError(
                "Daily transfer limit is Rs.200,000."
            )

        fee = self.get_transfer_fee()

        total_required = amount + fee

        if not self.can_withdraw(total_required):
            raise InsufficientBalanceError(
                "Insufficient balance for transfer and fee."
            )

        self._subtract_balance(total_required)

        receiver._add_balance(amount)

        self.daily_transfer += amount

        sender_transaction = TransferTransaction(
            amount,
            self,
            receiver,
            "DEBIT"
        )

        receiver_transaction = TransferTransaction(
            amount,
            receiver,
            self,
            "CREDIT"
        )

        self.transactions.append(sender_transaction)
        receiver.transactions.append(receiver_transaction)

        return sender_transaction, fee

    # ------------------------------------------------------
    # FEES
    # ------------------------------------------------------

    @abstractmethod
    def get_withdrawal_fee(self):
        pass

    @abstractmethod
    def get_transfer_fee(self):
        pass

    # ------------------------------------------------------
    # POLYMORPHIC METHODS
    # ------------------------------------------------------

    @abstractmethod
    def calculate_withdrawal_limit(self):
        pass

    @abstractmethod
    def can_withdraw(self, amount):
        pass


# ==========================================================
# SAVINGS ACCOUNT
# ==========================================================

class SavingsAccount(Account):

    MINIMUM_BALANCE = 5000
    WITHDRAWAL_LIMIT = 50000

    def calculate_withdrawal_limit(self):
        return self.WITHDRAWAL_LIMIT

    def can_withdraw(self, amount):

        return (
            self.get_balance() - amount
            >= self.MINIMUM_BALANCE
        )

    def get_withdrawal_fee(self):
        return 50

    def get_transfer_fee(self):
        return 100


# ==========================================================
# CURRENT ACCOUNT
# ==========================================================

class CurrentAccount(Account):

    OVERDRAFT_LIMIT = 50000
    WITHDRAWAL_LIMIT = 50000

    def calculate_withdrawal_limit(self):
        return self.WITHDRAWAL_LIMIT

    def can_withdraw(self, amount):

        return (
            self.get_balance() - amount
            >= -self.OVERDRAFT_LIMIT
        )

    def get_withdrawal_fee(self):
        return 25

    def get_transfer_fee(self):
        return 75


# ==========================================================
# CUSTOMER
# ==========================================================

class Customer:

    def __init__(self, customer_id, name, contact):

        self.customer_id = customer_id
        self.name = name
        self.contact = contact

        self.accounts = []
        self.cards = []

    def add_account(self, account):
        self.accounts.append(account)

    def add_card(self, card):
        self.cards.append(card)


# ==========================================================
# CARD
# ==========================================================

class Card:

    def __init__(self, card_number, customer, account):

        self.card_number = card_number
        self.customer = customer
        self.account = account

        # Encapsulation
        self.__status = "ACTIVE"

        self.failed_attempts = 0

    def is_active(self):
        return self.__status == "ACTIVE"

    def block(self):
        self.__status = "BLOCKED"

    def validate(self, pin):

        if not self.is_active():
            raise CardBlockedError(
                "This ATM card is blocked."
            )

        if not self.account.is_active():
            raise AccountInactiveError(
                "Linked account is inactive."
            )

        if self.account.verify_pin(pin):

            self.failed_attempts = 0
            return True

        self.failed_attempts += 1

        if self.failed_attempts >= 3:

            self.block()
            self.account.block()

            raise CardBlockedError(
                "Card blocked after 3 incorrect PIN attempts."
            )

        attempts_left = 3 - self.failed_attempts

        raise InvalidPINError(
            f"Incorrect PIN. "
            f"{attempts_left} attempt(s) remaining."
        )


# ==========================================================
# BANK
# ==========================================================

class Bank:

    def __init__(self, name):

        self.name = name
        self.customers = []
        self.accounts = {}
        self.cards = {}

    def add_customer(self, customer):

        self.customers.append(customer)

        for account in customer.accounts:
            self.accounts[account.account_number] = account

        for card in customer.cards:
            self.cards[card.card_number] = card

    def find_card(self, card_number):
        return self.cards.get(card_number)

    def find_account(self, account_number):
        return self.accounts.get(account_number)

    def transfer(
        self,
        sender_number,
        receiver_number,
        amount
    ):

        sender = self.find_account(sender_number)
        receiver = self.find_account(receiver_number)

        if sender is None:
            raise InvalidAccountError(
                "Sender account does not exist."
            )

        if receiver is None:
            raise InvalidAccountError(
                "Receiver account does not exist."
            )

        return sender.transfer(receiver, amount)


# ==========================================================
# ATM CASH MANAGEMENT
# ==========================================================

class ATM:

    def __init__(self, atm_id):

        self.atm_id = atm_id

        self.cash = {
            500: 20,
            1000: 30,
            5000: 10
        }

    def total_cash(self):

        return sum(
            denomination * quantity
            for denomination, quantity in self.cash.items()
        )

    def calculate_notes(self, amount):

        if amount > self.total_cash():
            return None

        remaining = amount
        notes = {}

        for denomination in sorted(
            self.cash.keys(),
            reverse=True
        ):

            available = self.cash[denomination]

            required = min(
                remaining // denomination,
                available
            )

            if required > 0:

                notes[denomination] = required

                remaining -= (
                    denomination * required
                )

        if remaining != 0:
            return None

        return notes

    def dispense_cash(self, notes):

        for denomination, quantity in notes.items():

            self.cash[denomination] -= quantity