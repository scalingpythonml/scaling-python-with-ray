import pandas as pd
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

# Decision tree
print('Decision trees')
from sklearn.tree import DecisionTreeClassifier

param_model1 = {'max_depth':range(10, 20),
                  'max_features': range(3,11)}

start = time.time()
model1 = GridSearchCV(DecisionTreeClassifier(random_state=1),
                      param_grid=param_model1,
                      scoring='accuracy',
                      n_jobs=-1)

model1 = model1.fit(X_train, y_train)
print(f"executed in {time.time() - start}, nodes {model1.best_estimator_.tree_.node_count}, "
      f"max_depth {model1.best_estimator_.tree_.max_depth}")

y_pred1 = model1.predict(X_test)
print(classification_report(y_test, y_pred1))

# Random forest
print('Random forest')
from sklearn.ensemble import RandomForestClassifier
param_model2 = {'n_estimators': [25, 50, 100, 150, 200, 250, 300, 350]}
start = time.time()
model2 = GridSearchCV(RandomForestClassifier(oob_score=True, random_state=1, warm_start=True, n_jobs=-1),
                      param_grid=param_model2,
                      scoring='accuracy',
                      n_jobs=-1)

model2 = model2.fit(X_train, y_train)
print(f"executed in {time.time() - start}, trees {len(model2.best_estimator_.estimators_)} ")
y_pred2 = model2.predict(X_test)
print(classification_report(y_test, y_pred2))

# ada boost
print('Ada boost')
from sklearn.ensemble import AdaBoostClassifier
param_model3 = {'n_estimators': [50, 100, 150, 200, 250, 300],
                'learning_rate': [0.5, 1.0, 2.0]}
start = time.time()
model3 = GridSearchCV(AdaBoostClassifier(DecisionTreeClassifier(max_depth=1, random_state=1)),
                      param_grid=param_model3,
                      scoring='accuracy',
                      n_jobs=-1)

model3 = model3.fit(X_train, y_train)
print(f"executed in {time.time() - start}, trees {len(model3.best_estimator_.estimators_)} learning rate {model3.best_estimator_.learning_rate} ")
y_pred3 = model3.predict(X_test)
print(classification_report(y_test, y_pred3))

#gradient boost
print('Gradient boost')
from sklearn.ensemble import GradientBoostingClassifier
param_model4 = {'n_estimators': [150, 200, 250, 300, 350],
                'learning_rate': [0.05, 0.1, 0.2]}
start = time.time()
model4 = GridSearchCV(GradientBoostingClassifier(random_state=1),
                      param_grid=param_model4,
                      scoring='accuracy',
                      n_jobs=-1)

model4 = model4.fit(X_train, y_train)
print(f"executed in {time.time() - start}, trees {len(model4.best_estimator_.estimators_)} learning rate {model4.best_estimator_.learning_rate} ")
y_pred4 = model4.predict(X_test)
print(classification_report(y_test, y_pred4))

# Support Vector Classifier
print('Support Vector Classifier')
from sklearn.svm import SVC
param_model5 = {'C': [0.1, 1, 10, 50, 100, 250, 500, 1000],
              'gamma': [1, 0.5, 0.25, 0.1, 0.01, 0.001, 0.0001],
              'kernel': ['rbf', 'sigmoid']}

start = time.time()
model5 = GridSearchCV(SVC(),
                    param_model5,
                    scoring='accuracy',
                    n_jobs=-1)
model5 = model5.fit(X_train, y_train)
print(f"executed in {time.time() - start} parameters {model5.best_estimator_}")
y_pred5 = model4.predict(X_test)
print(classification_report(y_test, y_pred5))
