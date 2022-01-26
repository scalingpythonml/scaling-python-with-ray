# based on https://docs.ray.io/en/latest/tune/tutorials/tune-sklearn.html

import pandas as pd
import time

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from ray.tune.sklearn import TuneGridSearchCV
from sklearn.metrics import classification_report

import joblib
from ray.util.joblib import register_ray

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

# Decision tree
print('Decision trees')
from sklearn.tree import DecisionTreeClassifier

param_model = {'max_depth':range(10, 20),
                'max_features': range(3,11)}

start = time.time()
model = GridSearchCV(DecisionTreeClassifier(random_state=1),
                      param_grid=param_model,
                      scoring='accuracy',
                      n_jobs=-1)

model = model.fit(X_train, y_train)
print(f"executed GridSearchCV in {time.time() - start}, nodes {model.best_estimator_.tree_.node_count}, "
      f"max_depth {model.best_estimator_.tree_.max_depth}")

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

start = time.time()
model = GridSearchCV(DecisionTreeClassifier(random_state=1),
                     param_grid=param_model,
                     scoring='accuracy',
                     n_jobs=-1)

register_ray()
with joblib.parallel_backend('ray'):
    model = model.fit(X_train, y_train)
print(f"executed GridSearchCV with joblib in {time.time() - start}, nodes {model.best_estimator_.tree_.node_count}, "
      f"max_depth {model.best_estimator_.tree_.max_depth}")

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

start = time.time()
model = TuneGridSearchCV(DecisionTreeClassifier(random_state=1),
                          param_grid=param_model,
                          scoring='accuracy')

model = model.fit(X_train, y_train)
print(f"executed TuneGridSearchCV in {time.time() - start}, nodes {model.best_estimator_.tree_.node_count}, "
      f"max_depth {model.best_estimator_.tree_.max_depth}")

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
