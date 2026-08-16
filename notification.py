"""Notification service abstraction.

Business logic depends on this interface, not on Telegram/Email/In-App directly.
A notification failure must NOT roll back the underlying application state.

Implementations:
  - InMemoryNotification: stores notifications for in-app display
  - TelegramNotification: sends via Telegram (requires bot token + chat_id)
"""
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

DATA = Path(__file__).resolve().parent / 'data'
NOTIFICATIONS_FILE = DATA / 'notifications.json'


class NotificationService:
    """Base notification interface."""

    def send(self, recipient: str, event: str, message: str, meta: dict = None):
        raise NotImplementedError

    def get_inbox(self, recipient: str, limit: int = 50) -> list:
        raise NotImplementedError


class InMemoryNotification(NotificationService):
    """Stores notifications in a local JSON file. Default for the MVP."""

    def _load(self):
        if not NOTIFICATIONS_FILE.exists():
            return []
        try:
            return json.loads(NOTIFICATIONS_FILE.read_text(encoding='utf-8'))
        except Exception:
            return []

    def _save(self, data):
        NOTIFICATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        NOTIFICATIONS_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def send(self, recipient: str, event: str, message: str, meta: dict = None):
        notifications = self._load()
        notifications.append({
            'recipient': recipient,
            'event': event,
            'message': message,
            'meta': meta or {},
            'created_at': datetime.now(timezone.utc).isoformat(),
            'read': False,
        })
        self._save(notifications)

    def get_inbox(self, recipient: str, limit: int = 50) -> list:
        notifications = self._load()
        inbox = [n for n in notifications if n.get('recipient') == recipient]
        return inbox[-limit:]

    def mark_read(self, recipient: str):
        notifications = self._load()
        for n in notifications:
            if n.get('recipient') == recipient:
                n['read'] = True
        self._save(notifications)


class TelegramNotification(NotificationService):
    """Telegram notification (requires configuration)."""

    def __init__(self, bot_token: str = '', chat_id: str = ''):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send(self, recipient: str, event: str, message: str, meta: dict = None):
        if not self.bot_token or not self.chat_id:
            return
        try:
            import urllib.request
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = json.dumps({"chat_id": self.chat_id, "text": message}).encode()
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req, timeout=10)
        except Exception:
            pass  # Notification failure must not crash the app

    def get_inbox(self, recipient: str, limit: int = 50) -> list:
        return []


def get_notification_service() -> NotificationService:
    """Return the configured notification service."""
    # Check for Telegram config
    import os
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    if bot_token and chat_id:
        return TelegramNotification(bot_token, chat_id)
    return InMemoryNotification()
