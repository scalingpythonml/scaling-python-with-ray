import ray
from ray import serve
import requests
import os
import pickle
import numpy as np

# Models locations
XGBOOST_MODEL_PATH = os.path.join("wine-quality_xgboost.pkl")

# Start Ray
ray.init()

# Start Serve
serve.start()
#define deployment
@serve.deployment(route_prefix="/xgboost")
class XGBoostModel:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.model = pickle.load(f)

    async def __call__(self, request):
        payload = await request.json()
        return self.serve(payload)

    def serve(self, request):
        input_vector = np.array([
            request["fixed acidity"],
            request["volatile acidity"],
            request["citric acid"],
            request["residual sugar"],
            request["chlorides"],
            request["free sulfur dioxide"],
            request["total sulfur dioxide"],
            request["density"],
            request["pH"],
            request["sulphates"],
            request["alcohol"],
        ])
        prediction = self.model.predict(input_vector.reshape(1,11))[0]
        return {"result": str(prediction)}

XGBoostModel.deploy(XGBOOST_MODEL_PATH)
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

print(requests.get("http://localhost:8000/xgboost", json=sample_request_input).text)
