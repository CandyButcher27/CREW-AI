import datetime
from typing import Dict, List, Any

# --- External Dependency / Mock Implementation ---

def get_share_price(symbol: str) -> float:
    """
    Simulates fetching the current market price for a given stock symbol.
    In a real application, this function would typically interact with an
    external market data API (e.g., Yahoo Finance API, Alpha Vantage).

    For the purpose of this self-contained module and testing, fixed prices
    are returned for a few common symbols.

    Args:
        symbol (str): The stock ticker symbol (e.g., 'AAPL', 'TSLA').

    Returns:
        float: The current price of one share of the given symbol.
               Returns 0.0 if the symbol is not recognized in this mock.
    """
    prices = {
        "AAPL": 170.00,
        "TSLA": 250.00,
        "GOOGL": 120.00,
        "MSFT": 320.00,
        "AMZN": 130.00,
        "NVDA": 450.00,
    }
    return prices.get(symbol.upper(), 0.0)

# --- Class: Account ---

class Account:
    """
    Manages a single user's trading account within a simulation platform.
    This includes managing cash balance, stock holdings, and a comprehensive
    history of all financial and trading transactions.
    """

    def __init__(self, account_id: str):
        """
        Initializes a new Account instance.

        Args:
            account_id (str): A unique identifier for the account.
        """
        self.account_id: str = account_id
        self._balance: float = 0.0  # Current cash balance
        self._initial_deposit_total: float = 0.0  # Cumulative sum of all deposits
        self._holdings: Dict[str, int] = {}  # Stock symbol -> quantity held
        self._transactions: List[Dict[str, Any]] = []  # List of recorded transactions

    def _record_transaction(
        self,
        transaction_type: str,
        cash_change: float,
        symbol: str = None,
        quantity: int = None,
        price_per_share: float = None,
        success: bool = True,
        message: str = ""
    ) -> None:
        """
        Internal helper method to record a transaction in the _transactions list.

        Args:
            transaction_type (str): Type of transaction (e.g., 'deposit', 'withdraw', 'buy', 'sell').
            cash_change (float): The effect this transaction had on the cash balance.
                                 Positive for cash inflow, negative for cash outflow.
            symbol (str, optional): Stock symbol for share transactions. Defaults to None.
            quantity (int, optional): Number of shares for share transactions. Defaults to None.
            price_per_share (float, optional): Price per share for share transactions. Defaults to None.
            success (bool, optional): Indicates if the transaction was successful. Defaults to True.
            message (str, optional): An optional message providing more details about the transaction.
        """
        transaction = {
            'timestamp': datetime.datetime.now().isoformat(),
            'type': transaction_type,
            'amount_effect_on_cash': cash_change,
            'symbol': symbol,
            'quantity': quantity,
            'price_per_share': price_per_share,
            'balance_after': self._balance,  # Record balance after transaction
            'success': success,
            'message': message
        }
        self._transactions.append(transaction)

    def deposit(self, amount: float) -> bool:
        """
        Adds funds to the account's cash balance. Records a 'deposit' transaction.

        Args:
            amount (float): The positive amount of money to deposit.

        Returns:
            bool: True if the deposit was successful, False otherwise.
        """
        if amount <= 0:
            self._record_transaction(
                "deposit", 0.0, success=False, message="Deposit amount must be positive."
            )
            return False
        
        self._balance += amount
        self._initial_deposit_total += amount  # Accumulate for profit/loss calculation
        self._record_transaction(
            "deposit", amount, success=True, message=f"Deposited {amount:.2f}"
        )
        return True

    def withdraw(self, amount: float) -> bool:
        """
        Removes funds from the account's cash balance. Records a 'withdraw' transaction.

        Args:
            amount (float): The positive amount of money to withdraw.

        Returns:
            bool: True if the withdrawal was successful, False otherwise.
        """
        if amount <= 0:
            self._record_transaction(
                "withdraw", 0.0, success=False, message="Withdrawal amount must be positive."
            )
            return False
        
        if self._balance < amount:
            self._record_transaction(
                "withdraw", -amount, success=False,
                message=f"Insufficient funds. Available: {self._balance:.2f}, Requested: {amount:.2f}"
            )
            return False
        
        self._balance -= amount
        self._record_transaction(
            "withdraw", -amount, success=True, message=f"Withdrew {amount:.2f}"
        )
        return True

    def buy_shares(self, symbol: str, quantity: int) -> bool:
        """
        Purchases shares of a given stock. Funds are deducted from the cash balance.
        Records a 'buy' transaction.

        Args:
            symbol (str): The stock ticker symbol (e.g., 'AAPL').
            quantity (int): The number of shares to buy.

        Returns:
            bool: True if the purchase was successful, False otherwise.
        """
        if quantity <= 0:
            self._record_transaction(
                "buy", 0.0, symbol, quantity, success=False, message="Quantity must be positive."
            )
            return False

        price = get_share_price(symbol)
        if price <= 0:
            self._record_transaction(
                "buy", 0.0, symbol, quantity, price, success=False,
                message=f"Invalid or unknown symbol: {symbol}. Cannot get price."
            )
            return False

        cost = price * quantity
        if self._balance < cost:
            self._record_transaction(
                "buy", -cost, symbol, quantity, price, success=False,
                message=f"Insufficient funds to buy {quantity} {symbol}. Cost: {cost:.2f}, Available: {self._balance:.2f}"
            )
            return False
        
        self._balance -= cost
        self._holdings[symbol.upper()] = self._holdings.get(symbol.upper(), 0) + quantity
        self._record_transaction(
            "buy", -cost, symbol, quantity, price, success=True,
            message=f"Bought {quantity} {symbol} at {price:.2f} each."
        )
        return True

    def sell_shares(self, symbol: str, quantity: int) -> bool:
        """
        Sells shares of a given stock. Funds are added to the cash balance.
        Records a 'sell' transaction.

        Args:
            symbol (str): The stock ticker symbol (e.g., 'AAPL').
            quantity (int): The number of shares to sell.

        Returns:
            bool: True if the sale was successful, False otherwise.
        """
        if quantity <= 0:
            self._record_transaction(
                "sell", 0.0, symbol, quantity, success=False, message="Quantity must be positive."
            )
            return False
        
        symbol_upper = symbol.upper()
        if self._holdings.get(symbol_upper, 0) < quantity:
            self._record_transaction(
                "sell", 0.0, symbol, quantity, success=False,
                message=f"Not enough {symbol} shares to sell. Have: {self._holdings.get(symbol_upper, 0)}, Requested: {quantity}"
            )
            return False
        
        price = get_share_price(symbol)
        if price <= 0:
            self._record_transaction(
                "sell", 0.0, symbol, quantity, price, success=False,
                message=f"Invalid or unknown symbol: {symbol}. Cannot get price."
            )
            return False
            
        revenue = price * quantity
        self._balance += revenue
        self._holdings[symbol_upper] -= quantity
        
        # Clean up holdings if quantity becomes zero
        if self._holdings[symbol_upper] == 0:
            del self._holdings[symbol_upper]

        self._record_transaction(
            "sell", revenue, symbol, quantity, price, success=True,
            message=f"Sold {quantity} {symbol} at {price:.2f} each."
        )
        return True

    def get_balance(self) -> float:
        """
        Returns the current cash balance in the account.

        Returns:
            float: The current cash balance.
        """
        return self._balance

    def get_holdings(self) -> Dict[str, int]:
        """
        Returns a copy of the current stock holdings.

        Returns:
            Dict[str, int]: A dictionary mapping stock symbols to quantities held.
                            Returns a copy to prevent external modification of internal state.
        """
        return self._holdings.copy()

    def get_initial_deposit_total(self) -> float:
        """
        Returns the total cumulative amount deposited into the account.
        This amount is used as the base for calculating overall profit/loss.

        Returns:
            float: The total amount deposited.
        """
        return self._initial_deposit_total

    def get_portfolio_value(self) -> float:
        """
        Calculates the total current value of the portfolio. This includes
        the cash balance and the current market value of all held shares.

        Returns:
            float: The total portfolio value.
        """
        total_shares_value = 0.0
        for symbol, quantity in self._holdings.items():
            price = get_share_price(symbol)
            total_shares_value += price * quantity
        return self._balance + total_shares_value

    def get_profit_loss(self) -> float:
        """
        Calculates the profit or loss of the account based on the current
        portfolio value relative to the total initial deposits.

        Returns:
            float: The profit or loss. Positive value for profit, negative for loss.
        """
        return self.get_portfolio_value() - self._initial_deposit_total

    def get_transactions(self) -> List[Dict[str, Any]]:
        """
        Returns a chronological list of all recorded transactions for the account.

        Returns:
            List[Dict[str, Any]]: A list where each element is a dictionary
                                  representing a transaction. Returns a copy
                                  to prevent external modification.
        """
        return self._transactions.copy()


# --- Example Usage (for testing/demonstration) ---

if __name__ == "__main__":
    print("--- Initializing Account ---")
    account = Account("user123_trading_account")
    print(f"Account ID: {account.account_id}")
    print(f"Current Balance: ${account.get_balance():.2f}")
    print(f"Holdings: {account.get_holdings()}")
    print(f"Initial Deposit Total: ${account.get_initial_deposit_total():.2f}")
    print(f"Portfolio Value: ${account.get_portfolio_value():.2f}")
    print(f"Profit/Loss: ${account.get_profit_loss():.2f}")

    print("\n--- Depositing Funds ($10,000) ---")
    if account.deposit(10000.00):
        print(f"Successfully deposited $10,000.00.")
    else:
        print("Failed to deposit funds.")
    print(f"Current Balance: ${account.get_balance():.2f}")
    print(f"Initial Deposit Total: ${account.get_initial_deposit_total():.2f}")
    print(f"Portfolio Value: ${account.get_portfolio_value():.2f}")
    print(f"Profit/Loss: ${account.get_profit_loss():.2f}")

    print("\n--- Buying AAPL Shares (50 shares) ---")
    if account.buy_shares("AAPL", 50):
        print(f"Successfully bought 50 AAPL shares.")
    else:
        print("Failed to buy AAPL shares.")
    print(f"Current Balance: ${account.get_balance():.2f}")
    print(f"Holdings: {account.get_holdings()}")
    print(f"Portfolio Value: ${account.get_portfolio_value():.2f}")
    print(f"Profit/Loss: ${account.get_profit_loss():.2f}")

    print("\n--- Buying TSLA Shares (10 shares) ---")
    if account.buy_shares("TSLA", 10):
        print(f"Successfully bought 10 TSLA shares.")
    else:
        print("Failed to buy TSLA shares.")
    print(f"Current Balance: ${account.get_balance():.2f}")
    print(f"Holdings: {account.get_holdings()}")
    print(f"Portfolio Value: ${account.get_portfolio_value():.2f}")
    print(f"Profit/Loss: ${account.get_profit_loss():.2f}")

    print("\n--- Attempting to buy too many GOOGL Shares (1000 shares) ---")
    if account.buy_shares("GOOGL", 1000):  # Should fail due to insufficient funds
        print(f"Successfully bought 1000 GOOGL shares (UNEXPECTED).")
    else:
        print("Failed to buy 1000 GOOGL shares (EXPECTED). Insufficient funds.")
    print(f"Current Balance: ${account.get_balance():.2f}")
    print(f"Holdings: {account.get_holdings()}")

    print("\n--- Selling AAPL Shares (20 shares) ---")
    if account.sell_shares("AAPL", 20):
        print(f"Successfully sold 20 AAPL shares.")
    else:
        print("Failed to sell AAPL shares.")
    print(f"Current Balance: ${account.get_balance():.2f}")
    print(f"Holdings: {account.get_holdings()}")
    print(f"Portfolio Value: ${account.get_portfolio_value():.2f}")
    print(f"Profit/Loss: ${account.get_profit_loss():.2f}")

    print("\n--- Attempting to sell non-existent shares (MSFT) ---")
    if account.sell_shares("MSFT", 5):  # Should fail as no MSFT shares are held
        print(f"Successfully sold 5 MSFT shares (UNEXPECTED).")
    else:
        print("Failed to sell 5 MSFT shares (EXPECTED). Not enough shares.")
    print(f"Current Balance: ${account.get_balance():.2f}")
    print(f"Holdings: {account.get_holdings()}")

    print("\n--- Withdrawing Funds ($1,000) ---")
    if account.withdraw(1000.00):
        print(f"Successfully withdrew $1,000.00.")
    else:
        print("Failed to withdraw funds.")
    print(f"Current Balance: ${account.get_balance():.2f}")

    print("\n--- Attempting to withdraw too much ($20,000) ---")
    if account.withdraw(20000.00):  # Should fail due to insufficient funds
        print(f"Successfully withdrew $20,000.00 (UNEXPECTED).")
    else:
        print("Failed to withdraw $20,000.00 (EXPECTED). Insufficient funds.")
    print(f"Current Balance: ${account.get_balance():.2f}")

    print("\n--- Final State of Account ---")
    print(f"Account ID: {account.account_id}")
    print(f"Current Balance: ${account.get_balance():.2f}")
    print(f"Holdings: {account.get_holdings()}")
    print(f"Initial Deposit Total: ${account.get_initial_deposit_total():.2f}")
    print(f"Portfolio Value: ${account.get_portfolio_value():.2f}")
    print(f"Profit/Loss: ${account.get_profit_loss():.2f}")

    print("\n--- Full Transaction History ---")
    transactions = account.get_transactions()
    if not transactions:
        print("No transactions recorded.")
    for i, transaction in enumerate(transactions):
        print(f"  {i+1}. {transaction}")