# based on https://docs.ray.io/en/latest/tune/tutorials/tune-sklearn.html

import pandas as pd
import time

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

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
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.25, random_state=0)

print('XGBoost')
import xgboost as xgb

start = time.time()
model = xgb.XGBClassifier(random_state=1)
model.fit(X_train, y_train)
print(f"executed XGBoost in {time.time() - start}")
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

print('Ray XGBoost')
from xgboost_ray import RayXGBClassifier

start = time.time()
model = RayXGBClassifier(
    n_jobs=10,  # In XGBoost-Ray, n_jobs sets the number of actors
    random_state=1
)
model.fit(X_train, y_train)
print(f"executed Ray XGBoost in {time.time() - start}")
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

print('light GBM')
# see https://www.analyticsvidhya.com/blog/2017/06/which-algorithm-takes-the-crown-light-gbm-vs-xgboost/
import lightgbm as lgb

train_data = lgb.Dataset(X_train,label=y_train)
param = {'num_leaves':150, 'objective':'binary','learning_rate':.05,'max_bin':200}
param['metric'] = ['auc', 'binary_logloss']
start = time.time()
model = lgb.train(param,train_data,100)
print(f"executed GBM in {time.time() - start}")
y_pred = model.predict(X_test)
#converting probabilities into 0 or 1
for i in range(len(y_pred)):
    if y_pred[i] >= .5:       # setting threshold to .5
        y_pred[i] = 1
    else:
        y_pred[i] = 0
print(classification_report(y_test, y_pred))

print('light GBM Ray')
# see https://docs.ray.io/en/master/lightgbm-ray.html#scikit-learn-api
from lightgbm_ray import RayLGBMClassifier

model = RayLGBMClassifier(
    n_jobs=4,  # In LightGBM-Ray, n_jobs sets the number of actors
    random_state=42)
start = time.time()
model.fit(X_train, y_train)
print(f"executed GBM on Ray in {time.time() - start}")
y_pred = model.predict(X_test)
#converting probabilities into 0 or 1
for i in range(len(y_pred)):
    if y_pred[i] >= .5:       # setting threshold to .5
        y_pred[i] = 1
    else:
        y_pred[i] = 0
print(classification_report(y_test, y_pred))
