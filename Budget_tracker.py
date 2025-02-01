import pandas as pd
import matplotlib.pyplot as plt
from plyer import notification  # For desktop notifications
import datetime
import streamlit as st

class BudgetTracker:
    def __init__(self):
        self.balance = 0.0
        self.transactions = []
        self.balance_threshold = 100.0  # Notify if balance goes below this amount
        self.large_expense_threshold = 500.0  # Notify for expenses above this amount
        self.recurring_transactions = []  # Store recurring transactions

    def add_transaction(self, amount, category, transaction_type):
        if transaction_type.lower() == "income":
            self.balance += amount
        elif transaction_type.lower() == "expense":
            self.balance -= amount
            # Notify for large expenses
            if amount > self.large_expense_threshold:
                self.notify_user(
                    title="Large Expense Alert",
                    message=f"A large expense of ${amount:.2f} was recorded in the '{category}' category."
                )
        else:
            st.error("Invalid transaction type. Use 'income' or 'expense'.")
            return

        transaction = {
            "amount": amount,
            "category": category,
            "type": transaction_type
        }
        self.transactions.append(transaction)
        st.success(f"Transaction added: {transaction_type} of ${amount:.2f} in '{category}' category.")

        # Notify if balance is below the threshold
        if self.balance < self.balance_threshold:
            self.notify_user(
                title="Low Balance Alert",
                message=f"Your balance is below the threshold (${self.balance_threshold:.2f}). Current balance: ${self.balance:.2f}."
            )

    def add_recurring_transaction(self, amount, category, transaction_type, frequency):
        """Add a recurring transaction."""
        recurring_transaction = {
            "amount": amount,
            "category": category,
            "type": transaction_type,
            "frequency": frequency,
            "last_added": datetime.datetime.now()
        }
        self.recurring_transactions.append(recurring_transaction)
        st.success(f"Recurring transaction added: {transaction_type} of ${amount:.2f} in '{category}' category, {frequency}.")

    def process_recurring_transactions(self):
        """Process recurring transactions based on frequency."""
        for transaction in self.recurring_transactions:
            last_added = transaction["last_added"]
            now = datetime.datetime.now()

            # Check if it's time for the next recurrence
            if transaction["frequency"] == "daily" and (now - last_added).days >= 1:
                self.add_transaction(transaction["amount"], transaction["category"], transaction["type"])
                transaction["last_added"] = now
            elif transaction["frequency"] == "weekly" and (now - last_added).days >= 7:
                self.add_transaction(transaction["amount"], transaction["category"], transaction["type"])
                transaction["last_added"] = now
            elif transaction["frequency"] == "monthly" and now.month != last_added.month:
                self.add_transaction(transaction["amount"], transaction["category"], transaction["type"])
                transaction["last_added"] = now

    def view_balance(self):
        return f"Current Balance: ${self.balance:.2f}"

    def view_transactions(self):
        if not self.transactions:
            return "No transactions recorded."
        else:
            transaction_list = []
            for idx, transaction in enumerate(self.transactions, 1):
                transaction_list.append(f"{idx}. {transaction['type'].capitalize()}: ${transaction['amount']:.2f} ({transaction['category']})")
            return "\n".join(transaction_list)

    def visualize_data(self):
        if not self.transactions:
            st.warning("No transactions to visualize.")
            return

        # Create a DataFrame from transactions
        df = pd.DataFrame(self.transactions)

        # Convert amounts to positive for expenses (for visualization purposes)
        df['amount'] = df.apply(lambda row: -row['amount'] if row['type'] == 'expense' else row['amount'], axis=1)

        # Plot income vs expenses
        st.subheader("Income vs Expenses")
        fig, ax = plt.subplots()
        df.groupby('type')['amount'].sum().plot(kind='bar', color=['green', 'red'], ax=ax)
        ax.set_title("Income vs Expenses")
        ax.set_xlabel("Transaction Type")
        ax.set_ylabel("Amount ($)")
        st.pyplot(fig)

        # Plot transactions over time (assuming transactions are in order)
        df['cumulative_balance'] = df['amount'].cumsum()
        st.subheader("Cumulative Balance Over Time")
        fig2, ax2 = plt.subplots()
        ax2.plot(df['cumulative_balance'], marker='o')
        ax2.set_title("Cumulative Balance Over Time")
        ax2.set_xlabel("Transaction Number")
        ax2.set_ylabel("Balance ($)")
        ax2.grid(True)
        st.pyplot(fig2)

    def notify_user(self, title, message):
        """Send a desktop notification to the user."""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Budget Tracker",
                timeout=10  # Notification stays for 10 seconds
            )
        except Exception as e:
            print(f"Error sending notification: {e}")
            print(f"Notification: {title} - {message}")

# Streamlit app interface
st.title("Budget Tracker")

# Ensure that the tracker object is persistent across app reruns
if 'tracker' not in st.session_state:
    st.session_state.tracker = BudgetTracker()

tracker = st.session_state.tracker

menu = ["Add Income", "Add Expense", "View Balance", "View Transactions", "Visualize Data", "Add Recurring Transaction", "Process Recurring Transactions"]
choice = st.sidebar.selectbox("Choose an option", menu)

if choice == "Add Income":
    amount = st.number_input("Enter income amount", min_value=0.0, step=1.0)
    category = st.text_input("Enter category (e.g., Salary, Bonus)")
    if st.button("Add Income"):
        tracker.add_transaction(amount, category, "income")

elif choice == "Add Expense":
    amount = st.number_input("Enter expense amount", min_value=0.0, step=1.0)
    category = st.text_input("Enter category (e.g., Food, Rent)")
    if st.button("Add Expense"):
        tracker.add_transaction(amount, category, "expense")

elif choice == "View Balance":
    st.write(tracker.view_balance())

elif choice == "View Transactions":
    st.write(tracker.view_transactions())

elif choice == "Visualize Data":
    tracker.visualize_data()

elif choice == "Add Recurring Transaction":
    amount = st.number_input("Enter recurring amount", min_value=0.0, step=1.0)
    category = st.text_input("Enter category (e.g., Rent, Subscription)")
    transaction_type = st.selectbox("Enter transaction type", ["income", "expense"])
    frequency = st.selectbox("Enter frequency", ["daily", "weekly", "monthly"])
    if st.button("Add Recurring Transaction"):
        tracker.add_recurring_transaction(amount, category, transaction_type, frequency)

elif choice == "Process Recurring Transactions":
    tracker.process_recurring_transactions()