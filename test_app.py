import base64
import requests

from io import BytesIO
from PIL import Image

newIm = Image.open('data/dni_random.jpg')
buffered = BytesIO()
newIm.save(buffered, format="png")

url = 'http://127.0.0.1:1080/crop'  # localhost and the defined port + endpoint
body = {
    "imageData": base64.b64encode(buffered.getvalue()).decode('utf-8')
}
response = requests.post(url, data=body)
base64_image = response.json()['dni_image']
img = Image.open(BytesIO(base64.b64decode(base64_image)))
img.save('data/image_after_endpoint.jpg')
print('Succesfully send and receive an image to flask endpoint')