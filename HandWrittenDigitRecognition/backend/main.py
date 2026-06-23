from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model # type: ignore
from PIL import Image
import numpy as np
import io

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = load_model("handwritten_digit_model.keras")


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    contents = await file.read()

    img = Image.open(
        io.BytesIO(contents)
    ).convert("L")

    #img.save("img1.png")
    
    img = img.resize((28,28))

    img = np.array(img)
    
    #Image.fromarray((img * 255).astype(np.uint8)).save("img2.png")

    img = img.reshape(
        1,
        28,
        28,
        1
    )

    prediction = model.predict(img)

    digit = int(np.argmax(prediction))

    confidence = float(np.max(prediction))

    return {
        "digit": digit,
        "confidence": confidence
    }