import requests


url = "http://127.0.0.1:8000/accounts/login/"

data = {
    "email": "mawia@gmail.com",
    "password": "admin1234"
}

res =requests.post(url, data)

print(res.status_code)