
import pandas as pd
import numpy as np
from sklearn import preprocessing 
from scipy import sparse
from sklearn import model_selection 
from sklearn import metrics
import xgboost as xgb
import multiprocessing


d = pd.read_csv("../data/airline100K.csv")

vars_cat = ["Month","DayofMonth","DayOfWeek","UniqueCarrier", "Origin", "Dest"]
vars_num = ["DepTime","Distance"]
for col in vars_cat:
  d[col] = preprocessing.LabelEncoder().fit_transform(d[col])
  
X_cat = preprocessing.OneHotEncoder().fit_transform(d[vars_cat])     # sparse mx   (less RAM, but also XGB runs 30x faster)
X = sparse.hstack((X_cat, d[vars_num]))                              # sparse mx
      
y = np.where(d["dep_delayed_15min"]=="Y",1,0)                        # numpy array


X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.1, random_state=123)



## Method 1 - sklearn API

## TRAIN
md = xgb.XGBClassifier(max_depth=10, n_estimators=100, learning_rate=0.1, n_jobs=-1)
%time md.fit(X_train, y_train)

## %time md.fit(X_train.toarray(), y_train)   # slow if not sparse!


## SCORE
y_pred = md.predict_proba(X_test)[:,1]

metrics.confusion_matrix(y_test, y_pred>0.5)
metrics.roc_auc_score(y_test, y_pred)



## Method 2 - orig xgboost API

dxgb_train = xgb.DMatrix(X_train, label = y_train)
dxgb_test = xgb.DMatrix(X_test)


## TRAIN
param = {'max_depth':10, 'eta':0.1, 'objective':'binary:logistic', 
             'silent':1, 'nthread': multiprocessing.cpu_count()}
%time md = xgb.train(param, dxgb_train, num_boost_round = 100)

## SCORE
y_pred = md.predict(dxgb_test)   

metrics.confusion_matrix(y_test, y_pred>0.5)
metrics.roc_auc_score(y_test, y_pred)


## try playing with the hyperparams e.g. max_depth = 2,5,10,15; learning_rate=0.01,0.03,0.1;
## n_estimators = 100,300,1000; check out further params in the docs
## (re-run from "TRAIN" part above)


