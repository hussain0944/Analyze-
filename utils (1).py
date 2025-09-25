import json
import requests

def load_permissions():
    try:
        with open("permissions.json") as f:
            return json.load(f)
    except FileNotFoundError:
        # إنشاء ملف الصلاحيات الافتراضي
        default_permissions = {
            "authorized_users": [123456789, 1142810150],  # المستخدمين المعتمدين
            "admins": [123456789, 1142810150],      # المشرفين
            "groups": {},
            "pending_requests": {},  # طلبات الانتظار
            "rejected_users": []     # المستخدمين المرفوضين
        }
        with open("permissions.json", "w") as f:
            json.dump(default_permissions, f)
        return default_permissions

def save_permissions(permissions):
    """حفظ الصلاحيات في الملف"""
    with open("permissions.json", "w") as f:
        json.dump(permissions, f, indent=2)

def add_user_request(user_id, user_info):
    """إضافة طلب مستخدم جديد"""
    permissions = load_permissions()
    if "pending_requests" not in permissions:
        permissions["pending_requests"] = {}
    permissions["pending_requests"][str(user_id)] = user_info
    save_permissions(permissions)

def approve_user(user_id):
    """الموافقة على مستخدم"""
    permissions = load_permissions()
    user_id_str = str(user_id)
    
    # التأكد من وجود المفتاح الصحيح
    if "authorized_users" not in permissions:
        permissions["authorized_users"] = permissions.get("1142810150", [])
    
    # إضافة المستخدم للمعتمدين (سواء كان في pending أم لا)
    if user_id not in permissions["authorized_users"]:
        permissions["authorized_users"].append(user_id)
    
    # حذف من قائمة الانتظار إن وجد
    if user_id_str in permissions.get("pending_requests", {}):
        del permissions["pending_requests"][user_id_str]
    
    save_permissions(permissions)
    return True

def reject_user(user_id):
    """رفض مستخدم"""
    permissions = load_permissions()
    user_id_str = str(user_id)
    
    if user_id_str in permissions["pending_requests"]:
        # إضافة للمرفوضين
        if user_id not in permissions["rejected_users"]:
            permissions["rejected_users"].append(user_id)
        # حذف من قائمة الانتظار
        del permissions["pending_requests"][user_id_str]
        save_permissions(permissions)
        return True
    return False

def get_pending_requests():
    """الحصول على طلبات الانتظار"""
    permissions = load_permissions()
    return permissions.get("pending_requests", {})

def get_all_users():
    """الحصول على جميع المستخدمين المعتمدين"""
    permissions = load_permissions()
    # دعم المفتاح القديم والجديد
    return permissions.get("authorized_users", permissions.get("1142810150", []))

def remove_user_approval(user_id):
    """إلغاء موافقة مستخدم"""
    permissions = load_permissions()
    # دعم المفتاح القديم والجديد
    user_list = permissions.get("authorized_users", permissions.get("1142810150", []))
    
    if user_id in user_list:
        user_list.remove(user_id)
        permissions["authorized_users"] = user_list
        save_permissions(permissions)
        return True
    return False

def search_user_by_id(search_id):
    """البحث عن مستخدم بالمعرف"""
    permissions = load_permissions()
    users = permissions.get("authorized_users", permissions.get("1142810150", []))
    return search_id in users

def is_authorized(user_id):
    perms = load_permissions()
    authorized = perms.get("authorized_users", perms.get("1142810150", []))
    return user_id in authorized

def is_admin(user_id):
    perms = load_permissions()
    return user_id in perms["admins"]

def send_to_telegram(chat_id, message, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def send_alert_to_enabled_groups(message, bot_token):
    perms = load_permissions()
    for chat_id, info in perms.get("groups", {}).items():
        if info.get("enabled"):
            send_to_telegram(chat_id, message, bot_token)