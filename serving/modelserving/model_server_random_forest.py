import ray
from ray import serve
import requests
import os
import pickle
import json

# Models locations
RANDOM_FOREST_MODEL_PATH = os.path.join("wine-quality_random_forest.pkl")
XGBOOST_MODEL_PATH = os.path.join("wine-quality_xgboost.pkl")

# Start Ray
ray.init()

# Start Serve
serve.start()
#define deployment
@serve.deployment(route_prefix="/winerandom")
class RandomForestModel:
    def __init__(self):
        with open(RANDOM_FOREST_MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)

    async def __call__(self, request):
        payload = await request.json()
        #print("Worker: received request with data", payload)
        input_vector = [
            payload["fixed acidity"],
            payload["volatile acidity"],
            payload["citric acid"],
            payload["residual sugar"],
            payload["chlorides"],
            payload["free sulfur dioxide"],
            payload["total sulfur dioxide"],
            payload["density"],
            payload["pH"],
            payload["sulphates"],
            payload["alcohol"],
        ]
        prediction = self.model.predict([input_vector])[0]
        return {"result": str(prediction)}



RandomForestModel.deploy()
# list current deploymente
print(serve.list_deployments())

sample_request_input = {
    "fixed acidity": -0.70071875,
    "volatile acidity": 0.34736425,
    "citric acid": -1.34012182,
    "residual sugar": -0.16942723,
    "chlorides": -0.1586918,
    "free sulfur dioxide":  1.06389977,
    "total sulfur dioxide": -0.10545198,
    "density": -0.66075704,
    "pH": 0.70550789,
    "sulphates": -0.46118037,
    "alcohol":  0.26002813,
}

response = requests.get("http://localhost:8000/winerandom", json=sample_request_input).text
result = json.loads(response)
print(result['result'])