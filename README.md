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

### Install ngrok
#### Install ngrok Agent
1. Download the latest ngrok binary for the linux distro from [ngrok download page](https://ngrok.com/download/linux?tab=download). Select the operating system as Linux, select the version, and copy the link that appears in the Download button. Below is an example for x86-64:
```bash
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
```
2. Unzip the downloaded file and move it to a directory in the PATH, i.e., `/usr/local/bin`:
```bash
sudo tar xvzf ./ngrok-v3-stable-linux-amd64.tgz -C /usr/local/bin
```
ngrok is now installed on the system.

### Authenticate the ngrok Agent
1. Login to [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken). Create account if not created.
2. Copy the Authtoken provided in the dashboard.
3. Authenticate the ngrok agent by using the command:
```bash
ngrok authtoken NGROK_AUTHTOKEN
```
**Note:** Replace the NGROK_AUTHTOKEN with the token copied from the dashboard.  

ngrok is now installed and running on the system.


## 📄Creating Whatsapp Templates
For this chatbot, we will be using **WhatsApp Interactive Templates** which expand the content we can send recipients beyond the standard *message template* and *media messages template* types to include interactive buttons. Interactive templates allow us to include actionable elements such as **buttons**.

We will primarily use:
- **List Messages**
- **Reply Button Messages**

### Creating an Interactive List WhatsApp Message
For creating an interactive list whatsapp message, the following json will be sent as payload:

```json
{
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": RECIPIENT_WAID,
    "type": "interactive",
    "interactive": {
        "type": "list",
        "header": {"type": "text", "text": "your-header-content"},
        "body": {"text": "your-text-message-content"},
        "footer": {"text": "your-footer-content"},
        "action": {
            "button": "cta-button-content",
            "sections":[
              {
                "title":"your-section-title-content",
                "rows": [
                  {
                    "id":"unique-row-identifier",
                    "title": "row-title-content",
                    "description": "row-description-content",           
                  }
                ]
              },
              {
                "title":"your-section-title-content",
                "rows": [
                  {
                    "id":"unique-row-identifier",
                    "title": "row-title-content",
                    "description": "row-description-content",           
                  }
                ]
              },
              ...
            ]
        }
    }
}
```

### Creating an Interactive Reply Button WhatsApp Message
For creating an interactive reply button whatsapp message, the following json will be sent as payload:

```json
{
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": RECIPIENT_WAID,
    "type": "interactive",
    "interactive": {

        "type": "button",
        "body": {
            "text": "your-message-content"
        },
        "action": {
            "buttons": [
                {
                    "type": "reply",
                    "reply": {
                        "id": "your-id-1",
                        "title": "some-title-1"
                    }
                },

                {
                    "type": "reply",
                    "reply": {
                        "id": "your-id-2",
                        "title": "some-title-2"
                    }
                },
                ...
            ]
        }
    }
}
```

## 🚀 Running the Chatbot

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

### Usage
- Open WhatsApp and send a message (___e.g., Hi___) to the registered WhatsApp Business number.
- The bot will respond with a main menu.
- You can:
    - Type `1` to browse products
    - Type `2` to view the cart
    - Type `3` to edit the cart
    - Type `4` to checkout
    - Type `5` for Customer Support
    - Type `menu` or `6` anytime to return to help menu

