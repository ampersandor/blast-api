import requests

# Define the URL
url = "http://localhost:5001/blast/"

# Define the file to be sent
file_path = "/Users/ampersandor/dev/github/ampersandor/blast-api/client/test_input01.fa"

# Prepare the query parameters
params = {"user_id": "AutoMSA", "outfmt": 7}

# Open the file in binary mode
with open(file_path, "rb") as f:
    # Prepare the files dictionary to send with the request
    files = {"file": f}

    # Send the GET request with the file as form data
    response = requests.get(url, params=params, files=files)

    # Print the response content
    if response.headers.get("Content-Type") == "application/json":
        print(response.json())
    else:
        print(response.content)
