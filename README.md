# Electronic Vehicles Sales Website — Python Flask & Google Cloud

An Electronic Vehicles Sales Website built with Python, Flask, Firebase Authentication, and Google Cloud Datastore.

---

## Prerequisites

Make sure the following are installed before getting started:

- [Python 3.x](https://www.python.org/downloads/) 
- [Google Cloud SDK (gcloud CLI)](https://cloud.google.com/sdk/docs/install)
- A Google Cloud project with Datastore enabled
- A Firebase project linked to the same Google Cloud project

---

## Project Structure

```
task-board-website-project/
├── main.py               # Flask app entry point
├── requirements.txt      # Python dependencies
├── app.yaml              # GCP App Engine config
├── index.yaml            # Cloud Datastore index config
├── static/               # CSS, JS, images
├── templates/            # HTML templates (Jinja2)
└── your-service-key.json # GCP service account key (DO NOT commit this)
```

---

## Local Setup

### 1. Clone the repository

```cmd
git clone https://github.com/pnaraltnsk/electronic-vehicles-website-project.git
cd electronic-vehicles-website-project
```

### 2. Create and activate a virtual environment

```cmd
python -m venv venv
venv\Scripts\activate
```

> On Mac/Linux: `source venv/bin/activate`

You should see `(venv)` appear at the start of your terminal prompt.

### 3. Install dependencies

```cmd
pip install -r requirements.txt
```

> If you get build errors, try: `venv\Scripts\python.exe -m pip install -r requirements.txt`

### 4. Add your GCP service account key

- Go to [console.cloud.google.com](https://console.cloud.google.com)
- Navigate to **IAM & Admin → Service Accounts**
- Select your service account → **Keys** tab → **Add Key → Create new key → JSON**
- Download the JSON file and place it in the project root folder
- Add the filename to `.gitignore` so it is never committed:

```
echo your-service-key.json >> .gitignore
```

### 5. Set the credentials environment variable

**Windows Command Prompt:**
```cmd
set GOOGLE_APPLICATION_CREDENTIALS=your-service-key.json
```

**Mac/Linux:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="your-service-key.json"
```

> This must be run every time you open a new terminal session before starting the app.

### 6. Run the app

```cmd
python main.py
```

The app will be available at: `http://127.0.0.1:8080`

---

## Authentication

This project uses **Firebase Authentication** — there are no passwords stored in Datastore. To log in you need a Firebase account.

### Adding a user

1. Go to [console.firebase.google.com](https://console.firebase.google.com)
2. Select your project
3. Navigate to **Authentication → Users**
4. Click **Add user** and enter an email and password
5. Use those credentials to log in through the app

---

## Deploying to Google Cloud App Engine

```cmd
# Authenticate with Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Deploy Datastore indexes first
gcloud datastore indexes create index.yaml

# Deploy the app
gcloud app deploy app.yaml
```

---

## requirements.txt 

```
cachetools==4.2.4
certifi==2021.10.8
charset-normalizer==2.0.12
click==8.0.4
colorama==0.4.4
Flask==2.0.3
google-api-core==2.7.1
google-auth==1.30.0
google-cloud-core==2.2.3
google-cloud-datastore==2.4.0
googleapis-common-protos==1.56.0
grpcio==1.44.0
grpcio-status==1.44.0
idna==3.3
itsdangerous==2.1.1
Jinja2==3.0.3
libcst==0.4.1
MarkupSafe==2.1.1
mypy-extensions==0.4.3
proto-plus==1.20.3
protobuf==3.19.4
pyasn1==0.4.8
pyasn1-modules==0.2.8
PyYAML==6.0
requests==2.27.1
rsa==4.8
six==1.16.0
typing-inspect==0.7.1
typing_extensions==4.1.1
urllib3==1.26.9
Werkzeug==2.0.3
```

---

## Security Notes

- **Never commit your service account JSON key to git**
- Always add it to `.gitignore` before placing it in the project folder
- If a key is accidentally committed, delete it immediately in GCP (**IAM & Admin → Service Accounts → Keys**) and create a new one
