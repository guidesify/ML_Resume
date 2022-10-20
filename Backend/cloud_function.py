import os
import pickle
import numpy as np
from google.cloud import storage


## Gloabl model variable
model = None


# Download model file from cloud storage bucket
def download_model_file():

    from google.cloud import storage

    # Model Bucket details
    BUCKET_NAME        = "resume_model"
    PROJECT_ID         = "guidesify-opinion"
    GCS_MODEL_FILE     = ["stack.mgz", "vote.mgz"]

    # Initialise a client
    client   = storage.Client(PROJECT_ID)
    
    # Create a bucket object for our bucket
    bucket   = client.get_bucket(BUCKET_NAME)

    # Create directory to store model file
    folder = '/tmp/'
    if not os.path.exists(folder):
        os.makedirs(folder)

    for f in GCS_MODEL_FILE:
        # Create a blob object from the filepath
        blob     = bucket.blob(f)
        # Download the file to a destination
        blob.download_to_filename(folder + f)


# Main entry point for the cloud function
def resume_model(request):

    # Use the global model model 2 variable 
    global model, model2

    if not model:
        download_model_file()
        model = pickle.load(open("/tmp/stack.mgz", 'rb'))
        model2 = pickle.load(open("/tmp/vote.mgz", 'rb'))
    
    
    # Get the features sent for prediction
    params = request.get_json()

    if params is not None:
        if 'text' in params:
            prediction = model.predict_proba([params['text']])
            return {"predictions": prediction.tolist()}
        elif 'text2' in params:
            prediction = model2.predict([params['text2']])
            return {"predictions": prediction.tolist()}
        elif 'classes' in params:
            return {"classes": model.classes_.tolist()}
        
    else:
        return "nothing sent for prediction"
