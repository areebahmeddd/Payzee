import requests
import json
import os

# URL of your API endpoint
url = "http://localhost:8000/api/v1/chatbot/"

# Path to your audio file
audio_file_path = r"C:\Users\areeb\Desktop\Payzee\kannada.mp3"

# User profile information - adjust as needed
user_profile = {
    "name": "User",
    "language": "kannada",
    "location": "Karnataka",
    "occupation": "farmer"
}

# Prepare the files and data for the request
files = {
    'file': (os.path.basename(audio_file_path), open(audio_file_path, 'rb'), 'audio/mpeg')
}
data = {
    'user_profile_json': json.dumps(user_profile)
}

# Send the request
response = requests.post(url, files=files, data=data)

# Save the response audio
if response.status_code == 200:
    with open('response.mp3', 'wb') as f:
        f.write(response.content)
    print("Response saved as response.mp3")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
