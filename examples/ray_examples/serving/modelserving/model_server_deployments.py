import ray
from ray import serve
import requests
import os
import pickle
import numpy as np
import asyncio


# Models locations
RANDOM_FOREST_MODEL_PATH = os.path.join("wine-quality_random_forest.pkl")
XGBOOST_MODEL_PATH = os.path.join("wine-quality_xgboost.pkl")
GRBOOST_MODEL_PATH = os.path.join("wine-quality_grboost.pkl")

# Start Ray
ray.init()

# Start Serve
serve.start()
#define deployments
@serve.deployment(route_prefix="/randomforest")
class RandomForestModel:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.model = pickle.load(f)

    async def __call__(self, request):
        payload = await request.json()
        return self.serve(payload)

    def serve(self, request):
        input_vector = [
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
        ]
        prediction = self.model.predict([input_vector])[0]
        return {"result": str(prediction)}

@serve.deployment(route_prefix="/grboost")
class GRBoostModel:
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

RandomForestModel.deploy(RANDOM_FOREST_MODEL_PATH)
XGBoostModel.deploy(XGBOOST_MODEL_PATH)
GRBoostModel.deploy(GRBOOST_MODEL_PATH)

@serve.deployment(route_prefix="/speculative")
class Speculative:
    def __init__(self):
        self.rfhandle = RandomForestModel.get_handle(sync=False)
        self.xgboosthandle = XGBoostModel.get_handle(sync=False)
        self.grboosthandle = GRBoostModel.get_handle(sync=False)
    async def __call__(self, request):
        payload = await request.json()
        f1, f2, f3 = await asyncio.gather(self.rfhandle.serve.remote(payload),
                self.xgboosthandle.serve.remote(payload), self.grboosthandle.serve.remote(payload))

        rfresurlt = ray.get(f1)['result']
        xgresurlt = ray.get(f2)['result']
        grresult = ray.get(f3)['result']
        ones = []
        zeros = []
        if rfresurlt == "1":
            ones.append("Random forest")
        else:
            zeros.append("Random forest")
        if xgresurlt == "1":
            ones.append("XGBoost")
        else:
            zeros.append("XGBoost")
        if grresult == "1":
            ones.append("Gradient boost")
        else:
            zeros.append("Gradient boost")
        if len(ones) >= 2:
            return {"result": "1", "methods": ones}
        else:
            return {"result": "0", "methods": zeros}

Speculative.deploy()

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

print(requests.get("http://localhost:8000/randomforest", json=sample_request_input).text)
print(requests.get("http://localhost:8000/grboost", json=sample_request_input).text)
print(requests.get("http://localhost:8000/xgboost", json=sample_request_input).text)
print(requests.get("http://localhost:8000/speculative", json=sample_request_input).text)

