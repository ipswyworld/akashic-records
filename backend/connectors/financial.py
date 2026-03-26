from connectors import BaseConnector
from models import UserLifeEntity, UserActivity

class PlaidConnector(BaseConnector):
    """Syncs bank account balances and transaction history."""
    def sync(self, db_session) -> int:
        print(f"Syncing Plaid for {self.user_id}...")
        return 1

class CryptoConnector(BaseConnector):
    """Syncs wallet balances and transaction history."""
    def sync(self, db_session) -> int:
        print(f"Syncing Crypto Wallets for {self.user_id}...")
        return 1

class SubscriptionConnector(BaseConnector):
    """Syncs active digital subscriptions and billing cycles."""
    def sync(self, db_session) -> int:
        print(f"Syncing Subscriptions for {self.user_id}...")
        return 1
