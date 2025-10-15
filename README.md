# 🛍️ E-Commerce WhatsApp Chatbot

This document provides step-by-step instructions for installing and configuring **E-Commerce Chatbot for WhatsApp** built using Python.

## 🤖 Introduction to E-Commerce Chatbot
It is a simple, text-based WhatsApp chatbot built using **Python**, **Flask** and the **WhatsApp Business Cloud API**. It lets users browse products, manage a cart, and checkout — all from WhatsApp.

## ✏️ Preparation
Before using the Chatbot, ensure that **Python** is installed on your system. It is recommended to use a **virtual environment** to avoid dependency conflicts and to simplify library management.

To create a virtual environment in your chosen directory, open a terminal and run:
```bash
python -m venv <directory>
```
Activate the virtual environment:
```bash
source venv/bin/activate
```


## 📋 Prerequisites

Before proceeding with the installation, make sure the following requirements are met:

- **Python 3.10+** installed and available in your PATH
- **pip** (Python package manager) updated to the latest version
- **Virtual environment** (recommended, as shown above)
- A **Linux-based environment** (tested on Ubuntu/Debian/Fedora, may vary for others)


## ⚙️ Installation Instructions

### Create a Authentication Token
1. Go to WhatsApp Business Settings and select the app.
2. Go to Users \> System Users.
3. Click on Add button to create a newe user. Provide a name and select Employee role.
4. Click on Create system user to create the user.
5. Select the user and then click on Generate Token.
6. Select the app, then select the token expiration period.
7. Then Assign permissions, mainly three permissions - 
`whatsapp_business_manage_events`, 
`whatsapp_business_management` and `whatsapp_business_messaging`.
8. Click on Generate Token to generate the authentication token.

### Create a .env file in the parent directory:
```bash
# .env file
APP_ID = <<YOUR-WHATSAPP-BUSINESS-APP_ID>>
APP_SECRET = <<YOUR-WHATSAPP-BUSINESS-APP_SECRET>>
RECIPIENT_WAID = <<YOUR-RECIPIENT-TEST-PHONE-NUMBER>>
VERSION = v22.0
PHONE_NUMBER_ID = <<YOUR-WHATSAPP-BUSINESS-PHONE-NUMBER-ID>>
ACCESS_TOKEN = <<YOUR-SYSTEM-USER-ACCESS-TOKEN>>
```


### Run the Flask Server
```bash
python app.py
```

It will start on http://127.0.0.1:5000/.

### Expose Local Server with ngrok

```bash
ngrok http 5000
```

It will provide an HTTPS URL: ` https://egal-grizzly-bayleigh.ngrok-free.dev `


### Configure Webhook in Meta Developer Console
1. Go to Developers Portal \> My Apps \> Your WhatsApp App.
2. Under Webhook \> click Configure Webhook.
3. Set:
    - Callback URL: https://egal-grizzly-bayleigh.ngrok-free.dev/webhook
    - Verify Token: sample_verify_token
4. Assign permissions to the Webhook fields:
    - messages
    - message_template_status_update (optional)
5. Click Verify and Save.


