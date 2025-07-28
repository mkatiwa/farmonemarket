import os, base64, requests, re, json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from dotenv import load_dotenv
from datetime import datetime
from django.http import JsonResponse, HttpResponseBadRequest, request, response
from django.views.decorators.csrf import csrf_exempt
from carts.models import Cart
from .forms import PaymentForm
from .models import Transaction

load_dotenv()

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")

MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
CALLBACK_URL = os.getenv("CALLBACK_URL")
MPESA_BASE_URL = os.getenv("MPESA_BASE_URL")


# Create your views here.

class InitiatePaymentView(LoginRequiredMixin, View):


    def post(self, request):
        try:
            phone = request.POST.get('phone_number')
            amount = request.POST.get('amount')

            if not phone or not amount:
                messages.error(request, "Phone number and amount are required")
                return redirect('carts:checkout')

            # Format phone number
            phone = self.format_phone_number(phone)


            if response.get("ResponseCode") == "0":
                #Create a transaction record
                Transaction.objects.create(
                    user=request.user,
                    phone=phone,
                    amount=amount,
                    checkout_request_id=response["CheckoutRequestID"],
                    status='pending'
                )
                return render(request, 'mpesa/pending.html', {
                    'checkout_request_id': response["CheckoutRequestID"]
                })
            else:
                error = response.get("errorMessage", "Failed to initiate payment")
                messages.error(request, error)
                return redirect('carts:checkout.html')

        except Exception as e:
            messages.error(request, str(e))
            return redirect('carts:checkout.html')



    def format_phone_number(self, phone):
        phone = phone.replace("+", "").replace(" ", "")
        if re.match(r"^254\d{9}$", phone):
            return phone
        elif phone.startswith("0") and len(phone) == 10:
            return "254" + phone[1:]
        raise ValueError("Invalid phone number format. Use 2547XXXXXXXX or 07XXXXXXXX")


    def generate_access_token(self):
        try:
            credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/json",
            }

            response = requests.get(
                f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
                headers=headers,
                timeout=30
            ).json()

            if "access_token" in response:
                return response['access_token']
            raise Exception("Access token missing in response")
        except Exception as e:
            raise Exception(f"Failed to get access token: {str(e)}")


    def initiate_stk_push(self, phone, amount):
        try:
            token = self.generate_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            stk_password = base64.b64encode(
                (MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode()
            ).decode()


            payload = {
                "BusinessShortCode": MPESA_SHORTCODE,
                "Password": stk_password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone,
                "PartyB": MPESA_SHORTCODE,
                "PhoneNumber": phone,
                "CallBackURL": CALLBACK_URL,
                "AccountReference": "Farm2Market",
                "TransactionDesc": "Payment for goods"
            }
            response = requests.post(
                f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"STK Push failed: {str(e)}")


@csrf_exempt
def mpesa_callback(request):
        if request.method != "POST":
            return HttpResponseBadRequest("Only POST requests are allowed")


        try:
            callback_data = json.loads(request.body)
            result_code = callback_data["Body"]["stkCallback"]["ResultCode"]
            checkout_request_id = callback_data["Body"]["stkCallback"]["CheckoutRequestID"]
            if result_code == 0:
                # Successful payment
                metadata = callback_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
                amount = next(item["Value"] for item in metadata if item["Name"] == "Amount")
                receipt = next(item["Value"] for item in metadata if item["Name"] == "MpesaReceiptNumber")
                phone = next(item["Value"] for item in metadata if item["Name"] == "PhoneNumber")

                Transaction.objects.filter(
                    checkout_request_id=checkout_request_id
                ).update(
                    mpesa_code=receipt,
                    status='completed',
                    phone=phone,
                    amount=amount
                )
            # Here you would typically create an order as well
            else:
                # Failed payment
                Transaction.objects.filter(
                    checkout_request_id=checkout_request_id
                ).update(
                    status='failed',
                    error_message=callback_data["Body"]["stkCallback"]["ResultDesc"]
                )
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})
        except Exception as e:
            return JsonResponse({"ResultCode": 1, "ResultDesc": str(e)})


class PaymentStatusView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            checkout_id = data.get('checkout_request_id')


            if not checkout_id:
                return JsonResponse({'error': 'Missing checkout ID'}, status=400)

            transaction = Transaction.objects.get(
                checkout_request_id=checkout_id,
                user=request.user
            )
            return JsonResponse({
                'status': transaction.status,
                'message': transaction.error_message or '',
                'mpesa_code': transaction.mpesa_code or ''
            })
        except Transaction.DoesNotExist:
            return JsonResponse({'error': 'Transaction not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
