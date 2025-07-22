import os, base64, requests, re, json

from django.shortcuts import render
from dotenv import load_dotenv
from datetime import datetime
from django.http import JsonResponse, HttpResponseBadRequest
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

def generate_access_token():
    """
    Get an access token for M-pesa APIs.

    Make a GET request to the token endpoint and return the access token
    obtained from the response.

    Raises:
        Exception: If the request fails or if the response does not contain
            an access token.
    """
    try:
        credentials = f'{CONSUMER_KEY}:{CONSUMER_SECRET}'
        encoded_credentials = base64.b64encoded(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }
        response = requests.get(
            f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
            headers=headers,
        ).json()

        if "access_token" in response:
            return response['access_token']
        else:
            raise Exception('Access toekn missing in response')
    except requests.RequestException as e:
        raise Exception(f"Failed to connect to M-pesa: {str(e)}")


def initiate_stk_push(phone, amount):
    try:
        token = generate_access_token
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        stk_password = base64.b64encode(
            ((MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode())
        ).decode()

        request_body = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": stk_password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillonline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": CALLBACK_URL,
            "AccountReference": "account",
            "TransactionDesc": "Payment for goods",
        }

        response = requests.post(
            f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest",
            json=request_body,
            headers=headers,
        ).json()

        return response
    except Exception as e:
        print(f"Failed to initiate STK Push: {str(e)}")
        return e


def format_phone_number(phone):
    phone = phone.replace("+", "")
    if re.match(r"^254\d{9}$", phone):
        return phone
    elif phone.startswith("0") and len(phone) == 10:
        return "254" + phone[1:]
    else:
        raise ValueError("Invalid phone number format")


def payment_view(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                # Get cart total
                cart = Cart.objects.get(user=request.user)
                total_amount = cart.get_total()

                # Format phone number
                phone = format_phone_number(form.cleaned_data['phone_number'])

                # Call STK push
                response = initiate_stk_push(phone, int(total_amount))

                if response.get("ResponseCode") == "0":
                    checkout_request_id = response["CheckoutRequestID"]
                    return render(request, 'mpesa/pending.html', {"checkout_request_id": checkout_request_id})
                else:
                    error_message = response.get("errorMessage", "Failed to send STK push. Please try again.")
                    return render(request, "mpesa/payment_form", {"form": form, "errorMessage": error_message})
            except Cart.DoesNotExist:
                return render(request, "mpesa/payment_form", {"form": form, "errorMessage": "Cart not found."})
    else:
        form = PaymentForm()
    return render(request, "mpesa/payment_form", {"form": form})


@csrf_exempt
def mpesa_callback(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST request are allowed")
    try:
        # parse the callback dat from the request body
        callback_data = json.loads(request.body)
        # check the result code
        result_code = callback_data["Body"]["stkCallback"]["ResultCode"]
        if result_code != 0:
            # Handle unsuccefull transaction
            error_message = callback_data["Body"]["stkCallback"]["ResultCode"]
            return JsonResponse({"ResultCode": result_code, "ResultDesc": error_message})
        # Extract metadata from the callback
        checkout_id = callback_data["Body"]["stkCallback"]["CheckoutRequestID"]
        body = callback_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
        # Find specific fields in the metadata
        amount = next(item["Value"] for item in body if item["Name"] == "Amount")
        mpesa_code = next(item["Value"] for item in body if item["Name"] == "MpesaReceiptNumber")
        phone = next(item["Value"] for item in body if item["Name"] == "PhoneNumber")

        # save transaction to the database
        Transaction.objects.create(
            amount=amount,
            checkout_id=checkout_id,
            mpesa_code=mpesa_code,
            status="Success"

        )
        # return a success response to mpesa
        return JsonResponse("success", safe=False)
    except (json.JSONDecodeError, KeyError) as e:
        # handle errors gracefully
        return HttpResponseBadRequest(f"Invalid request data: {str(e)}")


def query_stk_push(checkout_request_id):
    try:
        token = generate_access_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            ((MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode())
        ).decode()
        request_body = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequstID": checkout_request_id
        }
        response = requests.post(
            f"{MPESA_BASE_URL}/mpesa/stkpushquery/v1/query",
            json=request_body,
            headers=headers
        )
        print(response.json())
        return response.json()
    except requests.RequestException as e:
        print(f"Error querying STK status: {str(e)}")
        return {"error": str(e)}


def stk_status_view(request):
    if request.method == 'POST':
        try:
            # parse the JSON body
            data = json.loads(request.body)
            checkout_request_id = data.get('checkout_request_id')

            # Query the STK push status using your backend function
            status = query_stk_push(checkout_request_id)

            # Return the status as a JSON response
            return JsonResponse({"status": status})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)