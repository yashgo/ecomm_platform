# app.py
import os
import re
import json
import time
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from word2number import w2n

# Load environment variables from .env
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = "shopease_verify_token"  # Match with your webhook setup
RECIPIENT_WAID=os.getenv("RECIPIENT_WAID")
VERSION = os.getenv("VERSION", "v23.0")

app = Flask(__name__)

DATA_FILE = "user_data.json"
SESSION_TIMEOUT_SECONDS = 5 * 60  # 5 minutes


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


def send_template_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

    try:
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            print("Status:", response.status_code)
            print("Content-type:", response.headers.get("content-type"))
            print("Body:", response.text)
        else:
            print(response.status_code)
            print(response.text)
    except requests.ConnectionError as e:
        print("Connection Error:", str(e))


PRODUCTS = {
    "1": {"name": "🖱️ Wireless Mouse", "price": 650},
    "2": {"name": "🎧 Bluetooth Headphones", "price": 799},
    "3": {"name": "🔌 USB-C Charger", "price": 1499},
    "4": {"name": "📇 Laptop Stand", "price": 699},
}

MENU = {
    "cart_list_show": {"name": "1️⃣  Browse Our Collection"},
    "view_cart_show": {"name": "2️⃣  View Cart"},
    "edit_cart_show": {"name": "3️⃣  Edit Cart"},
    "checkout_cart_show": {"name": "4️⃣  Proceed to Checkout"},
    "support": {"name": "5️⃣  Customer Support"},
    "help_menu": {"name": "6️⃣  Help / Main Menu"},
    "exit": {"name": "7️⃣  Exit"}
}


def menu_help():
    sections = [{
        "title": "Help Menu",
        "rows": [
            {
                "id": f"{mid}",
                "title": m["name"],
            } for mid, m in MENU.items()
        ]
    }]

    payload = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": RECIPIENT_WAID,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": "🛍️ Welcome to ShopEase! 👋"},
            "body": {"text": "Choose an option below 👇"},
            "action": {"button": "View Menu", "sections": sections}
        }
    })

    return payload


def extract_number(text: str):
    text = text.lower().strip()

    # 1. Try to find digits: "2", "15", "300"
    m = re.search(r'\b\d+\b', text)
    if m:
        return int(m.group())

    # 2. Try to find number words: "two", "three", "twenty one", etc.
    tokens = text.split()

    # Try 3-word, then 2-word, then 1-word chunks: e.g. "twenty one", "two"
    for span_len in (3, 2, 1):
        for i in range(len(tokens) - span_len + 1):
            chunk = " ".join(tokens[i:i+span_len])
            try:
                value = w2n.word_to_num(chunk)
                return value
            except ValueError:
                continue

    # 3. No number found
    return None


def show_products_text():
    msg = ""
    for pid, p in PRODUCTS.items():
        msg += f"{pid}. {p['name']} — ₹{p['price']}\n"
    return msg


def view_products():
    sections = [{
        "title": "Available Products",
        "rows": [
            {
                "id": f"{pid}",
                "title": p["name"],
                "description": f"₹{p['price']}"
            } for pid, p in PRODUCTS.items()
        ]
    }]

    payload = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": RECIPIENT_WAID,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": "🛍️ Our Collection"},
            "body": {"text": "Choose a product below 👇"},
            "action": {"button": "View Products", "sections": sections}
        }
    })

    return payload


def cart_text(cart):
    if not cart:
        return "🛒 Your cart is empty.\n\nWhat would like to do next?"

    msg = "*🧺 Your Cart:*\n\n"
    total = 0
    count = 0
    for pid, qty in cart.items():
        p = PRODUCTS.get(pid, {"name": "Unknown", "price": 0})
        msg += f"- {p['name']} × {qty} = ₹{p['price'] * qty}\n"
        total += p["price"] * qty
        count += qty
    msg += f"\n*Items:* {count}\n*Total:* ₹{total}\n\nWhat would you like to do next?"
    return msg


def cart_item_select(cart):
    sections = [{
        "title": "Your Cart",
        "rows": [
            {
                "id": pid,
                "title": p["name"],
                "description": f"{qty} × ₹{p['price']} = ₹{p['price'] * qty}"
            }
            for pid, qty in cart.items()
            for p in [PRODUCTS.get(pid, {"name": "Unknown", "price": 0})]
        ]
    }]

    payload = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": RECIPIENT_WAID,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": "🧺 Your Cart"},
            "body": {"text": "Choose a product below 👇"},
            "action": {"button": "View Products", "sections": sections}
        }
    })

    return payload


def view_cart_card(msg):
    payload = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": RECIPIENT_WAID,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": msg
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "edit_cart",
                            "title": "Edit Cart"
                        }
                    },

                    {
                        "type": "reply",
                        "reply": {
                            "id": "checkout_cart",
                            "title": "Checkout Cart"
                        }
                    },

                    {
                        "type": "reply",
                        "reply": {
                            "id": "continue_shopping",
                            "title": "Continue Shopping"
                        }
                    }
                ]
            }
        }
    })

    return payload


def edit_cart_card():
    payload = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": RECIPIENT_WAID,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "What would you like to do?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "del_product",
                            "title": "Delete Product"
                        }
                    },

                    {
                        "type": "reply",
                        "reply": {
                            "id": "mod_quantity",
                            "title": "Modify Quantity"
                        }
                    },

                    {
                        "type": "reply",
                        "reply": {
                            "id": "continue_shopping",
                            "title": "Continue Shopping"
                        }
                    }
                ]
            }
        }
    })

    return payload


def checkout_cart_card():
    payload = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": RECIPIENT_WAID,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Do you want to checkout the items?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "checkout_yes",
                            "title": "Yes"
                        }
                    },

                    {
                        "type": "reply",
                        "reply": {
                            "id": "checkout_no",
                            "title": "No"
                        }
                    }
                ]
            }
        }
    })

    return payload


def post_checkout(cart):
    total = sum(PRODUCTS[pid]["price"] * qty for pid, qty in cart.items())
    checkout_mssg = f"Checkout complete! Your card was charged ₹{total}.\nThank you for shopping with ShopEase! 🛍️"

    payload = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": RECIPIENT_WAID,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": checkout_mssg
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "checkout_menu",
                            "title": "Continue Shopping"
                        }
                    },

                    {
                        "type": "reply",
                        "reply": {
                            "id": "checkout_exit",
                            "title": "Exit"
                        }
                    }
                ]
            }
        }
    })

    return payload



def continue_shopping():
    payload = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": RECIPIENT_WAID,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "What would you like to do next?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "view_cart",
                            "title": "View Cart"
                        }
                    },

                    {
                        "type": "reply",
                        "reply": {
                            "id": "continue_shopping",
                            "title": "Continue Shopping"
                        }
                    }
                ]
            }
        }
    })

    return payload


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
                    send_template_message(menu_help())
                    user["last_seen"] = now
                    user_sessions[phone] = user
                    save_user_data(user_sessions)
                    continue

                user["last_seen"] = now
                user_sessions[phone] = user
                cart = user.setdefault("cart", {})


                # handle user input or selection
                msg_type = msg.get("type")


                if text in ["hi", "hello", "hey", "start", "menu"]:
                    send_template_message(menu_help())
                    user["stage"] = "menu"
                    save_user_data(user_sessions)
                    continue


                if user["stage"] == "menu":
                    interactive = msg.get("interactive", {})

                    if not interactive or interactive.get("type") != "list_reply":
                        send_template_message(menu_help())
                        user["stage"] = "menu"
                        save_user_data(user_sessions)
                        continue

                    selected = interactive["list_reply"]
                    menu_id = selected["id"]

                    user["stage"] = menu_id
                    save_user_data(user_sessions)


                if user["stage"] == "cart_list_show":
                    payload = view_products()
                    send_template_message(payload)
                    user["stage"] = "cart_list"
                    save_user_data(user_sessions)
                    continue


                if user["stage"] == "cart_list":
                    interactive = msg.get("interactive", {})
                    selected = interactive["list_reply"]
                    product_id = selected["id"]
                    product_title = selected["title"]

                    user["selected_product"] = product_id
                    save_user_data(user_sessions)
                    send_whatsapp_message(phone, f"How many of the {product_title} would you like to add?")
                    user["stage"] = "item_quantity"
                    continue


                if user["stage"] == "item_quantity":
                    quantity = extract_number(text)
                    pid = user.get("selected_product")

                    if quantity is None or quantity <= 0:
                        send_whatsapp_message(phone, "Please enter a valid quantity!")
                        continue

                    if pid and pid in PRODUCTS:
                        cart[pid] = cart.get(pid, 0) + quantity
                        save_user_data(user_sessions)
                        send_whatsapp_message(phone, f"You have added *{quantity} × {PRODUCTS[pid]['name']}* to your cart 🛒")
                        send_template_message(continue_shopping())
                        user["stage"] = "post_add_choice"

                    else:
                        send_whatsapp_message(phone, "Please enter a valid quantity!")
                    continue


                if user["stage"] == "post_add_choice":
                    interactive = msg.get("interactive", {})

                    if interactive.get("type") == "button_reply":
                        selection = interactive["button_reply"]
                        bttn_id = selection["id"]

                        if bttn_id == "view_cart":
                            cart_msg = cart_text(cart)
                            send_template_message(view_cart_card(cart_msg))
                            user["stage"] = "view_cart_choice"
                            save_user_data(user_sessions)
                            continue

                        elif bttn_id == "continue_shopping":
                            send_template_message(menu_help())
                            user["stage"] = "menu"
                            save_user_data(user_sessions)
                            continue


                if user["stage"] == "view_cart_show":
                    if not cart:
                        send_whatsapp_message(phone, f"🛒 Your cart is empty. Please add a product to continue!")
                        send_template_message(menu_help())
                        user["stage"] = "menu"
                        save_user_data(user_sessions)
                        continue

                    else:
                        cart_msg = cart_text(cart)
                        send_template_message(view_cart_card(cart_msg))
                        user["stage"] = "view_cart_choice"
                        save_user_data(user_sessions)
                        continue


                if user["stage"] == "view_cart_choice":
                    interactive = msg.get("interactive", {})

                    if interactive.get("type") == "button_reply":
                        selection = interactive["button_reply"]
                        bttn_id = selection["id"]

                        if bttn_id == "edit_cart":
                            send_whatsapp_message(phone, "Select a product to edit!")
                            send_template_message(cart_item_select(cart))
                            user["stage"] = "edit_cart_product"
                            save_user_data(user_sessions)
                            continue

                        elif bttn_id == "checkout_cart":
                            if not cart:
                                send_whatsapp_message(phone, "🛒 Your cart is empty! Add items before checkout.")
                                send_template_message(menu_help())
                                user["stage"] = "menu"
                                save_user_data(user_sessions)
                                continue
                            else:
                                cart_msg = cart_text(cart)
                                send_whatsapp_message(phone, f"{cart_msg}")
                                send_template_message(checkout_cart_card())
                                user["stage"] = "checkout_cart_choice"
                                save_user_data(user_sessions)
                                continue

                        elif bttn_id == "continue_shopping":
                            send_template_message(menu_help())
                            user["stage"] = "menu"
                            save_user_data(user_sessions)
                            continue


                if user["stage"] == "edit_cart_show":
                    if not cart:
                        send_whatsapp_message(phone, f"🛒 Your cart is empty. Please add a product to continue!")
                        send_template_message(menu_help())
                        user["stage"] = "menu"
                        save_user_data(user_sessions)
                        continue
                    else:
                        send_whatsapp_message(phone, "Select a product to edit!")
                        send_template_message(cart_item_select(cart))
                        user["stage"] = "edit_cart_product"
                        save_user_data(user_sessions)
                        continue


                if user["stage"] == "edit_cart_product":
                    if not cart:
                        send_whatsapp_message(phone, f"🛒 Your cart is empty. Please add a product to continue!")
                        send_template_message(menu_help())
                        user["stage"] = "menu"
                        save_user_data(user_sessions)
                        continue
                    else:
                        interactive = msg.get("interactive", {})
                        selected = interactive["list_reply"]
                        product_id = selected["id"]
                        product_title = selected["title"]
                        user["selected_product"] = product_id
                        save_user_data(user_sessions)
                        send_template_message(edit_cart_card())
                        user["stage"] = "edit_cart_choice"
                        save_user_data(user_sessions)


                if user["stage"] == "edit_cart_choice":
                    interactive = msg.get("interactive", {})

                    if interactive.get("type") == "button_reply":
                        selection = interactive["button_reply"]
                        bttn_id = selection["id"]
                        pid = user["selected_product"]

                        if bttn_id == "del_product":
                            send_whatsapp_message(phone, f"Do you want to delete the {PRODUCTS[pid]['name']}? Please reply in yes or no!")
                            user["stage"] = "edit_del_cart_choice"
                            save_user_data(user_sessions)
                            continue

                        elif bttn_id == "mod_quantity":
                            send_whatsapp_message(phone, f"Enter the new quantity for {PRODUCTS[pid]['name']} !")
                            user["stage"] = "edit_mod_cart_choice"
                            save_user_data(user_sessions)
                            continue

                        elif bttn_id == "continue_shopping":
                            send_template_message(menu_help())
                            user["stage"] = "menu"
                            save_user_data(user_sessions)
                            continue


                if user["stage"] == "edit_del_cart_choice":
                    if text == "yes":
                        pid = user["selected_product"]
                        del cart[pid]
                        send_whatsapp_message(phone, f"{PRODUCTS[pid]['name']} is successfully removed from the cart!")
                        cart_msg = cart_text(cart)
                        send_template_message(view_cart_card(cart_msg))
                        user["stage"] = "view_cart_choice"
                        save_user_data(user_sessions)
                        continue

                    if text == "no":
                        send_template_message(edit_cart_card())
                        user["stage"] = "edit_cart_choice"
                        save_user_data(user_sessions)

                
                if user["stage"] == "edit_mod_cart_choice":
                    mod_quantity = extract_number(text)
                    pid = user["selected_product"]
                    cart[pid] = mod_quantity
                    send_whatsapp_message(phone, f"Updated {PRODUCTS[pid]['name']} to {mod_quantity}")
                    save_user_data(user_sessions)
                    cart_msg = cart_text(cart)
                    send_template_message(view_cart_card(cart_msg))
                    user["stage"] = "view_cart_choice"
                    save_user_data(user_sessions)
                    continue


                if user["stage"] == "checkout_cart_show":
                    if not cart:
                        send_whatsapp_message(phone, "🛒 Your cart is empty! Add items before checkout.")
                        send_template_message(menu_help())
                        user["stage"] = "menu"
                        save_user_data(user_sessions)
                        continue

                    else:
                        cart_msg = cart_text(cart)
                        send_whatsapp_message(phone, f"{cart_msg}")
                        send_template_message(checkout_cart_card())
                        user["stage"] = "checkout_cart_choice"
                        save_user_data(user_sessions)
                        continue


                if user["stage"] == "checkout_cart_choice":
                    if not cart:
                        send_whatsapp_message(phone, "🛒 Your cart is empty! Add items before checkout.")
                        send_template_message(menu_help())
                        user["stage"] = "menu"
                        save_user_data(user_sessions)
                        continue

                    else:
                        interactive = msg.get("interactive", {})

                        if interactive.get("type") == "button_reply":
                            selection = interactive["button_reply"]
                            bttn_id = selection["id"]

                            if bttn_id == "checkout_yes":
                                send_template_message(post_checkout(cart))
                                export_to_n8n(phone, cart, stage="Completed")
                                user["cart"] = {}
                                user["stage"] = "post_checkout_choice"

                            elif bttn_id == "checkout_no":
                                send_whatsapp_message(phone, "All right! Feel free to continue browsing!")
                                send_template_message(menu_help())
                                user["stage"] = "menu"
                                save_user_data(user_sessions)
                                continue


                if user["stage"] == "post_checkout_choice":
                    interactive = msg.get("interactive", {})

                    if interactive.get("type") == "button_reply":
                        selection = interactive["button_reply"]
                        bttn_id = selection["id"]

                        if bttn_id == "checkout_menu":
                            send_template_message(menu_help())
                            user["stage"] = "menu"
                            save_user_data(user_sessions)
                            continue
                        
                        elif bttn_id == "checkout_exit":
                            send_whatsapp_message(phone, f"Thanks for visting 🛍️ShopEase! If you need anything else, type *hi* or *menu* anytime.")
                            user["stage"] = "exit"
                            save_user_data(user_sessions)
                            continue


                if user["stage"] == "support":
                    customer_msg = f"📞 Customer Support:\nCall: +91-9876543210\nEmail: support@shopease.com\n\nWe are available 9:00–18:00 IST.\n\nAnything else? Here's the main menu!"
                    send_whatsapp_message(phone, f"{customer_msg}")
                    send_template_message(menu_help())
                    user["stage"] = "menu"
                    save_user_data(user_sessions)
                    continue


                if user["stage"] == "help_menu":
                    send_template_message(menu_help())
                    user["stage"] = "menu"
                    save_user_data(user_sessions)
                    continue


                if user["stage"] == "exit":
                    send_whatsapp_message(phone, f"Thanks for visting 🛍️ShopEase! If you need anything else, type *hi* or *menu* anytime.")
                    user["stage"] = "exit"
                    save_user_data(user_sessions)
                    continue


                # send_whatsapp_message(phone, "😕 I didn't understand that. Here's the main menu to guide you:")
                # send_template_message(menu_help())
                # user["stage"] = "menu"
                # save_user_data(user_sessions)


    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)


