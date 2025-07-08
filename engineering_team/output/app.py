import gradio as gr
from accounts import Account, get_share_price

# Initialize the single account for this demo
trading_account = Account("demo_user")

# --- Helper functions to interact with the account and format output ---

def refresh_status():
    """Fetches and formats the current status of the trading account."""
    balance = trading_account.get_balance()
    holdings = trading_account.get_holdings()
    portfolio_value = trading_account.get_portfolio_value()
    profit_loss = trading_account.get_profit_loss()
    initial_deposit = trading_account.get_initial_deposit_total()

    holdings_str = "No holdings."
    if holdings:
        holdings_list = []
        for symbol, qty in holdings.items():
            price = get_share_price(symbol)
            holdings_list.append(f"{qty}x {symbol} (Current Price: ${price:.2f}, Value: ${qty * price:.2f})")
        holdings_str = "\n".join(holdings_list)

    return (
        f"${balance:.2f}",
        holdings_str,
        f"${portfolio_value:.2f}",
        f"${profit_loss:.2f}",
        f"Total Initial Deposits: ${initial_deposit:.2f}"
    )

def deposit_funds(amount: float):
    """Deposits funds into the account and returns a message and updated status."""
    success = trading_account.deposit(amount)
    last_transaction = trading_account.get_transactions()[-1] if trading_account.get_transactions() else None
    message = last_transaction['message'] if last_transaction else ("Deposit successful." if success else "Deposit failed.")
    return message, *refresh_status()

def withdraw_funds(amount: float):
    """Withdraws funds from the account and returns a message and updated status."""
    success = trading_account.withdraw(amount)
    last_transaction = trading_account.get_transactions()[-1] if trading_account.get_transactions() else None
    message = last_transaction['message'] if last_transaction else ("Withdrawal successful." if success else "Withdrawal failed.")
    return message, *refresh_status()

def buy_shares_action(symbol: str, quantity: int):
    """Buys shares for the account and returns a message and updated status."""
    success = trading_account.buy_shares(symbol, quantity)
    last_transaction = trading_account.get_transactions()[-1] if trading_account.get_transactions() else None
    message = last_transaction['message'] if last_transaction else ("Buy successful." if success else "Buy failed.")
    return message, *refresh_status()

def sell_shares_action(symbol: str, quantity: int):
    """Sells shares from the account and returns a message and updated status."""
    success = trading_account.sell_shares(symbol, quantity)
    last_transaction = trading_account.get_transactions()[-1] if trading_account.get_transactions() else None
    message = last_transaction['message'] if last_transaction else ("Sell successful." if success else "Sell failed.")
    return message, *refresh_status()

def get_transactions_display():
    """Formats the transaction history for display in a Gradio Dataframe."""
    transactions = trading_account.get_transactions()
    if not transactions:
        return [] # Empty list for gr.Dataframe
    
    data = []
    for t in transactions:
        data.append([
            t['timestamp'],
            t['type'],
            t['symbol'] if t['symbol'] else '',
            t['quantity'] if t['quantity'] is not None else '',
            f"{t['price_per_share']:.2f}" if t['price_per_share'] is not None else '',
            f"{t['amount_effect_on_cash']:.2f}",
            f"{t['balance_after']:.2f}",
            "Yes" if t['success'] else "No",
            t['message']
        ])
    return data

# --- Gradio UI Definition ---

with gr.Blocks(title="Trading Account Simulator") as demo:
    gr.Markdown("# Simple Trading Account Simulator")
    gr.Markdown("A demo of basic account management and stock trading functionalities.")
    gr.Markdown("---")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Account Status")
            current_balance_output = gr.Textbox(label="Current Cash Balance", interactive=False)
            holdings_output = gr.Textbox(label="Current Holdings", interactive=False, lines=5)
            portfolio_value_output = gr.Textbox(label="Total Portfolio Value", interactive=False)
            profit_loss_output = gr.Textbox(label="Profit/Loss (vs. Initial Deposit)", interactive=False)
            initial_deposit_total_output = gr.Textbox(label="Initial Deposits", interactive=False)
            
            refresh_btn = gr.Button("Refresh Account Status")
            
        with gr.Column(scale=2):
            gr.Markdown("## Actions")
            action_message_output = gr.Textbox(label="Action Result", interactive=False, placeholder="Messages from actions will appear here.")

            with gr.Tab("Deposit Funds"):
                deposit_amount = gr.Number(label="Amount to Deposit", value=1000.00, minimum=0.01)
                deposit_btn = gr.Button("Deposit Funds")
            
            with gr.Tab("Withdraw Funds"):
                withdraw_amount = gr.Number(label="Amount to Withdraw", value=100.00, minimum=0.01)
                withdraw_btn = gr.Button("Withdraw Funds")

            with gr.Tab("Buy Shares"):
                buy_symbol = gr.Textbox(label="Stock Symbol (e.g., AAPL, TSLA, GOOGL)", value="AAPL")
                buy_quantity = gr.Number(label="Quantity", value=10, step=1, minimum=1)
                buy_btn = gr.Button("Buy Shares")
            
            with gr.Tab("Sell Shares"):
                sell_symbol = gr.Textbox(label="Stock Symbol (e.g., AAPL, TSLA, GOOGL)", value="AAPL")
                sell_quantity = gr.Number(label="Quantity", value=5, step=1, minimum=1)
                sell_btn = gr.Button("Sell Shares")
    
    gr.Markdown("---")
    gr.Markdown("## Transaction History")
    transactions_columns = [
        "Timestamp", "Type", "Symbol", "Quantity", "Price/Share",
        "Cash Effect", "Balance After", "Success", "Message"
    ]
    transactions_table = gr.Dataframe(
        headers=transactions_columns,
        col_count=(len(transactions_columns), "fixed"),
        type="array", # Use "array" when passing a list of lists
        label="Full Transaction History",
        interactive=False,
        row_count=(5, "dynamic"),
        wrap=True # Allows text wrapping in cells
    )
    show_transactions_btn = gr.Button("Show/Refresh Transactions History")


    # --- Event Listeners ---

    # Outputs that are updated by status refresh
    status_outputs = [
        current_balance_output,
        holdings_output,
        portfolio_value_output,
        profit_loss_output,
        initial_deposit_total_output
    ]

    # Initial load of the UI
    demo.load(
        refresh_status,
        inputs=None,
        outputs=status_outputs
    ).then( # Chain to also load transactions on startup
        get_transactions_display,
        inputs=None,
        outputs=[transactions_table]
    )

    # Refresh Status button
    refresh_btn.click(
        refresh_status,
        inputs=None,
        outputs=status_outputs
    )

    # Deposit button
    deposit_btn.click(
        deposit_funds,
        inputs=[deposit_amount],
        outputs=[action_message_output] + status_outputs
    ).then( # Update transactions after deposit
        get_transactions_display,
        inputs=None,
        outputs=[transactions_table]
    )

    # Withdraw button
    withdraw_btn.click(
        withdraw_funds,
        inputs=[withdraw_amount],
        outputs=[action_message_output] + status_outputs
    ).then( # Update transactions after withdrawal
        get_transactions_display,
        inputs=None,
        outputs=[transactions_table]
    )

    # Buy Shares button
    buy_btn.click(
        buy_shares_action,
        inputs=[buy_symbol, buy_quantity],
        outputs=[action_message_output] + status_outputs
    ).then( # Update transactions after buy
        get_transactions_display,
        inputs=None,
        outputs=[transactions_table]
    )

    # Sell Shares button
    sell_btn.click(
        sell_shares_action,
        inputs=[sell_symbol, sell_quantity],
        outputs=[action_message_output] + status_outputs
    ).then( # Update transactions after sell
        get_transactions_display,
        inputs=None,
        outputs=[transactions_table]
    )

    # Show Transactions button
    show_transactions_btn.click(
        get_transactions_display,
        inputs=None,
        outputs=[transactions_table]
    )

# Launch the Gradio application
demo.launch(share=True)