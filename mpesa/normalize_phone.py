def normalize_phone(phone):
    if phone.startswith("07"):
        return "254" + phone[1:]
    elif phone.startswith("+254"):
        return phone[1:]
    elif phone.startswith("254"):
        return phone
    else:
        return phone
