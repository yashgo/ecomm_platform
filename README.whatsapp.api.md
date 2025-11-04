# 🔌 Whatsapp Business API Installation & Documentation

This document provides requirements and step-by-step instructions for integrating and configuring **WhatsApp Business API** into the business operations, helping the business streanline communication, automate messaging and improve customer support.

## 🤖 Introduction to WhatsApp Business API
WhatsApp Business API enables medium and large businesses to integrate WhatsApp into their systems, automate messaging, and improve customer support.

**Benefits of WhatsApp Business API:**
- **Customer Engagement:** Real-time, personalized communication and instant support.
- **Scalability:** Multi-agent access for managing conversations.
- **Automation:** Chatbots and auto-replies for FAQs and faster responses.
- **Integration:** Works with CRM, e-commerce, and ticketing tools for tracking and history.
- **Security:** End-to-end encryption ensures safe communication.
- **Conversions:** Boosts sales with promotions, reminders, and order updates.

## 📋 Prerequisites

Before proceeding with the integration, make sure the following requirements are met:

- **Facebook Business Manager Account:** Account with completed business verification
- **Verified Business Account on Meta:** Legal name, website, and contact details required
- **Dedicated Phone Number:** Not linked to WhatsApp; must support SMS/voice verification
- **Business Solution Provider:** Either self-host or use providers (e.g., Twilio, 360Dialog)

## 👉 Choosing the Right WhatsApp BSP
- **Ease of Integration:** No-code vs. developer-heavy setup.
- **Pricing Model:** Depend on messaging volume, API access fees, and additional services.
- **Customer Support:** Look for 24/7 support and troubleshooting assistance.
- **Additional Features:** Look for CRM integration, automation tools, and analytics.

## ✅ Allowed and ❌ Restricted Usage of the API
### Allowed
- **OTPs and alerts:** Send OTPs, order updates, reminders via approved templates.
- **Two-Way Chats:** Provide support and reply within the 24-hour window.
- **Rich Media Usage:** Share images, videos, PDFs, buttons, and locations.
- **Personalized Messages:** Add names, dates, and custom fields for relevance.

### Restricted
- **Cold Outreach:** No uninvited messaging; opt-in is mandatory.
- **Unapproved Templates:** All message templates require WhatsApp approval.
- **Spam & Over-Promotion:** Avoid repetitive discount pushes or excessive messaging.
- **Prohibited Content:** No gambling, adult, misleading, or sensitive content.

## 🪜Step-by-Step Instructions

### Register as a Meta Developer (if not already)
> All the following instructions can be found at https://developers.facebook.com/docs/development/register/

1. Log into your Facebook account and go to https://developers.facebook.com/async/registration.
2. Click Next to agree to the Platform Terms and Developer Policies.
3. Verify your account via confirmation code sent to the phone number and email address.
4. Select the option that best describes your profession.

### Create a Meta App

1. Navigate to https://developers.facebook.com/apps/creation/ to begin the app creation process.
2. Enter the App name and App contact email in the App Details.
3. In Use Cases, select Other and click Next.
4. In the app type, select Business.
5. In the details, verify the details and click on Create app button.

### Configure the API
1. You will be redirected to the App Dashboard.
2. Under the **Add products to your app**, click **Set up** button under WhatsApp.
    > If you already have a business portfolio, you will be prompted to attach it. If you don’t have one, you'll be taken through some prompts that will help you create and attach one.
3. **Generate an access token**

    Navigate to WhatsApp \> API Setup in the left-hand menu of App Dashboard, and click the blue **Generate access token** button. Complete the flow to generate the user access token.

4. Add a recipient number

    Under **Send and receive messages**, select the **To** field and choose **Manage phone number list**. Then click on **Add phone number** button and enter the phone number along with the country extension and click Next. The recipient number will receive a confirmation code in WhatsApp that can be used to verify the number.

5. Create a system user for the Business Account

    Go to the App Settings in the business home and then in the left-hand menu, click on **System Users** under **Users**. Click on Add button and then enter a System user name and select the System user role as **Admin** and then click on Create system user. Then configure the assets and assign the WhatsApp app with full control.


### 🏢 Building a simple API using Minimal App with Python and Flask

Before creating the app, ensure that **Python** is installed on your system. It is recommended to use a **virtual environment** to avoid dependency conflicts and to simplify library management.

To create a virtual environment in your chosen directory, open a terminal and run:
```bash
mkdir myproject
cd myproject
python -m venv venv
```
Activate the virtual environment:
```bash
source venv/bin/activate
```
Now, install flask using `pip install flask[async]`

Create a new folder named templates at the project root and create a new file named index.html:

```html
<!DOCTYPE html>
<html>
    <head>
        <title>Flight Confirmation Demo for Python</title>
        <h1 class="text-center">Flight Confirmation Demo for Python</h1>
        <link
            href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"
            rel="stylesheet"
            integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC"
            crossorigin="anonymous"
        />
    </head>
    <body>
        <div class="d-flex flex-row justify-content-center align-items-center">
            <div class="border px-3">
                <div class="row">
                    <div class="col-sm-6 d-none d-sm-block">
                        <img
                            src="https://images.unsplash.com/photo-1530521954074-e64f6810b32d?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NHx8YWlyJTIwdHJhdmVsfGVufDB8fDB8fA%3D%3D&auto=format&fit=crop&w=500&q=60"
                            alt="Login image"
                            class="w-100 vh-50 pt-3 pb-3"
                            style="object-fit: cover; object-position: left"
                        />
                    </div>
                    <div class="col-sm-6 text-black">
                        <div class="px-5 ms-xl-4">
                            <i
                                class="fas fa-crow fa-2x me-3 pt-5 mt-xl-4"
                                style="color: #709085"
                            ></i>
                        </div>

                        <div class="d-flex align-items-center h-custom-2">
                            <form class="w-100" method="post" action="/welcome">
                                <div class="form-outline mb-4">
                                    <input
                                        type="text"
                                        value="this_is_a_demo@email.com"
                                        disabled
                                        class="form-control form-control-md text-muted"
                                    />
                                </div>

                                <div class="form-outline mb-4">
                                    <input
                                        type="text"
                                        value="••••••••••••••••"
                                        disabled
                                        id="form2Example28"
                                        class="form-control form-control-md text-muted"
                                    />
                                </div>

                                <div class="pt-1 mb-4">
                                    <input type="submit" class="btn btn-info btn-lg btn-block" value="Login"/>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

        </div>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    </body>
</html>
```

Create an app.py file at the project root with the content:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
```

**Connecting Python with WhatsApp Business App**

Create a config.json file at the project root with the following settings, replacing any placeholders with details from your WhatsApp Business account dashboard:

```json
{
  "APP_ID": "<<YOUR-WHATSAPP-BUSINESS-APP_ID>>",
  "APP_SECRET": "<<YOUR-WHATSAPP-BUSINESS-APP_SECRET>>",
  "RECIPIENT_WAID": "<<YOUR-RECIPIENT-TEST-PHONE-NUMBER>>",
  "VERSION": "v22.0",
  "PHONE_NUMBER_ID": "<<YOUR-WHATSAPP-BUSINESS-PHONE-NUMBER-ID>>",
  "ACCESS_TOKEN": "<<YOUR-SYSTEM-USER-ACCESS-TOKEN>>"
}
```

> For the APP_SECRET, navigate to https://developers.facebook.com/apps/ and select the App. Now, on the left sidebar, go to **Settings \> Basic**. In the app secret, click the **Show** button to reveal the secret.
>
> In the RECIPIENT_WAID, enter the whatsapp number, where you want to send the message. It should be already be added in the API Setup menu before using. 


Now, install aiohttp to enable your app to perform asynchronous HTTP requests:
```bash
pip install aiohttp[speedups]
```

Now, create a new message_helper.py file at the project root to encapsulate the code that sends text-based messages via the API.

```python
import aiohttp
import json
from flask import current_app

async def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    async with aiohttp.ClientSession() as session:
        url = 'https://graph.facebook.com' + f"/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"
        try:
            async with session.post(url, data=data, headers=headers) as response:
                if response.status == 200:
                    print("Status:", response.status)
                    print("Content-type:", response.headers['content-type'])
                    html = await response.text()
                    print("Body:", html)
                else:
                    print(response.status)        
                    print(response)        
        except aiohttp.ClientConnectorError as e:
            print('Connection Error', str(e))

def get_template_message_input(recipient, template_name="hello_world", lang="en_US"):
    return json.dumps({
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "template",
        "template": {
            "name": template_name,
            "language": { "code": lang }
        }
    })

def get_custom_message(recipient, text):
    return json.dumps({
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {
            "body": text
        }
    })
```


The above code makes an HTTP POST request to the /messages endpoint on the Meta Graph API at graph.facebook.com, passing:

- The Cloud API version you’re working with
- The test phone number that will receive the message (you have already configured this)
- The access token you generated for your System User

Now, create app.py at the project root:
```python
import json
from flask import Flask, render_template
import flask
from message_helper import get_template_message_input, get_custom_message, send_message

app = Flask(__name__)
with open('config.json') as f:
    config = json.load(f)

app.config.update(config)

@app.route("/")
def index():
    return render_template('index.html', name=__name__)

@app.route('/welcome', methods=['POST'])
async def welcome():
    data = get_template_message_input(
        app.config['RECIPIENT_WAID'],
        template_name="hello_world"
    )
    await send_message(data)
    return flask.redirect(flask.url_for('index'))

@app.route('/custom', methods=['POST'])
async def custom():
    message_text="Welcome to the Flight Confirmation Demo App for Python!"
    data = get_custom_message(app.config['RECIPIENT_WAID'], message_text)
    await send_message(data)
    return flask.redirect(flask.url_for('index'))
```

Now, run the app using `flask run`
Then, you’ll see the app running locally at port 5000:
```bash
* Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a pr
oduction WSGI server instead.
* Running on http://127.0.0.1:5000
Press CTRL+C to quit

```

Now, visit http://127.0.0.1:5000/ and you will see the application. Click on the login button. A WhatsApp message will be sent based on the hello_world template to the recipient defined in the json file and configured in the API setup.


> NOTE: Since, we are using a free test phone number provided by WhatsApp when creating the API, we are limited to very basic templates and cannot define a free form template in the API code itself.
