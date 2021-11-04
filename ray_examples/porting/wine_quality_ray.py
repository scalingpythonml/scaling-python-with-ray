import pandas as pd
import ray
import time

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
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

# Start Ray
ray.init()

X_train_handle = ray.put(X_train)
X_test_handle = ray.put(X_test)
Y_train_handle = ray.put(y_train)
Y_test_handle = ray.put(y_test)

# Decision tree
@ray.remote
def dt_function(X_train: pd.Series, X_test: pd.Series, y_train: pd.Series) -> pd.Series:
    from sklearn.tree import DecisionTreeClassifier

    param_model = {'max_depth':range(10, 20),
                      'max_features': range(3,11)}
#    model = GridSearchCV(DecisionTreeClassifier(random_state=1),
#                         param_grid=param_model,
#                         scoring='accuracy',
#                         n_jobs=-1)
    model = DecisionTreeClassifier(random_state=1)

    print(f'model created')
    model = model.fit(X_train, y_train)
    print(f'Done fitting')
    y_predict = model.predict(X_test)
    print(f'Done predicting')
    return y_predict

# Random forest
@ray.remote
def rf_function(X_train: pd.Series, X_test: pd.Series, y_train: pd.Series) -> pd.Series:
    from sklearn.ensemble import RandomForestClassifier
    param_model = {'n_estimators': [25, 50, 100, 150, 200, 250, 300, 350]}
    print(f'Params done')
    model = GridSearchCV(RandomForestClassifier(oob_score=True, random_state=1, warm_start=True, n_jobs=-1),
                          param_grid=param_model,
                          scoring='accuracy',
                          n_jobs=-1)

    print(f'Model created')
    model = model.fit(X_train, y_train)
    print(f'Model fitted')
    y_predict = model.predict(X_test)
    print(f'Done predicting {y_predict.head(1)}')
    return y_predict

# ada boost
@ray.remote
def ab_function(X_train: pd.Series, X_test: pd.Series, y_train: pd.Series) -> pd.Series:
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import AdaBoostClassifier
    param_model = {'n_estimators': [50, 100, 150, 200, 250, 300],
                    'learning_rate': [0.5, 1.0, 2.0]}
    print(f'Params done')
    model = GridSearchCV(AdaBoostClassifier(DecisionTreeClassifier(max_depth=1, random_state=1)),
                          param_grid=param_model,
                          scoring='accuracy',
                          n_jobs=-1)

    print(f'Model created')
    model = model.fit(X_train, y_train)
    print(f'Model fitted')
    y_predict = model.predict(X_test)
    print(f'Done predicting {y_predict.head(1)}')
    return y_predict

#gradient boost
@ray.remote
def gb_function(X_train: pd.Series, X_test: pd.Series, y_train: pd.Series) -> pd.Series:
    from sklearn.ensemble import GradientBoostingClassifier
    param_model = {'n_estimators': [150, 200, 250, 300, 350],
                    'learning_rate': [0.05, 0.1, 0.2]}
    print(f'Params done')
    model = GridSearchCV(GradientBoostingClassifier(random_state=1),
                          param_grid=param_model,
                          scoring='accuracy',
                          n_jobs=-1)

    print(f'Model created')
    model = model.fit(X_train, y_train)
    print(f'Model fitted')
    y_predict = model.predict(X_test)
    print(f'Done predicting {y_predict.head(1)}')
    return y_predict

# Support Vector Classifier
@ray.remote
def svm_function(X_train: pd.Series, X_test: pd.Series, y_train: pd.Series) -> pd.Series:
    from sklearn.svm import SVC
    param_model = {'C': [0.1, 1, 10, 50, 100, 250, 500, 1000],
                  'gamma': [1, 0.5, 0.25, 0.1, 0.01, 0.001, 0.0001],
                  'kernel': ['rbf', 'sigmoid']}

    print(f'Params done')
    model = GridSearchCV(SVC(),
                        param_model,
                        scoring='accuracy',
                        n_jobs=-1)
    print(f'Model created')
    model = model.fit(X_train, y_train)
    print(f'Model fitted')
    y_predict = model.predict(X_test)
    print(f'Done predicting {y_predict.head(1)}')
    return y_predict

start = time.time()

dt_handle = dt_function.remote(X_train_handle, X_test_handle, Y_train_handle)
#rf_handle = rf_function.remote(X_train_handle, X_test_handle, Y_train_handle)
#ab_handle = ab_function.remote(X_train_handle, X_test_handle, Y_train_handle)
#gb_handle = gb_function.remote(X_train_handle, X_test_handle, Y_train_handle)
#svm_handle = svm_function.remote(X_train_handle, X_test_handle, Y_train_handle)

#y_pred_dt, y_pred_rf, y_pred_ab, y_pred_gb, y_pred_svm = \
#    ray.get([dt_handle, rf_handle, ab_handle, gb_handle, svm_handle])
y_pred_dt = ray.get(dt_handle)

print("Decision Trees")
print(classification_report(y_test, y_pred_dt))
#print("Random Forest")
#print(classification_report(y_test, y_pred_rf))
#print("Ada boost")
#print(classification_report(y_test, y_pred_ab))
#print("Gradient Boost")
#print(classification_report(y_test, y_pred_gb))
#print("Support Vector Classifier")
#print(classification_report(y_test, y_pred_svm))

print(f"executed in {time.time() - start} ")
