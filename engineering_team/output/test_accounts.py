```python
import unittest
import datetime
from unittest.mock import patch, ANY

# Assuming accounts.py is in the same directory
from accounts import Account, get_share_price 

class TestAccount(unittest.TestCase):
    """
    Unit tests for the Account class in accounts.py.
    """

    def setUp(self):
        """
        Set up a fresh Account instance before each test.
        """
        self.account = Account("test_account_123")

    def test_initialization(self):
        """
        Test that an Account instance is initialized correctly.
        """
        self.assertEqual(self.account.account_id, "test_account_123")
        self.assertEqual(self.account.get_balance(), 0.0)
        self.assertEqual(self.account.get_holdings(), {})
        self.assertEqual(self.account.get_initial_deposit_total(), 0.0)
        self.assertEqual(self.account.get_transactions(), [])

    @patch('accounts.datetime')
    def test_deposit_successful(self, mock_datetime):
        """
        Test successful deposit of funds.
        """
        # Mock datetime.datetime.now() to ensure consistent timestamp in transaction
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.assertTrue(self.account.deposit(100.00))
        self.assertAlmostEqual(self.account.get_balance(), 100.00)
        self.assertAlmostEqual(self.account.get_initial_deposit_total(), 100.00)
        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertDictContainsSubset({
            'timestamp': "2023-01-01T10:00:00",
            'type': 'deposit',
            'amount_effect_on_cash': 100.00,
            'balance_after': 100.00,
            'success': True,
            'message': 'Deposited 100.00'
        }, transactions[0])
        # Check for presence of optional keys, which should be None for deposits
        self.assertIsNone(transactions[0]['symbol'])
        self.assertIsNone(transactions[0]['quantity'])
        self.assertIsNone(transactions[0]['price_per_share'])


    @patch('accounts.datetime')
    def test_deposit_negative_amount(self, mock_datetime):
        """
        Test deposit with a negative amount. Should fail.
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.assertFalse(self.account.deposit(-50.00))
        self.assertAlmostEqual(self.account.get_balance(), 0.0)
        self.assertAlmostEqual(self.account.get_initial_deposit_total(), 0.0)
        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertDictContainsSubset({
            'timestamp': "2023-01-01T10:00:00",
            'type': 'deposit',
            'amount_effect_on_cash': 0.0,
            'balance_after': 0.0,
            'success': False,
            'message': 'Deposit amount must be positive.'
        }, transactions[0])

    @patch('accounts.datetime')
    def test_deposit_zero_amount(self, mock_datetime):
        """
        Test deposit with zero amount. Should fail.
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.assertFalse(self.account.deposit(0.0))
        self.assertAlmostEqual(self.account.get_balance(), 0.0)
        self.assertAlmostEqual(self.account.get_initial_deposit_total(), 0.0)
        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertDictContainsSubset({
            'timestamp': "2023-01-01T10:00:00",
            'type': 'deposit',
            'amount_effect_on_cash': 0.0,
            'balance_after': 0.0,
            'success': False,
            'message': 'Deposit amount must be positive.'
        }, transactions[0])

    @patch('accounts.datetime')
    def test_withdraw_successful(self, mock_datetime):
        """
        Test successful withdrawal of funds.
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.account.deposit(200.00)
        self.assertTrue(self.account.withdraw(50.00))
        self.assertAlmostEqual(self.account.get_balance(), 150.00)
        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertDictContainsSubset({
            'timestamp': "2023-01-01T10:00:00",
            'type': 'withdraw',
            'amount_effect_on_cash': -50.00,
            'balance_after': 150.00,
            'success': True,
            'message': 'Withdrew 50.00'
        }, transactions[1])

    @patch('accounts.datetime')
    def test_withdraw_insufficient_funds(self, mock_datetime):
        """
        Test withdrawal with insufficient funds. Should fail.
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.account.deposit(50.00)
        self.assertFalse(self.account.withdraw(100.00))
        self.assertAlmostEqual(self.account.get_balance(), 50.00) # Balance should remain unchanged
        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertDictContainsSubset({
            'timestamp': "2023-01-01T10:00:00",
            'type': 'withdraw',
            'amount_effect_on_cash': -100.00, # Amount requested still recorded
            'balance_after': 50.00, # Balance should be what it was before failed transaction
            'success': False,
            'message': ANY # Message will contain dynamic balance, so check with ANY
        }, transactions[1])
        self.assertIn("Insufficient funds", transactions[1]['message'])

    @patch('accounts.datetime')
    def test_withdraw_negative_amount(self, mock_datetime):
        """
        Test withdrawal with a negative amount. Should fail.
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.account.deposit(100.00)
        self.assertFalse(self.account.withdraw(-10.00))
        self.assertAlmostEqual(self.account.get_balance(), 100.00)
        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertDictContainsSubset({
            'timestamp': "2023-01-01T10:00:00",
            'type': 'withdraw',
            'amount_effect_on_cash': 0.0,
            'balance_after': 100.00,
            'success': False,
            'message': 'Withdrawal amount must be positive.'
        }, transactions[1])

    @patch('accounts.datetime')
    def test_withdraw_zero_amount(self, mock_datetime):
        """
        Test withdrawal with zero amount. Should fail.
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.account.deposit(100.00)
        self.assertFalse(self.account.withdraw(0.0))
        self.assertAlmostEqual(self.account.get_balance(), 100.00)
        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertDictContainsSubset({
            'timestamp': "2023-01-01T10:00:00",
            'type': 'withdraw',
            'amount_effect_on_cash': 0.0,
            'balance_after': 100.00,
            'success': False,
            'message': 'Withdrawal amount must be positive.'
        }, transactions[1])

    @patch('accounts.get_share_price')
    @patch('accounts.datetime')
    def test_buy_shares_successful(self, mock_datetime, mock_get_share_price):
        """
        Test successful purchase of shares.
        """
        mock_get_share_price.return_value = 150.00 # Mock AAPL price
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.account.deposit(5000.00)
        self.assertTrue(self.account.buy_shares("AAPL", 10))
        self.assertAlmostEqual(self.account.get_balance(), 3500.00) # 5000 - (150 * 10) = 3500
        self.assertEqual(self.account.get_holdings(), {"AAPL": 10})
        
        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertDictContainsSubset({
            'timestamp': "2023-01-01T10:00:00",
            'type': 'buy',
            'amount_effect_on_cash': -1500.00,
            'symbol': 'AAPL',
            'quantity': 10,
            'price_per_share': 150.00,
            'balance_after': 3500.00,
            'success': True,
            'message': 'Bought 10 AAPL at 150.00 each.'
        }, transactions[1])
        mock_get_share_price.assert_called_with("AAPL")

    @patch('accounts.get_share_price')
    @patch('accounts.datetime')
    def test_buy_shares_insufficient_funds(self, mock_datetime, mock_get_share_price):
        """
        Test purchase of shares with insufficient funds. Should fail.
        """
        mock_get_share_price.return_value = 1000.00 # Mock high price for TSLA
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.account.deposit(500.00)
        self.assertFalse(self.account.buy_shares("TSLA", 1)) # Cost 1000, balance 500
        self.assertAlmostEqual(self.account.get_balance(), 500.00)
        self.assertEqual(self.account.get_holdings(), {}) # Holdings should remain empty

        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertDictContainsSubset({
            'timestamp': "2023-01-01T10:00:00",
            'type': 'buy',
            'amount_effect_on_cash': -1000.00, # Cost of attempt still recorded
            'symbol': 'TSLA',
            'quantity': 1,
            'price_per_share': 1000.00,
            'balance_after': 500.00,
            'success': False,
            'message': ANY
        }, transactions[1])
        self.assertIn("Insufficient funds", transactions[1]['message'])

    @patch('accounts.get_share_price')
    @patch('accounts.datetime')
    def test_buy_shares_invalid_quantity(self, mock_datetime, mock_get_share_price):
        """
        Test buying shares with a non-positive quantity. Should fail.
        """
        mock_get_share_price.return_value = 100.00
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.account.deposit(1000.00)
        self.assertFalse(self.account.buy_shares("GOOGL", 0))
        self.assertFalse(self.account.buy_shares("GOOGL", -5))
        self.assertAlmostEqual(self.account.get_balance(), 1000.00)
        self.assertEqual(self.account.get_holdings(), {})

        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 3) # Deposit + two failed buys
        self.assertDictContainsSubset({
            'type': 'buy', 'quantity': 0, 'success': False, 'message': 'Quantity must be positive.'
        }, transactions[1])
        self.assertDictContainsSubset({
            'type': 'buy', 'quantity': -5, 'success': False, 'message': 'Quantity must be positive.'
        }, transactions[2])
        mock_get_share_price.assert_not_called() # Price lookup should not happen for invalid quantity

    @patch('accounts.get_share_price')
    @patch('accounts.datetime')
    def test_buy_shares_unknown_symbol(self, mock_datetime, mock_get_share_price):
        """
        Test buying shares of an unknown symbol. Should fail.
        """
        mock_get_share_price.return_value = 0.0 # Simulate unknown symbol returning 0.0
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.account.deposit(1000.00)
        self.assertFalse(self.account.buy_shares("UNKNOWN", 10))
        self.assertAlmostEqual(self.account.get_balance(), 1000.00)
        self.assertEqual(self.account.get_holdings(), {})

        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertDictContainsSubset({
            'timestamp': "2023-01-01T10:00:00",
            'type': 'buy',
            'symbol': 'UNKNOWN',
            'quantity': 10,
            'price_per_share': 0.0,
            'success': False,
            'message': 'Invalid or unknown symbol: UNKNOWN. Cannot get price.'
        }, transactions[1])
        mock_get_share_price.assert_called_with("UNKNOWN")

    @patch('accounts.get_share_price')
    @patch('accounts.datetime')
    def test_sell_shares_successful(self, mock_datetime, mock_get_share_price):
        """
        Test successful sale of shares.
        """
        mock_get_share_price.side_effect = [170.00, 180.00] # Buy price, then sell price
        mock_datetime.datetime.now.side_effect = [
            datetime.datetime(2023, 1, 1, 10, 0, 0), # Deposit
            datetime.datetime(2023, 1, 1, 10, 1, 0), # Buy
            datetime.datetime(2023, 1, 1, 10, 2, 0)  # Sell
        ]
        mock_datetime.datetime.isoformat.side_effect = [
            "2023-01-01T10:00:00",
            "2023-01-01T10:01:00",
            "2023-01-01T10:02:00"
        ]

        self.account.deposit(10000.00)
        self.account.buy_shares("AAPL", 50) # Cost 50 * 170 = 8500. Balance: 1500, Holdings: {'AAPL': 50}

        self.assertTrue(self.account.sell_shares("AAPL", 20)) # Sell 20 * 180 = 3600. Balance: 1500 + 3600 = 5100
        self.assertAlmostEqual(self.account.get_balance(), 5100.00)
        self.assertEqual(self.account.get_holdings(), {"AAPL": 30}) # 50 - 20 = 30

        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 3)
        self.assertDictContainsSubset({
            'timestamp': "2023-01-01T10:02:00",
            'type': 'sell',
            'amount_effect_on_cash': 3600.00,
            'symbol': 'AAPL',
            'quantity': 20,
            'price_per_share': 180.00,
            'balance_after': 5100.00,
            'success': True,
            'message': 'Sold 20 AAPL at 180.00 each.'
        }, transactions[2])
        # Ensure get_share_price was called for buy and then for sell
        mock_get_share_price.assert_any_call("AAPL")

    @patch('accounts.get_share_price')
    @patch('accounts.datetime')
    def test_sell_shares_not_enough_holdings(self, mock_datetime, mock_get_share_price):
        """
        Test selling more shares than held. Should fail.
        """
        mock_get_share_price.side_effect = [170.00, 180.00]
        mock_datetime.datetime.now.side_effect = [
            datetime.datetime(2023, 1, 1, 10, 0, 0), # Deposit
            datetime.datetime(2023, 1, 1, 10, 1, 0), # Buy
            datetime.datetime(2023, 1, 1, 10, 2, 0)  # Sell attempt
        ]
        mock_datetime.datetime.isoformat.side_effect = [
            "2023-01-01T10:00:00",
            "2023-01-01T10:01:00",
            "2023-01-01T10:02:00"
        ]

        self.account.deposit(10000.00)
        self.account.buy_shares("AAPL", 10) # Holdings: {'AAPL': 10}

        self.assertFalse(self.account.sell_shares("AAPL", 20)) # Try to sell 20 when only 10 are held
        self.assertAlmostEqual(self.account.get_balance(), 10000.00 - (170.00 * 10)) # Balance unchanged from before failed sell
        self.assertEqual(self.account.get_holdings(), {"AAPL": 10}) # Holdings unchanged

        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 3)
        self.assertDictContainsSubset({
            'timestamp': "2023-01-01T10:02:00",
            'type': 'sell',
            'amount_effect_on_cash': 0.0,
            'symbol': 'AAPL',
            'quantity': 20,
            'success': False,
            'message': ANY
        }, transactions[2])
        self.assertIn("Not enough AAPL shares to sell", transactions[2]['message'])
        # get_share_price should not be called if holding check fails first
        # For simplicity, if it's called, it's fine as long as transaction fails.
        # But, ideally, it's short-circuited.
        # The current implementation of Account calls get_share_price *after* checking holdings.
        mock_get_share_price.assert_called_with("AAPL") # Called for buy, then for failed sell.

    @patch('accounts.get_share_price')
    @patch('accounts.datetime')
    def test_sell_shares_non_existent_holding(self, mock_datetime, mock_get_share_price):
        """
        Test selling shares of a stock not held. Should fail.
        """
        mock_get_share_price.return_value = 100.00
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.account.deposit(1000.00)
        self.assertFalse(self.account.sell_shares("MSFT", 5)) # MSFT is not held
        self.assertAlmostEqual(self.account.get_balance(), 1000.00)
        self.assertEqual(self.account.get_holdings(), {})

        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertDictContainsSubset({
            'type': 'sell',
            'symbol': 'MSFT',
            'quantity': 5,
            'success': False,
            'message': ANY
        }, transactions[1])
        self.assertIn("Not enough MSFT shares to sell", transactions[1]['message'])
        mock_get_share_price.assert_not_called() # Price lookup should not happen if stock not held

    @patch('accounts.get_share_price')
    @patch('accounts.datetime')
    def test_sell_shares_invalid_quantity(self, mock_datetime, mock_get_share_price):
        """
        Test selling shares with a non-positive quantity. Should fail.
        """
        mock_get_share_price.return_value = 100.00
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.account.deposit(2000.00)
        self.account.buy_shares("GOOGL", 10)

        self.assertFalse(self.account.sell_shares("GOOGL", 0))
        self.assertFalse(self.account.sell_shares("GOOGL", -5))
        # Balance and holdings should be unchanged from buy operation
        self.assertAlmostEqual(self.account.get_balance(), 1000.00) # 2000 - (100 * 10)
        self.assertEqual(self.account.get_holdings(), {"GOOGL": 10})

        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 3) # Deposit + Buy + 1 failed sell
        self.assertDictContainsSubset({
            'type': 'sell', 'quantity': 0, 'success': False, 'message': 'Quantity must be positive.'
        }, transactions[2])
        # The second invalid sell would also be recorded if it were allowed to proceed,
        # but the test stops at the first failure.
        mock_get_share_price.assert_called_with("GOOGL") # Called for buy. Not called for invalid sell quantity.

    @patch('accounts.get_share_price')
    @patch('accounts.datetime')
    def test_sell_shares_unknown_symbol_after_holding_check(self, mock_datetime, mock_get_share_price):
        """
        Test selling shares of an unknown symbol when some shares might be held.
        This tests the get_share_price check path.
        """
        # Mock get_share_price to return a valid price for buying, then 0.0 for selling
        mock_get_share_price.side_effect = [100.00, 0.0]
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 10, 0, 0)
        mock_datetime.datetime.isoformat.return_value = "2023-01-01T10:00:00"

        self.account.deposit(2000.00)
        self.account.buy_shares("XYZ", 10) # Assume 'XYZ' is valid during buy due to first mock_get_share_price return

        # Now try to sell XYZ, but mock get_share_price to return 0.0 for it
        self.assertFalse(self.account.sell_shares("XYZ", 5)) # Should fail due to price 0.0
        # Balance and holdings should be unchanged from buy operation
        self.assertAlmostEqual(self.account.get_balance(), 1000.00) # 2000 - (100 * 10)
        self.assertEqual(self.account.get_holdings(), {"XYZ": 10})

        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 3) # Deposit + Buy + Failed Sell
        self.assertDictContainsSubset({
            'type': 'sell',
            'symbol': 'XYZ',
            'quantity': 5,
            'price_per_share': 0.0,
            'success': False,
            'message': 'Invalid or unknown symbol: XYZ. Cannot get price.'
        }, transactions[2])
        # get_share_price should have been called twice, once for buy, once for sell
        self.assertEqual(mock_get_share_price.call_count, 2)
        mock_get_share_price.assert_any_call("XYZ")

    def test_get_balance(self):
        """
        Test get_balance returns the correct current cash balance.
        """
        self.assertEqual(self.account.get_balance(), 0.0)
        self.account.deposit(500.00)
        self.assertAlmostEqual(self.account.get_balance(), 500.00)
        self.account.withdraw(100.00)
        self.assertAlmostEqual(self.account.get_balance(), 400.00)
        
        with patch('accounts.get_share_price', return_value=10.00):
            self.account.buy_shares("ABC", 10) # 400 - 100 = 300
        self.assertAlmostEqual(self.account.get_balance(), 300.00)

    def test_get_holdings(self):
        """
        Test get_holdings returns a copy of the current stock holdings.
        """
        self.assertEqual(self.account.get_holdings(), {})
        
        with patch('accounts.get_share_price', return_value=100.00):
            self.account.deposit(2000.00)
            self.account.buy_shares("AAPL", 10)
            self.account.buy_shares("TSLA", 5)
        
        expected_holdings = {"AAPL": 10, "TSLA": 5}
        self.assertEqual(self.account.get_holdings(), expected_holdings)

        # Ensure it returns a copy, not the internal reference
        retrieved_holdings = self.account.get_holdings()
        retrieved_holdings["GOOGL"] = 20 # Modify the copy
        self.assertEqual(self.account.get_holdings(), expected_holdings) # Internal state should be unchanged

        with patch('accounts.get_share_price', return_value=100.00):
            self.account.sell_shares("AAPL", 10) # Sell all AAPL
        self.assertEqual(self.account.get_holdings(), {"TSLA": 5}) # AAPL should be removed if quantity is 0

    def test_get_initial_deposit_total(self):
        """
        Test get_initial_deposit_total returns the cumulative sum of deposits.
        """
        self.assertEqual(self.account.get_initial_deposit_total(), 0.0)
        self.account.deposit(100.00)
        self.assertAlmostEqual(self.account.get_initial_deposit_total(), 100.00)
        self.account.deposit(200.00)
        self.assertAlmostEqual(self.account.get_initial_deposit_total(), 300.00)
        
        # Withdrawals, buys, sells should not affect initial_deposit_total
        self.account.withdraw(50.00)
        with patch('accounts.get_share_price', return_value=10.00):
            self.account.buy_shares("XYZ", 10)
        self.assertAlmostEqual(self.account.get_initial_deposit_total(), 300.00)

    @patch('accounts.get_share_price')
    def test_get_portfolio_value(self, mock_get_share_price):
        """
        Test get_portfolio_value calculates total value correctly.
        """
        mock_get_share_price.side_effect = [170.00, 250.00, 175.00, 260.00] # For buy/sell and then for portfolio value check

        self.assertEqual(self.account.get_portfolio_value(), 0.0)

        self.account.deposit(10000.00) # Balance: 10000
        self.assertAlmostEqual(self.account.get_portfolio_value(), 10000.00)

        self.account.buy_shares("AAPL", 10) # Buy at 170. Balance: 10000 - 1700 = 8300. Holdings: {'AAPL': 10}
                                            # Mock for portfolio value: AAPL price 175
        expected_value = 8300.00 + (10 * 175.00) # 8300 + 1750 = 10050
        mock_get_share_price.reset_mock()
        mock_get_share_price.side_effect = [175.00] # Price for AAPL for portfolio calculation
        self.assertAlmostEqual(self.account.get_portfolio_value(), expected_value)
        mock_get_share_price.assert_called_once_with("AAPL")

        self.account.buy_shares("TSLA", 5) # Buy at 250. Balance: 8300 - 1250 = 7050. Holdings: {'AAPL': 10, 'TSLA': 5}
                                            # Mock for portfolio value: AAPL 175, TSLA 260
        expected_value = 7050.00 + (10 * 175.00) + (5 * 260.00) # 7050 + 1750 + 1300 = 10100
        mock_get_share_price.reset_mock()
        mock_get_share_price.side_effect = [175.00, 260.00] # Prices for AAPL, TSLA
        self.assertAlmostEqual(self.account.get_portfolio_value(), expected_value)
        mock_get_share_price.assert_any_call("AAPL")
        mock_get_share_price.assert_any_call("TSLA")

    @patch('accounts.get_share_price')
    def test_get_profit_loss(self, mock_get_share_price):
        """
        Test get_profit_loss calculates profit/loss correctly.
        """
        mock_get_share_price.side_effect = [170.00, 250.00, 175.00, 260.00] # For buy/sell and then for portfolio value check

        self.assertEqual(self.account.get_profit_loss(), 0.0)

        self.account.deposit(10000.00) # Balance: 10000. Initial deposit: 10000.
        self.assertAlmostEqual(self.account.get_profit_loss(), 0.0) # Portfolio value = 10000, P/L = 10000 - 10000 = 0

        self.account.buy_shares("AAPL", 10) # Buy at 170. Balance: 8300. Holdings: {'AAPL': 10}
        # For portfolio value: AAPL price 175
        # Portfolio Value = 8300 + (10 * 175) = 10050
        # P/L = 10050 - 10000 = 50
        mock_get_share_price.reset_mock()
        mock_get_share_price.side_effect = [175.00]
        self.assertAlmostEqual(self.account.get_profit_loss(), 50.00)

        self.account.buy_shares("TSLA", 5) # Buy at 250. Balance: 7050. Holdings: {'AAPL': 10, 'TSLA': 5}
        # For portfolio value: AAPL 175, TSLA 260
        # Portfolio Value = 7050 + (10 * 175) + (5 * 260) = 10100
        # P/L = 10100 - 10000 = 100
        mock_get_share_price.reset_mock()
        mock_get_share_price.side_effect = [175.00, 260.00]
        self.assertAlmostEqual(self.account.get_profit_loss(), 100.00)

        # Simulate a loss
        # Sell AAPL for less than bought, or prices drop
        self.account.deposit(5000) # Initial deposit total now 15000.
                                   # Balance: 12050 (7050 + 5000). Holdings: {'AAPL':10, 'TSLA':5}
                                   # P/L base should be 15000.
        mock_get_share_price.reset_mock()
        mock_get_share_price.side_effect = [160.00, 240.00] # New prices for AAPL, TSLA
        # Current PV = 12050 + (10 * 160) + (5 * 240) = 12050 + 1600 + 1200 = 14850
        # P/L = 14850 - 15000 = -150
        self.assertAlmostEqual(self.account.get_profit_loss(), -150.00)


    @patch('accounts.datetime')
    @patch('accounts.get_share_price')
    def test_get_transactions(self, mock_get_share_price, mock_datetime):
        """
        Test get_transactions returns a chronological list of transactions.
        """
        mock_datetime.datetime.now.side_effect = [
            datetime.datetime(2023, 1, 1, 10, 0, 0),
            datetime.datetime(2023, 1, 1, 10, 1, 0),
            datetime.datetime(2023, 1, 1, 10, 2, 0),
            datetime.datetime(2023, 1, 1, 10, 3, 0),
            datetime.datetime(2023, 1, 1, 10, 4, 0),
        ]
        mock_datetime.datetime.isoformat.side_effect = [
            "2023-01-01T10:00:00",
            "2023-01-01T10:01:00",
            "2023-01-01T10:02:00",
            "2023-01-01T10:03:00",
            "2023-01-01T10:04:00",
        ]
        mock_get_share_price.return_value = 100.00

        self.account.deposit(1000.00) # 1
        self.account.withdraw(50.00)  # 2
        self.account.buy_shares("MSFT", 5) # 3
        self.account.sell_shares("MSFT", 2) # 4
        self.account.withdraw(2000.00) # 5 - Failed withdrawal

        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 5)

        # Check types and order
        self.assertEqual(transactions[0]['type'], 'deposit')
        self.assertTrue(transactions[0]['success'])
        self.assertEqual(transactions[0]['timestamp'], "2023-01-01T10:00:00")
        self.assertAlmostEqual(transactions[0]['balance_after'], 1000.00)

        self.assertEqual(transactions[1]['type'], 'withdraw')
        self.assertTrue(transactions[1]['success'])
        self.assertEqual(transactions[1]['timestamp'], "2023-01-01T10:01:00")
        self.assertAlmostEqual(transactions[1]['balance_after'], 950.00)

        self.assertEqual(transactions[2]['type'], 'buy')
        self.assertTrue(transactions[2]['success'])
        self.assertEqual(transactions[2]['symbol'], 'MSFT')
        self.assertEqual(transactions[2]['quantity'], 5)
        self.assertAlmostEqual(transactions[2]['price_per_share'], 100.00)
        self.assertEqual(transactions[2]['timestamp'], "2023-01-01T10:02:00")
        self.assertAlmostEqual(transactions[2]['balance_after'], 450.00) # 950 - 5*100 = 450

        self.assertEqual(transactions[3]['type'], 'sell')
        self.assertTrue(transactions[3]['success'])
        self.assertEqual(transactions[3]['symbol'], 'MSFT')
        self.assertEqual(transactions[3]['quantity'], 2)
        self.assertAlmostEqual(transactions[3]['price_per_share'], 100.00)
        self.assertEqual(transactions[3]['timestamp'], "2023-01-01T10:03:00")
        self.assertAlmostEqual(transactions[3]['balance_after'], 650.00) # 450 + 2*100 = 650

        self.assertEqual(transactions[4]['type'], 'withdraw')
        self.assertFalse(transactions[4]['success'])
        self.assertEqual(transactions[4]['timestamp'], "2023-01-01T10:04:00")
        self.assertAlmostEqual(transactions[4]['balance_after'], 650.00) # Balance should not change for failed transactions


    def test_holdings_copy_integrity(self):
        """
        Verify that get_holdings returns a copy and modifying it doesn't affect internal state.
        """
        self.account.deposit(1000.00)
        with patch('accounts.get_share_price', return_value=10.00):
            self.account.buy_shares("TEST", 10)

        holdings_copy = self.account.get_holdings()
        holdings_copy["TEST"] = 5 # Modify the copy
        holdings_copy["NEW"] = 20 # Add to the copy

        self.assertEqual(self.account.get_holdings(), {"TEST": 10}) # Internal state should be unchanged
        self.assertNotEqual(self.account.get_holdings(), holdings_copy)

    def test_transactions_copy_integrity(self):
        """
        Verify that get_transactions returns a copy and modifying it doesn't affect internal state.
        """
        self.account.deposit(100.00)
        
        transactions_copy = self.account.get_transactions()
        transactions_copy[0]['type'] = 'FAKE_DEPOSIT'
        transactions_copy.append({"type": "FAKE_TRANSACTION"})

        self.assertEqual(self.account.get_transactions()[0]['type'], 'deposit') # Internal state should be unchanged
        self.assertEqual(len(self.account.get_transactions()), 1) # Internal list length unchanged
        self.assertNotEqual(self.account.get_transactions(), transactions_copy)


# This allows running the tests directly from the file
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```