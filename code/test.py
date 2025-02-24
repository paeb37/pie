from google.oauth2 import service_account
import vertexai
import os

# Initialize credentials
credentials = service_account.Credentials.from_service_account_file(
    os.path.join(os.pardir, 'gemini-key.json'),  # Use os.pardir to refer to the parent directory
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

# Configure Vertex AI
vertexai.init(
    project="test-451914",
    location="us-central1",
    credentials=credentials
)

# Use the Gemini client
from vertexai.preview.generative_models import GenerativeModel
model = GenerativeModel("gemini-pro")

query = '''
I am a Computer Science major looking to get a nontechnical job. 
Give me advice on how to do this.
'''

response = model.generate_content(query)

print(response.text)