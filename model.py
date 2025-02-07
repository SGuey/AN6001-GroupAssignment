# Import pandas
import pandas as pd
import numpy as np

# Load dataset
cc_apps = pd.read_csv("crx.data.csv", header=None)

# Inspect data
cc_apps.head()

# Replace the '?'s with NaN
cc_apps = cc_apps.replace('?', np.nan)

# Iterate over each column of cc_apps
for col in cc_apps.columns:
    # Check if the column is of object type
    if cc_apps[col].dtypes == 'object':
        # Impute with the most frequent value
        cc_apps = cc_apps.fillna(cc_apps[col].value_counts().index[0])
    if cc_apps[col].dtypes == 'int':
        cc_apps = cc_apps.fillna(cc_apps[col].mean())

# Import LabelEncoder
from sklearn.preprocessing import LabelEncoder

# Instantiate LabelEncoder
le = LabelEncoder() 

# Iterate over all the values of each column and extract their dtypes
for col in cc_apps.columns.to_numpy():
    # Compare if the dtype is object
    if cc_apps[col].dtypes =='object':
    # Use LabelEncoder to do the numeric transformation
        cc_apps[col]=le.fit_transform(cc_apps[col])

# Import train_test_split
from sklearn.model_selection import train_test_split

# Drop the features 11 and 13 and convert the DataFrame to a NumPy array
cc_apps = cc_apps.drop([6, 11, 13], axis=1)

# Rename columns
cc_apps.columns = [
    "Male", "Age", "Debt", "Married", "BankCustomer", "EducationLevel",
    "YearsEmployed", "PriorDefault", "Employed",
    "CreditScore", "Citizen", "Income", "Approved"
]  # Removed DriversLicense and ZipCode

cc_apps["Age"] = cc_apps["Age"].astype(float) / 5

print(cc_apps.head())
print(cc_apps.describe())

cc_apps = cc_apps.to_numpy()

# Segregate features and labels into separate variables
X,y = cc_apps[:,0:12] , cc_apps[:,12]

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X,
                                y,
                                test_size=0.33,
                                random_state=42)

# Import MinMaxScaler
from sklearn.preprocessing import MinMaxScaler

# Instantiate MinMaxScaler and use it to rescale X_train and X_test
scaler = MinMaxScaler(feature_range=(0, 1))
rescaledX_train = scaler.fit_transform(X_train)
rescaledX_test = scaler.transform(X_test)

# Import LogisticRegression
from sklearn.linear_model import LogisticRegression

# Instantiate a LogisticRegression classifier with default parameter values
logreg = LogisticRegression()

# Fit logreg to the train set
logreg.fit(rescaledX_train, y_train)

# Import confusion_matrix
from sklearn.metrics import confusion_matrix

# Use logreg to predict instances from the test set and store it
y_pred = logreg.predict(rescaledX_test)

# Get the accuracy score of logreg model and print it
print("Accuracy of logistic regression classifier: ", logreg.score(rescaledX_test, y_test))

# Print the confusion matrix of the logreg model
print(confusion_matrix(y_test, y_pred))

import joblib
joblib.dump(logreg, "model.pkl")
joblib.dump(scaler, "scaler.pkl")