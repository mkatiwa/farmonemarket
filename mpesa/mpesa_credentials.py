import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64

import requests
import json
from requests.auth import HTTPBasicAuth
from .keys import MpesaC2bCredential  # or wherever your credentials are

class MpesaAccessToken:
    @staticmethod
    def get_token():
        r = requests.get(
            MpesaC2bCredential.api_URL,
            auth=HTTPBasicAuth(
                MpesaC2bCredential.consumer_key,
                MpesaC2bCredential.consumer_secret
            )
        )
        mpesa_access_token = json.loads(r.text)
        return mpesa_access_token['access_token']

    import base64
    from datetime import datetime

    class LipanaMpesaPpassword:
        business_short_code = "123456"
        passkey = "abcde12345"

        @classmethod
        def generate_password(cls):
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            data_to_encode = cls.business_short_code + cls.passkey + timestamp
            encoded = base64.b64encode(data_to_encode.encode())
            return encoded.decode('utf-8'), timestamp

# class MpesaC2bCredential:
#     consumer_key = 'LZr2F2P8GKUlqk2ZIacGcq71sIOv6VK1nuWnmVyepwqQO6Ps'
#     consumer_secret = 'OO8UpIn97GMr5X32Z1dIvXknYqOFJbUN6kDJfviIjL1Cmj4EADbvbKEINyd2BFgq'
#     api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
#
#
# class MpesaAccessToken:
#     r = requests.get(MpesaC2bCredential.api_URL,
#                      auth=HTTPBasicAuth(MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret))
#     mpesa_access_token = json.loads(r.text)
#     validated_mpesa_access_token = mpesa_access_token['access_token']
#
#
# class LipanaMpesaPpassword:
#     lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
#     Business_short_code = "174379"
#     Test_c2b_shortcode = "600344"
#     passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
#
#     data_to_encode = Business_short_code + passkey + lipa_time
#
#     online_password = base64.b64encode(data_to_encode.encode())
#     decode_password = online_password.decode('utf-8')
