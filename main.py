import tkinter as tk
from tkinter import messagebox, simpledialog

from classes import (
    Bank,
    ATM,
    Customer,
    Card,
    SavingsAccount,
    CurrentAccount
)

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
# BANK / ATM
# ==========================================================

bank = Bank("National ATM Bank")
atm = ATM("ATM-001")


# ==========================================================
# PRE-REGISTERED CUSTOMERS
# Different cards = different customers
# ==========================================================

# ---------------- CUSTOMER 1 ----------------

customer1 = Customer(
    "C001",
    "Fatima",
    "03001234567"
)

account1 = SavingsAccount(
    "10002345",
    customer1,
    "12345",
    75000
)

card1 = Card(
    "12345",
    customer1,
    account1
)

customer1.add_account(account1)
customer1.add_card(card1)

bank.add_customer(customer1)


# ---------------- CUSTOMER 2 ----------------

customer2 = Customer(
    "C002",
    "Ali",
    "03111234567"
)

account2 = CurrentAccount(
    "10006789",
    customer2,
    "12345",
    100000
)

card2 = Card(
    "123456",
    customer2,
    account2
)

customer2.add_account(account2)
customer2.add_card(card2)

bank.add_customer(customer2)


# ---------------- CUSTOMER 3 ----------------

customer3 = Customer(
    "C003",
    "Sara",
    "03221234567"
)

account3 = SavingsAccount(
    "10007890",
    customer3,
    "12345",
    60000
)

card3 = Card(
    "1234",
    customer3,
    account3
)

customer3.add_account(account3)
customer3.add_card(card3)

bank.add_customer(customer3)


# ---------------- CUSTOMER 4 ----------------

customer4 = Customer(
    "C004",
    "Ahmed",
    "03331234567"
)

account4 = CurrentAccount(
    "10004567",
    customer4,
    "12345",
    120000
)

card4 = Card(
    "1234567",
    customer4,
    account4
)

customer4.add_account(account4)
customer4.add_card(card4)


bank.add_customer(customer4)


# ==========================================================
# ATM GUI
# ==========================================================

class ATMApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "ATM Banking System"
        )

        self.root.geometry(
            "900x650"
        )

        self.root.resizable(
            False,
            False
        )

        self.current_card = None
        self.current_account = None
        self.current_customer = None

        self.card_screen()

    # ------------------------------------------------------
    # CLEAR
    # ------------------------------------------------------

    def clear(self):

        for widget in self.root.winfo_children():
            widget.destroy()

    # ------------------------------------------------------
    # BUTTON
    # ------------------------------------------------------

    def make_button(
        self,
        parent,
        text,
        command
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 13, "bold"),
            width=25,
            height=2
        )

    # ======================================================
    # INSERT CARD
    # ======================================================

    def card_screen(self):

        self.clear()

        tk.Label(
            self.root,
            text="ATM BANKING SYSTEM",
            font=("Arial", 32, "bold")
        ).pack(pady=55)

        tk.Label(
            self.root,
            text="💳  INSERT YOUR CARD",
            font=("Arial", 22, "bold")
        ).pack(pady=10)

        tk.Label(
            self.root,
            text="Enter your card number",
            font=("Arial", 15)
        ).pack(pady=10)

        card_entry = tk.Entry(
            self.root,
            font=("Arial", 20),
            width=15,
            justify="center"
        )

        card_entry.pack(pady=15)

        def insert_card():

            card_number = card_entry.get().strip()

            if not card_number.isdigit():
                messagebox.showerror(
                    "Invalid Card",
                    "Card number must contain digits only."
                )
                return

            card = bank.find_card(card_number)

            if card is None:
                messagebox.showerror(
                    "Invalid Card",
                    "This card is not registered."
                )
                return

            if not card.is_active():
                messagebox.showerror(
                    "Card Blocked",
                    "This card is blocked."
                )
                return

            self.current_card = card
            self.current_customer = card.customer
            self.current_account = card.account

            self.pin_screen()

        self.make_button(
            self.root,
            "ENTER CARD",
            insert_card
        ).pack(pady=25)

    # ======================================================
    # PIN
    # ======================================================

    def pin_screen(self):

        self.clear()

        tk.Label(
            self.root,
            text="ENTER PIN",
            font=("Arial", 32, "bold")
        ).pack(pady=65)

        tk.Label(
            self.root,
            text="Enter 4 or 5 digit PIN",
            font=("Arial", 15)
        ).pack()

        pin_entry = tk.Entry(
            self.root,
            show="*",
            font=("Arial", 22),
            width=10,
            justify="center"
        )

        pin_entry.pack(pady=20)

        def login():

            pin = pin_entry.get().strip()

            if not pin.isdigit() or len(pin) not in (4, 5):

                messagebox.showerror(
                    "Invalid PIN",
                    "PIN must contain 4 or 5 digits."
                )

                return

            try:

                self.current_card.validate(pin)

                self.menu()

            except (
                InvalidPINError,
                CardBlockedError,
                AccountInactiveError
            ) as error:

                messagebox.showerror(
                    "Authentication",
                    str(error)
                )

                if isinstance(error, CardBlockedError):

                    self.current_card = None
                    self.current_account = None
                    self.current_customer = None

                    self.card_screen()

        self.make_button(
            self.root,
            "ENTER PIN",
            login
        ).pack(pady=15)

    # ======================================================
    # ATM MENU
    # ======================================================

    def menu(self):

        self.clear()

        tk.Label(
            self.root,
            text="========== ATM ==========",
            font=("Arial", 30, "bold")
        ).pack(pady=25)

        tk.Label(
            self.root,
            text=(
                f"Welcome, {self.current_customer.name}\n"
                f"Account: {self.current_account.account_number}"
            ),
            font=("Arial", 16)
        ).pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack(pady=25)

        options = [
            ("1. Check Balance", self.check_balance),
            ("2. Deposit", self.deposit),
            ("3. Withdraw", self.withdraw),
            ("4. Transfer Money", self.transfer),
            ("5. Change PIN", self.change_pin),
            ("6. Mini Statement", self.mini_statement),
            ("7. Exit / Remove Card", self.exit)
        ]

        for index, (text, command) in enumerate(options):

            self.make_button(
                frame,
                text,
                command
            ).grid(
                row=index // 2,
                column=index % 2,
                padx=15,
                pady=10
            )

    # ======================================================
    # BALANCE
    # ======================================================

    def check_balance(self):

        balance = self.current_account.get_balance()

        messagebox.showinfo(
            "Balance",
            f"Customer: {self.current_customer.name}\n"
            f"Account: {self.current_account.account_number}\n\n"
            f"Available Balance:\n"
            f"Rs. {balance:,.2f}"
        )

    # ======================================================
    # DEPOSIT
    # ======================================================

    def deposit(self):

        amount = simpledialog.askfloat(
            "Deposit",
            "Enter amount:"
        )

        if amount is None:
            return

        try:

            transaction = self.current_account.deposit(amount)

            messagebox.showinfo(
                "Deposit Successful",
                f"Amount: Rs. {amount:,.2f}\n\n"
                f"Transaction ID:\n"
                f"{transaction.transaction_id}\n\n"
                f"New Balance:\n"
                f"Rs. {self.current_account.get_balance():,.2f}"
            )

        except (
            InvalidAmountError,
            AccountInactiveError
        ) as error:

            messagebox.showerror(
                "Deposit Error",
                str(error)
            )

    # ======================================================
    # WITHDRAW
    # ======================================================

    def withdraw(self):

        amount = simpledialog.askfloat(
            "Withdraw",
            "Enter amount:"
        )

        if amount is None:
            return

        try:

            transaction, notes = (
                self.current_account.withdraw(
                    amount,
                    atm
                )
            )

            fee = self.current_account.get_withdrawal_fee()

            note_text = ""

            for denomination, quantity in notes.items():

                note_text += (
                    f"Rs.{denomination} × {quantity}\n"
                )

            messagebox.showinfo(
                "Withdrawal Successful",
                f"Amount: Rs. {amount:,.2f}\n"
                f"Withdrawal Fee: Rs. {fee}\n\n"
                f"Transaction ID:\n"
                f"{transaction.transaction_id}\n\n"
                f"Cash Dispensed:\n"
                f"{note_text}\n"
                f"Remaining Balance:\n"
                f"Rs. {self.current_account.get_balance():,.2f}"
            )

        except (
            InvalidAmountError,
            InsufficientBalanceError,
            InsufficientATMFundsError,
            AccountInactiveError,
            DailyLimitExceededError
        ) as error:

            messagebox.showerror(
                "Withdrawal Error",
                str(error)
            )

    # ======================================================
    # TRANSFER
    # ======================================================

    def transfer(self):

        receiver_number = simpledialog.askstring(
            "Transfer",
            "Enter receiver account number:"
        )

        if not receiver_number:
            return

        amount = simpledialog.askfloat(
            "Transfer",
            "Enter amount:"
        )

        if amount is None:
            return

        try:

            transaction, fee = bank.transfer(
                self.current_account.account_number,
                receiver_number,
                amount
            )

            messagebox.showinfo(
                "Transfer Successful",
                f"Transferred: Rs. {amount:,.2f}\n"
                f"Transfer Fee: Rs. {fee}\n\n"
                f"Transaction ID:\n"
                f"{transaction.transaction_id}\n\n"
                f"New Balance:\n"
                f"Rs. {self.current_account.get_balance():,.2f}"
            )

        except (
            InvalidAccountError,
            InvalidAmountError,
            InsufficientBalanceError,
            AccountInactiveError,
            DailyLimitExceededError
        ) as error:

            messagebox.showerror(
                "Transfer Error",
                str(error)
            )

    # ======================================================
    # CHANGE PIN
    # ======================================================

    def change_pin(self):

        old_pin = simpledialog.askstring(
            "Change PIN",
            "Enter old PIN:",
            show="*"
        )

        if old_pin is None:
            return

        new_pin = simpledialog.askstring(
            "Change PIN",
            "Enter new PIN:",
            show="*"
        )

        if new_pin is None:
            return

        try:

            self.current_account.change_pin(
                old_pin,
                new_pin
            )

            messagebox.showinfo(
                "Success",
                "PIN changed successfully."
            )

        except InvalidPINError as error:

            messagebox.showerror(
                "PIN Error",
                str(error)
            )

    # ======================================================
    # MINI STATEMENT
    # ======================================================

    def mini_statement(self):

        window = tk.Toplevel(self.root)

        window.title("Mini Statement")
        window.geometry("750x500")

        tk.Label(
            window,
            text="========== MINI STATEMENT ==========",
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        tk.Label(
            window,
            text=f"Account: "
                 f"{self.current_account.account_number}",
            font=("Arial", 14)
        ).pack()

        transactions = (
            self.current_account.transactions[-5:]
        )

        if not transactions:

            tk.Label(
                window,
                text="No transactions yet.",
                font=("Arial", 14)
            ).pack(pady=30)

        else:

            for transaction in reversed(transactions):

                if transaction.get_type() == "DEPOSIT":
                    sign = "+"

                elif transaction.get_type() == "WITHDRAWAL":
                    sign = "-"

                else:
                    sign = "-"

                text = (
                    f"{transaction.date_time.strftime('%d-%b-%Y %H:%M')}   "
                    f"{transaction.get_type():12}   "
                    f"{sign}Rs.{transaction.amount:,.2f}"
                )

                tk.Label(
                    window,
                    text=text,
                    font=("Arial", 12)
                ).pack(pady=5)

        tk.Label(
            window,
            text=(
                f"\nCurrent Balance: "
                f"Rs. {self.current_account.get_balance():,.2f}"
            ),
            font=("Arial", 15, "bold")
        ).pack(pady=20)

    # ======================================================
    # EXIT / REMOVE CARD
    # ======================================================

    def exit(self):

        self.current_card = None
        self.current_account = None
        self.current_customer = None

        self.card_screen()


# ==========================================================
# START
# ==========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ATMApp(root)

    root.mainloop()