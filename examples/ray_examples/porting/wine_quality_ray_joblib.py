# based on https://docs.ray.io/en/latest/joblib.html

import pandas as pd
import time
import ray

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
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

ray.init()

# copy data to object store
X_train_handle = ray.put(X_train)
X_test_handle = ray.put(X_test)
Y_train_handle = ray.put(y_train)


# Decision tree
@ray.remote
def dt_function(X_train: pd.Series, X_test: pd.Series, y_train: pd.Series) -> pd.Series:

    from sklearn.tree import DecisionTreeClassifier

    param_model = {'max_depth':range(10, 20),
                    'max_features': range(3,11)}
    model = GridSearchCV(DecisionTreeClassifier(random_state=1),
                          param_grid=param_model,
                          scoring='accuracy',
                          n_jobs=-1)
    register_ray()
    with joblib.parallel_backend('ray'):
        model = model.fit(X_train, y_train)
    return model.predict(X_test)

# Random forest
@ray.remote
def rf_function(X_train: pd.Series, X_test: pd.Series, y_train: pd.Series) -> pd.Series:
    from sklearn.ensemble import RandomForestClassifier
    param_model = {'n_estimators': [25, 50, 100, 150, 200, 250, 300, 350]}
    model = GridSearchCV(RandomForestClassifier(oob_score=True, random_state=1, warm_start=True, n_jobs=-1),
                          param_grid=param_model,
                          scoring='accuracy',
                          n_jobs=-1)
    register_ray()
    with joblib.parallel_backend('ray'):
        model = model.fit(X_train, y_train)
    return model.predict(X_test)

# ada boost
@ray.remote
def ab_function(X_train: pd.Series, X_test: pd.Series, y_train: pd.Series) -> pd.Series:
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import AdaBoostClassifier
    param_model = {'n_estimators': [50, 100, 150, 200, 250, 300],
                   'learning_rate': [0.5, 1.0, 2.0]}
    model = GridSearchCV(AdaBoostClassifier(DecisionTreeClassifier(max_depth=1, random_state=1)),
                         param_grid=param_model,
                         scoring='accuracy',
                         n_jobs=1)

    register_ray()
    with joblib.parallel_backend('ray'):
        model = model.fit(X_train, y_train)
    return model.predict(X_test)

#gradient boost
@ray.remote
def gb_function(X_train: pd.Series, X_test: pd.Series, y_train: pd.Series) -> pd.Series:
    from sklearn.ensemble import GradientBoostingClassifier
    param_model = {'n_estimators': [150, 200, 250, 300, 350],
                   'learning_rate': [0.05, 0.1, 0.2]}
    model = GridSearchCV(GradientBoostingClassifier(random_state=1),
                         param_grid=param_model,
                         scoring='accuracy',
                         n_jobs=1)

    register_ray()
    with joblib.parallel_backend('ray'):
        model = model.fit(X_train, y_train)
    return model.predict(X_test)

# Support Vector Classifier
@ray.remote
def svm_function(X_train: pd.Series, X_test: pd.Series, y_train: pd.Series) -> pd.Series:
    from sklearn.svm import SVC
    param_model = {'C': [0.1, 1, 10, 50, 100, 250, 500, 1000],
                   'gamma': [1, 0.5, 0.25, 0.1, 0.01, 0.001, 0.0001],
                   'kernel': ['rbf', 'sigmoid']}

    model = GridSearchCV(SVC(),
                         param_model,
                         scoring='accuracy',
                         n_jobs=1)
    register_ray()
    with joblib.parallel_backend('ray'):
        model = model.fit(X_train, y_train)
    return model.predict(X_test)

# start execution
start = time.time()
dt_handle = dt_function.remote(X_train_handle, X_test_handle, Y_train_handle)
rf_handle = rf_function.remote(X_train_handle, X_test_handle, Y_train_handle)
ab_handle = ab_function.remote(X_train_handle, X_test_handle, Y_train_handle)
gb_handle = gb_function.remote(X_train_handle, X_test_handle, Y_train_handle)
svm_handle = svm_function.remote(X_train_handle, X_test_handle, Y_train_handle)

handles = {dt_handle : 'Decision Trees', rf_handle : 'Random Forest', ab_handle : 'Ada boost',
           gb_handle : 'Gradient Boost', svm_handle : 'SVM Classifier'}

ids = [dt_handle, rf_handle, ab_handle, gb_handle, svm_handle]

# get results
while len(ids) > 0:
    ready, not_ready = ray.wait(ids)
    for id in ready:
        print(f'completed function {handles[id]} in {time.time() - start}')
        print(classification_report(y_test,ray.get(id)))
    ids = not_ready

print(f"executed in {time.time() - start} ")
