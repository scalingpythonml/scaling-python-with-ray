import pandas as pd
import time

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from lightgbm_ray import RayLGBMClassifier

# Get data
df = pd.read_csv("winequality-red.csv", delimiter=";")
print(f"Rows, columns: {str(df.shape)}")
print(df.head)
print(df.isna().sum())

# Create Classification version of target variable
df['goodquality'] = [1 if x >= 6 else 0 for x in df['quality']]
X = df.drop(['quality','goodquality'], axis = 1)
y = df['goodquality']
print(df['goodquality'].value_counts())

# Normalize feature variables
X_features = X
X = StandardScaler().fit_transform(X)
# Splitting the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.25, random_state=0)

model = RayLGBMClassifier(
    n_jobs=4,               # In LightGBM-Ray, n_jobs sets the number of actors
    random_state=42)

start = time.time()
model.fit(X_train, y_train)
print(f"executed LightGBM in {time.time() - start}")
y_pred = model.predict(X_test)
#converting probabilities into 0 or 1
for i in range(len(y_pred)):
    if y_pred[i] >= .5:       # setting threshold to .5
        y_pred[i] = 1
    else:
        y_pred[i] = 0
print(classification_report(y_test, y_pred))