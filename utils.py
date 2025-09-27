import json
import requests
from typing import Dict, Any, List


def load_permissions() -> Dict[str, Any]:
    """Load permissions from permissions.json or create defaults."""
    try:
        with open("permissions.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Create default permissions schema
        default_permissions = {
            # New key name
            "authorized_users": [123456789, 1142810150],
            # Admins list
            "admins": [123456789, 1142810150],
            # Enabled groups for broadcasts/alerts
            "groups": {},
            # Pending access requests mapped by user_id (string) -> user_info
            "pending_requests": {},
            # Rejected users list (ints)
            "rejected_users": []
        }
        with open("permissions.json", "w", encoding="utf-8") as f:
            json.dump(default_permissions, f, ensure_ascii=False, indent=2)
        return default_permissions


def save_permissions(permissions: Dict[str, Any]) -> None:
    """Persist the permissions structure to disk."""
    with open("permissions.json", "w", encoding="utf-8") as f:
        json.dump(permissions, f, ensure_ascii=False, indent=2)


def add_user_request(user_id: int, user_info: Dict[str, Any]) -> None:
    """Add a new access request for review by admins."""
    permissions = load_permissions()
    if "pending_requests" not in permissions:
        permissions["pending_requests"] = {}
    permissions["pending_requests"][str(user_id)] = user_info
    save_permissions(permissions)


def approve_user(user_id: int) -> bool:
    """Approve a user. Works whether or not they were pending."""
    permissions = load_permissions()
    user_id_str = str(user_id)

    # Backward compatibility: migrate old key if present
    if "authorized_users" not in permissions:
        permissions["authorized_users"] = permissions.get("1142810150", [])

    # Add to authorized list if not already
    if user_id not in permissions["authorized_users"]:
        permissions["authorized_users"].append(user_id)

    # Remove from pending if exists
    if user_id_str in permissions.get("pending_requests", {}):
        del permissions["pending_requests"][user_id_str]

    save_permissions(permissions)
    return True


def reject_user(user_id: int) -> bool:
    """Reject a pending user request."""
    permissions = load_permissions()
    user_id_str = str(user_id)

    if user_id_str in permissions.get("pending_requests", {}):
        if user_id not in permissions.get("rejected_users", []):
            permissions.setdefault("rejected_users", []).append(user_id)
        del permissions["pending_requests"][user_id_str]
        save_permissions(permissions)
        return True
    return False


def get_pending_requests() -> Dict[str, Any]:
    """Return map of user_id(str) -> user_info for pending requests."""
    permissions = load_permissions()
    return permissions.get("pending_requests", {})


def get_all_users() -> List[int]:
    """Return list of authorized user IDs (ints)."""
    permissions = load_permissions()
    # Support both the new key and legacy key
    return permissions.get("authorized_users", permissions.get("1142810150", []))


def remove_user_approval(user_id: int) -> bool:
    """Remove a user's approval (if not an admin)."""
    permissions = load_permissions()
    user_list = permissions.get("authorized_users", permissions.get("1142810150", []))

    if user_id in user_list:
        user_list.remove(user_id)
        permissions["authorized_users"] = user_list
        save_permissions(permissions)
        return True
    return False


def search_user_by_id(search_id: int) -> bool:
    """Check if a user ID is in the authorized list."""
    permissions = load_permissions()
    users = permissions.get("authorized_users", permissions.get("1142810150", []))
    return search_id in users


def is_authorized(user_id: int) -> bool:
    perms = load_permissions()
    authorized = perms.get("authorized_users", perms.get("1142810150", []))
    return user_id in authorized


def is_admin(user_id: int) -> bool:
    perms = load_permissions()
    return user_id in perms.get("admins", [])


def send_to_telegram(chat_id: int, message: str, bot_token: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        # fail silently for background notifications
        pass


def send_alert_to_enabled_groups(message: str, bot_token: str) -> None:
    perms = load_permissions()
    for chat_id, info in perms.get("groups", {}).items():
        if info.get("enabled"):
            send_to_telegram(int(chat_id), message, bot_token)
