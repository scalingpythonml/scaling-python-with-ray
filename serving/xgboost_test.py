import os
import pickle
import numpy as np


XGBOOST_MODEL_PATH = os.path.join("modelserving/wine-quality_xgboost.pkl")

with open(XGBOOST_MODEL_PATH, "rb") as f:
    model = pickle.load(f)

print(model)

input_vector = np.array([-0.87307788,  0.68255284, -1.28877135, -0.31132282, -0.20119924, -0.75308482,
                         -0.95690307, -0.93636416,  0.25195842, -0.22512806, -0.02157362])

iv1 = input_vector.reshape(1,11)

prediction = model.predict(input_vector.reshape(1,11))[0]

print(prediction)

