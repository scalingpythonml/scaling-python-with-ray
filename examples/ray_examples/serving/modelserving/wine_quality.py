import pandas as pd
import os

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
from sklearn.preprocessing import StandardScaler
X_features = X
X = StandardScaler().fit_transform(X)
# Splitting the data
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.25, random_state=0)

# Decision tree
print('Decision trees')
from sklearn.metrics import classification_report
from sklearn.tree import DecisionTreeClassifier

model1 = DecisionTreeClassifier(random_state=1)
model1.fit(X_train, y_train)
y_pred1 = model1.predict(X_test)
print(classification_report(y_test, y_pred1))

# Random forest
print('Random forest')
from sklearn.ensemble import RandomForestClassifier

model2 = RandomForestClassifier(oob_score=True, random_state=1, warm_start=True, n_jobs=-1)
model2.fit(X_train, y_train)
y_pred2 = model2.predict(X_test)
print(classification_report(y_test, y_pred2))


# ada boost
print('Ada boost')
from sklearn.ensemble import AdaBoostClassifier

model3 = AdaBoostClassifier(random_state=1)
model3.fit(X_train, y_train)
y_pred3 = model3.predict(X_test)
print(classification_report(y_test, y_pred3))


#gradient boost
print('Gradient boost')
from sklearn.ensemble import GradientBoostingClassifier

model4 = GradientBoostingClassifier(random_state=1)
model4.fit(X_train, y_train)
y_pred4 = model4.predict(X_test)
print(classification_report(y_test, y_pred4))

#XGBoost
print('XGBoost')
import xgboost as xgb

model5 = xgb.XGBClassifier(random_state=1)
model5.fit(X_train, y_train)
y_pred5 = model5.predict(X_test)
print(classification_report(y_test, y_pred5))

#save models - random forest, XGBoost and GRBoost
import pickle
RANDOM_FOREST_MODEL_PATH = os.path.join("wine-quality_random_forest.pkl")
XGBOOST_MODEL_PATH = os.path.join("wine-quality_xgboost.pkl")
GRBOOST_MODEL_PATH = os.path.join("wine-quality_grboost.pkl")
with open(RANDOM_FOREST_MODEL_PATH, "wb") as f:
    pickle.dump(model2, f)
with open(XGBOOST_MODEL_PATH, "wb") as f:
    pickle.dump(model5, f)
with open(GRBOOST_MODEL_PATH, "wb") as f:
    pickle.dump(model5, f)
