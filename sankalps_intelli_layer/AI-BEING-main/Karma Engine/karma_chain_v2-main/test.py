import requests

resp = requests.get(
    "https://api.heygen.com/v2/avatars",
    headers={"x-api-key": "sk_V2_hgu_kAcLT379oy9_oBYDEJ69x7wOIuyqunynz4HbI3LrWYTN"}
)
print(resp.json())
