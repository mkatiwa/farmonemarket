# import base64, os
# from datetime import datetime
# from .normalize_phone import normalize_phone
# from django.contrib.sites import requests
# from django.shortcuts import render
# from dotenv import load_dotenv
# load_dotenv()
# CONSUMER_KEY = os.getenv('CONSUMER_KEY')
# CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
# MPESA_PASSKEY = os.getenv('MPESA_PASSKEY')
# MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE')
# CALLBACK_URL = os.getenv('CALLBACK_URL')
# MPESA_BASE_URL = os.getenv('MPESA_BASE_URL')
#
# # Create your views here.
# def generate_access_token():
#     try:
#         credentials = f'{CONSUMER_KEY}:{CONSUMER_SECRET}'
#         encoded_credentials = base64.b64encode(credentials.encode()).decode()
#         headers = {
#             'Authorization': f'Basic {encoded_credentials}',
#             'Content-Type': 'application/json',
#         }
#         response = requests.get(
#             f'{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials',
#             headers = headers,
#         ).json()
#         if 'access_token' in response:
#             return response['access_token']
#         else:
#             raise Exception('access token missing')
#
#     except requests.RequestException as e:
#         raise Exception(f'Failed to connect to mpesa: {str(e)}')
#
# def initiate_stk_push():
#     user = request.user
#     phone = normalize_phone(user.phone_number)
#     try:
#         token = generate_access_token()
#         headers = {
#             'Authorization': f'Bearer {token}',
#             'Content-Type': 'application/json',
#         }
#         timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#         stk_password = base64.b64encode((MPESA_PASSKEY+MPESA_SHORTCODE+timestamp).encode()).decode()
#
#         request_body = {
#             'BussinessShortCode': MPESA_SHORTCODE,
#             'Password': stk_password,
#             'Timestamp': timestamp,
#             'TransactionType': 'CustomerPayBillonline',
#             'Amount': 100,
#             'PartyA': 1,
#             'PartyB': MPESA_SHORTCODE,
#             'PhoneNumber': phone,
#             'CallBackURL': CALLBACK_URL,
#             'AccountReference': 'account',
#             'TransactionDesc': 'Pay for goods',
#
#         }
#         response = requests.post(
#             f'{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest',
#             json=request_body,
#             headers=headers,
#         ).json()
#         return response
#
#     except Exception as e:
#         print(f'failed to initiate stkpush: {str(e)}')
#         return e
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
import requests
from django.shortcuts import redirect
from requests import Response
from requests.auth import HTTPBasicAuth
import json
import logging
from Farm2Market import settings
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.views.decorators.csrf import csrf_exempt
from .models import MpesaPayment

@csrf_exempt
def stk_push(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')

        access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        stk_push_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

        consumer_key = settings.MPESA_CONSUMER_KEY
        consumer_secret = settings.MPESA_CONSUMER_SECRET
        shortcode = settings.MPESA_SHORTCODE
        passkey = settings.MPESA_PASSKEY
        callback_url = settings.MPESA_CALLBACK_URL


def getAccessToken(request):
    consumer_key = 'LZr2F2P8GKUlqk2ZIacGcq71sIOv6VK1nuWnmVyepwqQO6Ps'
    consumer_secret = 'OO8UpIn97GMr5X32Z1dIvXknYqOFJbUN6kDJfviIjL1Cmj4EADbvbKEINyd2BFgq'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']

    return HttpResponse(validated_mpesa_access_token)


def lipa_na_mpesa_online(request, stk_push_url):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    request_body = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": 254792281262,  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": 254792281262,  # replace with your phone number to get stk push
        "CallBackURL": "https://fa20-41-186-110-41.ngrok-free.app -> http://localhost:8000",
        "AccountReference": "Henry",
        "TransactionDesc": "Testing stk push"
    }
    response :Response = requests.post(stk_push_url, json=request_body, headers=headers)

    if response.status_code == 200:
        messages.success(request, 'STK Push sent. Check your phone to complete payment.')
    else:
        try:
            error_response = response.json()
        except ValueError:
            error_response = response.text

        messages.error(request, f"Payment failed: {error_response}")

    return redirect('checkout')  # Replace with the actual name of your checkout view

    #
    # return HttpResponse("Invalid request", status=400)
    # response = requests.post(api_url, json=request, headers=headers)
    # return HttpResponse('success')

logger = logging.getLogger(__name__)

@csrf_exempt
def mpesa_callback(request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            logger.info("M-Pesa Callback Data: %s", json.dumps(data, indent=2))

            result = data.get('Body', {}).get('stkCallback', {})

            merchant_request_id = result.get('MerchantRequestID')
            checkout_request_id = result.get('CheckoutRequestID')
            result_code = result.get('ResultCode')
            result_desc = result.get('ResultDesc')

            if result_code == 0:
                # Payment was successful
                metadata = result.get('CallbackMetadata', {}).get('Item', [])
                mpesa_data = {}
                for item in metadata:
                    name = item.get('Name')
                    value = item.get('Value', '')
                    mpesa_data[name] = value

                MpesaPayment.objects.create(
                    merchant_request_id=merchant_request_id,
                    checkout_request_id=checkout_request_id,
                    phone_number=mpesa_data.get('PhoneNumber'),
                    amount=mpesa_data.get('Amount'),
                    mpesa_receipt_number=mpesa_data.get('MpesaReceiptNumber'),
                    transaction_date=mpesa_data.get('TransactionDate'),
                    status='Completed',
                )
            else:
                # Payment failed or was cancelled
                MpesaPayment.objects.create(
                    merchant_request_id=merchant_request_id,
                    checkout_request_id=checkout_request_id,
                    status='Failed',
                    result_desc=result_desc
                )

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Callback received successfully"})

        except Exception as e:
            logger.error(f"M-Pesa Callback Error: {str(e)}")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Callback processing error"}, status=500)


@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               "ConfirmationURL": "https://79372821.ngrok.io/api/v1/c2b/confirmation",
               "ValidationURL": "https://79372821.ngrok.io/api/v1/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)

    return HttpResponse(response.text)


@csrf_exempt
def call_back(request):
    pass


@csrf_exempt
def validation(request):

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    mpesa_body =request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)

    payment = MpesaPayment(
        first_name=mpesa_payment['FirstName'],
        last_name=mpesa_payment['LastName'],
        middle_name=mpesa_payment['MiddleName'],
        description=mpesa_payment['TransID'],
        phone_number=mpesa_payment['MSISDN'],
        amount=mpesa_payment['TransAmount'],
        reference=mpesa_payment['BillRefNumber'],
        organization_balance=mpesa_payment['OrgAccountBalance'],
        type=mpesa_payment['TransactionType'],

    )
    payment.save()

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }

    return JsonResponse(dict(context))

