# app.py
import os
import json
import time
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = "shopease_verify_token"  # Match with your webhook setup
VERSION = os.getenv("VERSION", "v23.0")

app = Flask(__name__)

DATA_FILE = "user_data.json"
SESSION_TIMEOUT_SECONDS = 5 * 60  # 5 minutes


N8N_WEBHOOK_URL = "https://n8n.my8n.xyz/webhook-test/whatsapp-order"

def export_to_n8n(phone, cart, stage="Completed"):
    total = sum(PRODUCTS[pid]["price"] * qty for pid, qty in cart.items())
    for pid, qty in cart.items():
        product = PRODUCTS.get(pid, {})
        payload = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "phone": phone,
            "product_name": product.get("name", "Unknown"),
            "quantity": qty,
            "price": product.get("price", 0),
            "total_item": product.get("price", 0) * qty,
            "grand_total": total,
            "stage": stage,
        }
        try:
            r = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
            if r.status_code == 200:
                print(f"Sent order for {phone} → {product['name']} to n8n.")
            else:
                print(f"n8n responded with {r.status_code}: {r.text}")
        except Exception as e:
            print(f"Failed to send order data to n8n: {e}")


# -------------------- Persistent user data --------------------
def load_user_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            print("⚠️ user_data.json corrupted or empty, resetting.")
            return {}
    return {}

def save_user_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

user_sessions = load_user_data()

# -------------------- Product Catalog --------------------
PRODUCTS = {
    "1": {"name": "Wireless Mouse", "price": 650},
    "2": {"name": "Bluetooth Headphones", "price": 799},
    "3": {"name": "USB-C Charger", "price": 1499},
    "4": {"name": "Laptop Stand", "price": 699},
}

# -------------------- WhatsApp send helper --------------------
def send_whatsapp_message(phone_number, message):
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message},
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to send message: {e}")
        if "resp" in locals():
            print("Response:", resp.text)

# -------------------- Menu / text blocks --------------------
def main_menu_text():
    return (
        "*🛍️ Welcome to ShopEase!* 👋\n\n"
        "Choose an option:\n\n"
        "1️⃣ *Browse Our Collection*\n"
        "2️⃣ *View Cart*\n"
        "3️⃣ *Edit Cart*\n"
        "4️⃣ *Proceed to Checkout*\n"
        "5️⃣ *Customer Support*\n"
        "6️⃣ *Help / Main Menu*\n\n"
        "Reply with the number or option name.\n(Type *menu* anytime to return here.)"
    )

def show_products_text():
    msg = "*🛒 Available Products:*\n\n"
    for pid, p in PRODUCTS.items():
        msg += f"{pid}. {p['name']} — ₹{p['price']}\n"
    msg += "\nReply with the *product number* to add it to your cart, or type *menu* to go back."
    return msg

def cart_summary_text(cart):
    if not cart:
        return "🛒 Your cart is empty.\n\nType *1* to browse products or *menu* to see options."
    msg = "*🧺 Your Cart:*\n"
    total = 0
    count = 0
    for pid, qty in cart.items():
        p = PRODUCTS.get(pid, {"name": "Unknown", "price": 0})
        msg += f"- {p['name']} × {qty} = ₹{p['price'] * qty}\n"
        total += p["price"] * qty
        count += qty
    msg += f"\n*Items:* {count}\n*Total:* ₹{total}\n\nReply *checkout* to pay, *edit* to modify, or *menu* to return."
    return msg

# -------------------- Webhook verification --------------------
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403
    return "No content", 404

# -------------------- Incoming messages --------------------
@app.route("/webhook", methods=["POST"])
def incoming_messages():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"status": "no data"}), 400

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", []) or []
            for msg in messages:
                phone = msg.get("from")
                text_raw = msg.get("text", {}).get("body", "") or ""
                text = text_raw.strip().lower()

                user = user_sessions.get(
                    phone,
                    {"cart": {}, "stage": "menu", "selected_product": None, "last_seen": 0},
                )
                now = int(time.time())
                last_seen = user.get("last_seen", 0)
                if last_seen and (now - last_seen) > SESSION_TIMEOUT_SECONDS:
                    user["stage"] = "menu"
                    send_whatsapp_message(
                        phone, "👋 Welcome back to *ShopEase!* (Session restarted after inactivity)"
                    )
                    send_whatsapp_message(phone, main_menu_text())
                    user["last_seen"] = now
                    user_sessions[phone] = user
                    save_user_data(user_sessions)
                    continue

                user["last_seen"] = now
                user_sessions[phone] = user
                cart = user.setdefault("cart", {})

                # --- Greetings ---
                if text in ["hi", "hello", "hey", "start"]:
                    send_whatsapp_message(phone, "👋 Hi there! Here's what I can do for you:")
                    send_whatsapp_message(phone, main_menu_text())
                    user["stage"] = "menu"
                    save_user_data(user_sessions)
                    continue

                # --- NEW: Browse products from main menu ---
                if text in ["1", "browse", "browse products", "browse our collection"]:
                    send_whatsapp_message(phone, show_products_text())
                    user["stage"] = "browsing"
                    save_user_data(user_sessions)
                    continue

                # Awaiting quantity
                if user.get("stage") == "awaiting_quantity":
                    if text.isdigit() and int(text) > 0:
                        qty = int(text)
                        pid = user.get("selected_product")
                        if pid and pid in PRODUCTS:
                            cart[pid] = cart.get(pid, 0) + qty
                            save_user_data(user_sessions)
                            send_whatsapp_message(
                                phone,
                                f"✅ You have added *{qty} × {PRODUCTS[pid]['name']}* to your cart.",
                            )
                            send_whatsapp_message(
                                phone,
                                "Would you like to *continue shopping* or go to the *menu*?",
                            )
                            user["stage"] = "post_add_choice"
                        else:
                            send_whatsapp_message(
                                phone, "❌ That product doesn't exist. Please reply with a valid product number."
                            )
                    else:
                        send_whatsapp_message(phone, "❌ Please enter a valid quantity (a positive number).")
                    save_user_data(user_sessions)
                    continue

                if user.get("stage") == "post_add_choice":
                    if text in ["continue", "continue shopping", "1", "browse"]:
                        send_whatsapp_message(phone, show_products_text())
                        user["stage"] = "browsing"
                    elif text in ["menu", "6", "help", "main menu"]:
                        send_whatsapp_message(phone, main_menu_text())
                        user["stage"] = "menu"
                    else:
                        send_whatsapp_message(
                            phone, "Reply *continue* to keep shopping or *menu* to return to main menu."
                        )
                    save_user_data(user_sessions)
                    continue

                if user.get("stage") == "browsing":
                    if text in PRODUCTS:
                        user["selected_product"] = text
                        user["stage"] = "awaiting_quantity"
                        send_whatsapp_message(
                            phone,
                            f"How many *{PRODUCTS[text]['name']}* would you like to add? (enter a number)",
                        )
                    elif text in ["menu", "6", "help"]:
                        send_whatsapp_message(phone, main_menu_text())
                        user["stage"] = "menu"
                    else:
                        send_whatsapp_message(
                            phone, "Reply with a *product number* to add it, or *menu* to return."
                        )
                    save_user_data(user_sessions)
                    continue

                # View cart
                if text in ["2", "view cart", "cart"]:
                    send_whatsapp_message(phone, cart_summary_text(cart))
                    user["stage"] = "cart_view"
                    save_user_data(user_sessions)
                    continue

                # --- FIXED cart_view section ---
                if user.get("stage") == "cart_view":
                    if text in ["checkout", "4", "proceed to checkout"]:
                        if not cart:
                            send_whatsapp_message(
                                phone, "🛒 Your cart is empty. Browse products to add items first."
                            )
                            send_whatsapp_message(phone, show_products_text())
                            user["stage"] = "browsing"
                        else:
                            total = sum(PRODUCTS[pid]["price"] * qty for pid, qty in cart.items())
                            send_whatsapp_message(
                                phone,
                                f"💳 Your total is ₹{total}.\nReply *confirm* to complete purchase, or *cancel* to go back.",
                            )
                            user["stage"] = "awaiting_checkout_confirm"

                    elif text in ["1", "browse", "browse products"]:
                        send_whatsapp_message(phone, show_products_text())
                        user["stage"] = "browsing"

                    elif text in ["edit", "3", "modify cart", "edit cart"]:
                        if not cart:
                            send_whatsapp_message(
                                phone, "🛒 Your cart is empty — nothing to modify.\nType *1* to browse products."
                            )
                            user["stage"] = "menu"
                        else:
                            msg = "*✏️ Modify Cart:*\n"
                            for pid, qty in cart.items():
                                p = PRODUCTS.get(pid, {"name": "Unknown", "price": 0})
                                msg += f"{pid}. {p['name']} × {qty}\n"
                            msg += "\nReply with the *product number* to update its quantity (0 to delete), or *menu* to return."
                            send_whatsapp_message(phone, msg)
                            user["stage"] = "modifying"

                    elif text in ["menu", "6", "help"]:
                        send_whatsapp_message(phone, main_menu_text())
                        user["stage"] = "menu"

                    else:
                        send_whatsapp_message(
                            phone,
                            "Please reply with *1* to browse, *edit* to modify, *checkout* to pay, or *menu* to return.",
                        )

                    save_user_data(user_sessions)
                    continue

                # Checkout confirmation
                if user.get("stage") == "awaiting_checkout_confirm":
                    if text in ["confirm", "yes", "y"]:
                        total = sum(PRODUCTS[pid]["price"] * qty for pid, qty in cart.items())
                        export_to_n8n(phone, cart, stage="Completed")
                        send_whatsapp_message(
                            phone,
                            f"✅ Checkout complete! Your card was charged ₹{total}.\nThank you for shopping with ShopEase! 🛍️",
                        )
                        user["cart"] = {}
                        user["stage"] = "post_checkout_choice"
                        send_whatsapp_message(phone, "Would you like to *continue shopping* or *exit*?")
                    elif text in ["cancel", "no", "n", "menu"]:
                        send_whatsapp_message(phone, "Checkout canceled. Returning to main menu.")
                        send_whatsapp_message(phone, main_menu_text())
                        user["stage"] = "menu"
                    else:
                        send_whatsapp_message(
                            phone, "Reply *confirm* to complete purchase or *cancel* to return."
                        )
                    save_user_data(user_sessions)
                    continue

                if user.get("stage") == "post_checkout_choice":
                    if text in ["continue", "continue shopping", "1", "browse"]:
                        send_whatsapp_message(phone, show_products_text())
                        user["stage"] = "browsing"
                    elif text in ["exit", "quit", "no"]:
                        send_whatsapp_message(
                            phone,
                            "Thanks for visiting ShopEase! If you need anything else, type *hi* or *menu* anytime.",
                        )
                        user["stage"] = "menu"
                    else:
                        send_whatsapp_message(
                            phone, "Please reply *continue* to shop more or *exit* to finish."
                        )
                    save_user_data(user_sessions)
                    continue

                # Edit / modify cart
                if text in ["3", "modify cart", "edit", "edit cart"]:
                    if not cart:
                        send_whatsapp_message(
                            phone, "🛒 Your cart is empty — nothing to modify.\nType *1* to browse products."
                        )
                        user["stage"] = "menu"
                    else:
                        msg = "*✏️ Modify Cart:*\n"
                        for pid, qty in cart.items():
                            p = PRODUCTS.get(pid, {"name": "Unknown", "price": 0})
                            msg += f"{pid}. {p['name']} × {qty}\n"
                        msg += "\nReply with the *product number* to update its quantity (0 to delete), or *menu* to return."
                        send_whatsapp_message(phone, msg)
                        user["stage"] = "modifying"
                    save_user_data(user_sessions)
                    continue

                if user.get("stage") == "modifying":
                    if text in cart:
                        user["selected_product"] = text
                        user["stage"] = "awaiting_update"
                        send_whatsapp_message(
                            phone, f"Enter the new quantity for *{PRODUCTS[text]['name']}* (0 to remove):"
                        )
                    elif text in ["menu", "6", "help"]:
                        send_whatsapp_message(phone, main_menu_text())
                        user["stage"] = "menu"
                    else:
                        send_whatsapp_message(
                            phone, "Reply with the product number in your cart, or *menu* to return."
                        )
                    save_user_data(user_sessions)
                    continue

                if user.get("stage") == "awaiting_update":
                    if text.isdigit() and int(text) >= 0:
                        qty = int(text)
                        pid = user.get("selected_product")
                        if pid and pid in cart:
                            if qty == 0:
                                del cart[pid]
                                send_whatsapp_message(
                                    phone, f"🗑️ Removed *{PRODUCTS[pid]['name']}* from your cart."
                                )
                            else:
                                cart[pid] = qty
                                send_whatsapp_message(
                                    phone,
                                    f"🔁 Updated *{PRODUCTS[pid]['name']}* quantity to {qty}.",
                                )
                            user["stage"] = "menu"
                            send_whatsapp_message(phone, main_menu_text())
                        else:
                            send_whatsapp_message(phone, "That product isn't in your cart.")
                    else:
                        send_whatsapp_message(
                            phone, "Please enter a valid number (0 to remove, or positive integer)."
                        )
                    save_user_data(user_sessions)
                    continue

                # Direct checkout from main menu
                if text in ["4", "checkout", "proceed to checkout"]:
                    if not cart:
                        send_whatsapp_message(
                            phone, "🛒 Your cart is empty — add items before checkout."
                        )
                        send_whatsapp_message(phone, main_menu_text())
                        user["stage"] = "menu"
                    else:
                        total = sum(PRODUCTS[pid]["price"] * qty for pid, qty in cart.items())
                        send_whatsapp_message(
                            phone,
                            f"💳 Your total is ₹{total}. Reply *confirm* to complete purchase or *cancel* to return.",
                        )
                        user["stage"] = "awaiting_checkout_confirm"
                    save_user_data(user_sessions)
                    continue

                # Customer support
                if text in ["5", "customer support", "support", "customer care"]:
                    send_whatsapp_message(
                        phone,
                        "📞 Customer Support:\nCall: +91-9876543210\nEmail: support@shopease.com\n\nWe are available 9:00–18:00 IST.",
                    )
                    send_whatsapp_message(phone, "Anything else? Here's the main menu:")
                    send_whatsapp_message(phone, main_menu_text())
                    user["stage"] = "menu"
                    save_user_data(user_sessions)
                    continue

                # Help / main menu
                if text in ["6", "help", "menu", "main menu"]:
                    send_whatsapp_message(phone, main_menu_text())
                    user["stage"] = "menu"
                    save_user_data(user_sessions)
                    continue

                # Fallback
                send_whatsapp_message(
                    phone, "😕 I didn't understand that. Here's the main menu to guide you:"
                )
                send_whatsapp_message(phone, main_menu_text())
                user["stage"] = "menu"
                save_user_data(user_sessions)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)

