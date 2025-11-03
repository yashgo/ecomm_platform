# 🛍️ Integration of N8N with E-Commerce WhatsApp Chatbot

This document provides step-by-step instructions for installing and configuring **N8N locally and integating it with E-Commerce Chatbot for WhatsApp** built using Python to inegrate the user data with the google sheets.

## 🤖 Introduction to N8N
It is an open-source workflow automation platform, enables users to visually create workflows with a node-based interface. It can be used via cloud or can be locally hosted. It supports developers with JavaScript, API calls and self-hosting and also offer over 200 integrations like Google Sheets, Slack, GitHub, etc.

## ✏️ Preparation
Before using the N8N and the chatbot, ensure that **Docker** and **Python** is installed on your system. It is recommended to use a **virtual environment** to avoid dependency conflicts and to simplify library management.


## 📋 Prerequisites

Before proceeding with the installation, make sure the following requirements are met:

- **Docker Engine** and **Docker** using the rpm repository
- **Docker Compose** installed and running
- **A registered domain (e.g., `xyz.com`)**
- **Cloudflare Tunnel** to expose n8n to public
- **Google Cloud Account**
- **Python 3.10+** installed and available in your PATH
- **pip** (Python package manager) updated to the latest version
- **Virtual environment** (recommended, as shown above)
- A **Linux-based environment** (tested on Ubuntu/Debian/Fedora, may vary for others)


## ⚙️ Installation Instructions

### 🐳 Docker Installation

> **Note:** This guide uses Fedora as the example system, but the steps apply to any Linux distribution. For other distros, refer to the official Docker installation guide at `https://docs.docker.com/engine/install`.


#### Set up the rpm repository
1. Install the dnf-plugins-core package to manage the DNF repositories.
2. Add the docker repository

```bash
sudo dnf -y install dnf-plugins-core
sudo dnf-3 config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
```

#### Install the Docker Engine
1. To install the latest version, run:
```bash
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
2. When prompted, verify the GPG key fingerprint — **`060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35`** — and accept it.

> **Note:** The command installs Docker but doesn’t start it. It also creates a `docker` group without adding any users by default.

3. Start Docker Engine and enable it to run on boot:
```bash
sudo systemctl enable --now docker
```
> **Note:** This enables the Docker service to start automatically at boot.  
> To start Docker manually instead, run:  
> `sudo systemctl start docker`

4. Verify that the installation is successful by running the hello-world image:
```bash
sudo docker run hello-world
```
> **Note:** This command downloads a test image, runs it in a container, prints a confirmation message, and then exits.

Docker Engine is now successfully installed and started.


### 🛡️ Cloudflare Tunnel Installation Instructions
> **Note:** To use a Cloudflare Tunnel, you must have a Cloudflare-managed domain. You can either register a new domain with Cloudflare or transfer your existing domain to Cloudflare.

#### Transfer an existing domain to Cloudflare
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Add your domain to cloudflare.
3. Update your domain’s **nameservers** to the ones provided by Cloudflare.
    > E.g.: For **GoDaddy**, go to **GoDaddy → Domain → DNS → Nameservers**, and change them with the Cloudflare's Nameservers.

<!-- spacing -->

> **Note:** It may take upto **24 hours** to change the nameservers of the domain. Once the nameservers are updated, you will receive a confirmation email from Cloudflare.

#### Setting up the Cloudflare Tunnel

##### Creating a Cloudflare Tunnel
1. Log in to [Cloudflare One](https://one.dash.cloudflare.com/).
2. Go to **Networks > Connectors > Cloudflare Tunnels**
3. Select **Create a tunnel**
4. Choose **Cloudflared** as the connector type and select **Next**.
5. Enter a name for the tunnel.
6. Click on **Save tunnel**.
7. Now, install `cloudflared` on your system by clicking on the appropriate operating system under **Choose an environment**. In this case, we select **Red Hat**. Then, copy the command in the box below and paste it in the terminal. Run the command.
8. Once, the command has finished running, the connector will appear in Cloudflare One.
9. Select Next.

##### Configuring the Cloudflare Tunnel
1. Go to the **Published application routes** tab.
2. Enter a subdomain (`n8n`) and select the **Domain** from the dropdown menu.
3. Under **Service**, choose the **Service type** as `https` and specify the URL as `localhost`
4. Under **Additional application settings > TLS**, turn on the **No TLS Verify**.
5. Select **Complete setup**.

Anyone on the Internet can now access the application at the specified hostname.


### 🤖 N8N Installation Instructions
1. Create a project directory to store your n8n environment configuration and Docker Compose files.
```bash
mkdir n8n-compose
cd n8n-compose
```
2. Inside the `n8n-compose` directory, create a .env file to customize n8n instance's details:
```bash
# .env file
# DOMAIN_NAME and SUBDOMAIN together determine where n8n will be reachable from
# The top level domain to serve from
DOMAIN_NAME=example.com

# The subdomain to serve from
SUBDOMAIN=n8n

# The above example serve n8n at: https://n8n.example.com

# Optional timezone to set which gets used by Cron and other scheduling nodes
# New York is the default value if not set
GENERIC_TIMEZONE=Asia/Kolakata

# The email address to use for the TLS/SSL certificate creation
SSL_EMAIL=user@example.com
```
3. Inside the project directory, create a directory called `local-files` for sharing files between the n8n instance and the host system.
```bash
mkdir local-files
```
4. Create a `docker-compose.yml` file and paste the following in the file:
```yaml
services:
  traefik:
    image: "traefik"
    restart: always
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.web.http.redirections.entryPoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.mytlschallenge.acme.tlschallenge=true"
      - "--certificatesresolvers.mytlschallenge.acme.email=${SSL_EMAIL}"
      - "--certificatesresolvers.mytlschallenge.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - traefik_data:/letsencrypt
      - /var/run/docker.sock:/var/run/docker.sock:ro

  n8n:
    image: docker.n8n.io/n8nio/n8n
    restart: always
    ports:
      - "127.0.0.1:5678:5678"
    labels:
      - traefik.enable=true
      - traefik.http.routers.n8n.rule=Host(`${SUBDOMAIN}.${DOMAIN_NAME}`)
      - traefik.http.routers.n8n.tls=true
      - traefik.http.routers.n8n.entrypoints=web,websecure
      - traefik.http.routers.n8n.tls.certresolver=mytlschallenge
      - traefik.http.middlewares.n8n.headers.SSLRedirect=true
      - traefik.http.middlewares.n8n.headers.STSSeconds=315360000
      - traefik.http.middlewares.n8n.headers.browserXSSFilter=true
      - traefik.http.middlewares.n8n.headers.contentTypeNosniff=true
      - traefik.http.middlewares.n8n.headers.forceSTSHeader=true
      - traefik.http.middlewares.n8n.headers.SSLHost=${DOMAIN_NAME}
      - traefik.http.middlewares.n8n.headers.STSIncludeSubdomains=true
      - traefik.http.middlewares.n8n.headers.STSPreload=true
      - traefik.http.routers.n8n.middlewares=n8n@docker
    environment:
      - N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
      - N8N_HOST=${SUBDOMAIN}.${DOMAIN_NAME}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - N8N_RUNNERS_ENABLED=true
      - NODE_ENV=production
      - WEBHOOK_URL=https://${SUBDOMAIN}.${DOMAIN_NAME}/
      - GENERIC_TIMEZONE=${GENERIC_TIMEZONE}
      - TZ=${GENERIC_TIMEZONE}
    volumes:
      - n8n_data:/home/node/.n8n
      - ./local-files:/files

volumes:
  n8n_data:
  traefik_data:

```
> **Note:** The Docker Compose file above configures two containers: one for n8n, and one to run traefik, an application proxy to manage TLS/SSL certificates and handle routing.

5. Start n8n by running:
```bash
sudo docker compose up -d
```
6. To stop the containers, type:
```bash
sudo docker compose stop
```

The n8n instance is now up and running.


## Configuring N8N Instance
### Connecting the N8N instance with Google Sheets

#### Setup Google Cloud Project
1. Navigate to [Google Cloud Console](https://console.cloud.google.com/).
2. In the Project Picker, Click on **New Project**.
3. Enter the name of the project, e.g., `n8n-project` and click on **Create**.
4. Then open the created project.

#### Enable APIs
1. Go to **APIs & Services > Enabled APIs & Services**
2. In the search bar, search for Google Sheets and click on it.
3. Click **Enable** to enable the API.
4. Do the same for **Google Drive API**.

#### Setup OAuth
1. Go to **APIs & Services**.
2. On the left hand side, click **OAuth consent screen** and click on **Get started**.
3. Enter the name of the app, e.g., `n8n-sheet` and select the email from the drop-down menu in **User support email** under the **App Information**, then click Next.
4. Select the Audience as **External** and click Next.
5. Enter the Email ID in the **Contact Information** and click on next.
6. Check the box, agreeing to the User Policy.
7. Click on Create to configure the project.

#### Create Credentials in N8N
1. Open N8N and login.
2. Then go to credentials, below Overview and click on **Create Credential**.
3. Select **Google Sheets OAuth2 API** and click on **Continue**.
4. Copy the **OAuth Redirect URL**.

#### Configure OAuth Client
1. In the left hand side of **OAuth Consent Screen**, click on **Clients**.
2. Select **Application type** as **Web application**.
3. Enter the name of the client, e.g., n8n-sheets-client.
4. Click on **Add URL** under **Authorized redirect URls** and paste the OAUTH Redirect URL copied from N8N.
5. Click on **Create**.
> **Note:** It may take 5 minutes to a few hours for settings to take effect. 
6. Now, navigate to **OAuth Consent Screen > Branding** on the left hand side.
7. Enter the **Application home page** under the **App Domain**, eg., `https://n8n.domain`
8. Enter the **Authorized domain**, e.g., `xyz.com` under the **Authorized domains**.
9. Click on **Save**.
10. Now, navigate to **OAuth Consent Screen > Audience** on the left hand side.
11. Click on **Add users** under **Test users** to add the users allowed to access the n8n instance.
12. Enter the enail ID of the user and click on **Save**.
13. Now, navigate to **OAuth Consent Screen > Clients** on the left hand side and click on the client that we just created.
14. Under the **Additional Information**, copy the **Client ID** and the **Client Secret**.

#### Connecting N8N to the Google Sheets API
1. Return to the Create Credentials screen in the N8N instance.
2. Paste the **Client ID** and the **Client Secret** in the respective fields.
3. Click on **Sign in with Google**.
4. Sign in using the account that was entered in the **Test User**.
5. Click on **Allow**.

Now, the N8N instance is connected with the Google Sheets.


### Connecting the Chtabot with the N8N instance
1. Create a google sheet and name it anything, e.g., Chatbot WhatsApp API and add the following columns:

    | Timestamp | Phone | Product Name | Quantity | Unit Price | Total (Item) | Grand Total | Stage |
    |------------|--------|---------------|-----------|-------------|---------------|--------------|--------|
    |------------|--------|---------------|-----------|-------------|---------------|--------------|--------|

2. Add some dummy values to make it easier for N8N to map the columns.

    | 2025-10-24 11:40  | 91xxxxxxxxxx | Bluetooth Headphones | 2         | 799         | 1598          | 1598         | Completed  |
    |-|-|-|-|-|-|-|-|
3. Go to N8N instance and click on **Create Workflow**
4. Add a **On webhook call** trigger and edit it.
5. Change the HTTP Method to POST and copy the Webhook URL.
6. Now, click on `+` button and add **Google Sheets** trigger by clicking on **Action in an app > Google Sheets**.
7. Select **Append or update row in sheet** as the **SHEET WITHIN DOCUMENT ACTIONS**.
8. Select the google sheet from the drop-down menu in the **Document** column and select **Sheet1** in the **Sheet** column.
9. Select **Map Each Column Manually** in the **Mapping Column Mode** and select **Timestamp** in the **Column to match on**.
10. Under the Values to Send, select **Expression** in the column and map the values as the following:

    |Field|Expression|
    |---|---|
    |Timestamp|`{{ $json.body.timestamp }}`|
    |Phone|`{{ $json.body.phone }}`|
    |Product Name|`{{ $json.body.product_name }}`|
    |Quantity|`{{ $json.body.quantity }}`|
    |Unit Price|`{{ $json.body.price }}`|
    |Total (Item)|`{{ $json.body.total_item }}`|
    |Grand Total|`{{ $json.body.grand_total }}`|
    |Stage|`{{ $json.body.stage }}`|

11. Click Back to canvas.
12. Now, in the python app.py file, add the following function to export values to google sheet using N8N:
```python
N8N_WEBHOOK_URL = "{the webhook url from n8n}"

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
```
13. Also, rewrite the checkout logic to call the export function on checkout to actually run the workflow:
```python
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
```
14. Now, save the workflow and click on **Execute Workflow** to start the workflow.

15. Run the Flask Server
```bash
python app.py
```

It will start on http://127.0.0.1:5000/.

16. And expose Local Server with ngrok

```bash
ngrok http 5000
```

It will provide an HTTPS URL: ` https://egal-grizzly-bayleigh.ngrok-free.dev `

On checkout, the data exports to the google sheet.
