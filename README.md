* #  Farm2Market - Digital Agri-Marketplace

**Farm2Market** is a Django-based web platform that allows smallholder farmers to sell their products directly to buyers without middlemen. It provides an e-commerce-like interface for listing agricultural products, placing orders, and making payments via **M-Pesa STK Push**.

---

## link to the Demo Video
https://drive.google.com/file/d/1Xadrl1zrFMJq6oi6kJ1rjWhXq3uFtZis/view?usp=sharing

## link to the deployed version 
https://mawia.thisisemmanuel.pro/products/

## Link to zip file
https://alueducation.instructure.com/courses/2050/assignments/28964/submissions/834?comment_id=206563&download=344050



## Link to Required documents
https://docs.google.com/document/d/17BMKs8Ko9G4xaN9xRF6H1_nWA5eREdSGZNce7KS-5C0/edit?usp=sharing

## Screenshots
https://drive.google.com/file/d/1B6DNztjMm2jKU2pHxE4py1O0XQ_Xlxof/view?usp=sharing
https://drive.google.com/file/d/1iXZTMslRHzUMZa370UttTrYSPm1c_t8t/view?usp=sharing
https://drive.google.com/file/d/1dOG6QDqwpNve58e0AdFKPs_SxhhDuAVI/view?usp=sharing
https://drive.google.com/file/d/1XPwLBNKrA7nlqc7g8AO5QLPp_XAovsp5/view?usp=sharing

## 🌟 Key Features

* 👩‍🌾 Farmer Product Listings
* 👩‍🌾 Buyers Dashboard
* 🛒 Cart & Checkout Workflow
* 💰 M-Pesa STK Push Payments
* 📋 Orders  Dashboard
* 🔐 Secure Login and Profile Management
* 📱 Mobile-Responsive UI

---

## 🛠️ Tech Stack

* **Framework**: Django 
* **Frontend**: Bootstrap 5, HTML5
* **Database**: SQLite (default, dev)
* **Payment API**: Safaricom Daraja API
* **Tunneling**: Ngrok for webhook testing

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/mkatiwa/farmonemarket.git
cd farmonemarket
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
# or
source .venv/bin/activate    # Linux/macOS
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up `.env` Variables

Create a `.env` file in your root project directory:

```
DEBUG=True
SECRET_KEY=your_django_secret
ALLOWED_HOSTS=127.0.0.1,localhost

MPESA_CONSUMER_KEY=your_daraja_consumer_key
MPESA_CONSUMER_SECRET=your_daraja_consumer_secret
MPESA_SHORTCODE=your_shortcode
MPESA_PASSKEY=your_lipa_na_mpesa_passkey
```

### 5. Apply Migrations & Run Server

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📲 Testing M-Pesa STK Push (With Ngrok)

To receive M-Pesa callbacks:

### Step 1: Install Ngrok

Download it from: [https://ngrok.com/download](https://ngrok.com/download)

Unzip and move the executable to your system path.

### Step 2: Authenticate Ngrok

```bash
ngrok config add-authtoken <your_token_here>
```

### Step 3: Start Ngrok

```bash
ngrok http 8000
```

Copy the HTTPS URL generated (e.g., `https://abcd1234.ngrok.io`).

### Step 4: Update Safaricom Daraja Callback URLs

Log in to [Daraja Portal](https://developer.safaricom.co.ke), set your:

* **Confirmation URL**: `https://your-ngrok-url/mpesa/confirmation/`
* **Validation URL**: `https://your-ngrok-url/mpesa/validation/`
* **Callback (STK Push)**: `https://your-ngrok-url/mpesa/callback/`

---

## 📂 Folder Structure

```
farm2market/
️️️
├── accounts/         # Registration & Login
├── carts/            # Cart logic
├── dashboard/        # Admin dashboard
├── mpesa/            # Payment integration
├── orders/           # Order management
├── products/         # Product listings
├── profiles/         # Farmer/buyer profiles
├── static/           # Static assets (CSS, JS)
├── templates/        # HTML files
├── Farm2Market/      # Main project settings
└── manage.py
```

---

## 📅 requirements.txt

Save this file as `requirements.txt` in your root folder:

```
Django>=5.0.0
python-decouple
requests
pytz
Pillow
```


## 🤝 Contributing

1. Fork this repo
2. Create your branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your message"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a pull request 🎉



## 💖 Empowering Farmers, One Click at a Time!
 
