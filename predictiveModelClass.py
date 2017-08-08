# %load ../codes/predictiveModelClass.py
class PredictiveModelByilding(object):
  """docstring for PredictiveModelByilding
this class will handle all pipeline for a preeictive modèle building 
in the chapter of my machine learning project ,
it will train differents modele, encode data,scale data, and so on
  """
  def __init__(self,dataset,encoderFunction):
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import cross_val_score
    from sklearn.model_selection import StratifiedShuffleSplit
    from sklearn.svm import LinearSVR
    from sklearn.svm import SVR
    from sklearn.metrics import mean_squared_error
    if isinstance(dataset,pd.DataFrame):
      self.dataset=dataset
      self.training_set=pd.DataFrame()
      self.test_set=pd.DataFrame()
      self.predictiveModels={}
      self.X_train=pd.DataFrame()
      self.X_test=pd.DataFrame()
      self.Y_train=pd.Series()
      self.Y_test=pd.Series()
      self.dataset_bin=encoderFunction(dataset,catCol=['SCHOOL_RIGHT', 'OPTION_RIGHT'],numCol=['DIPPERC','CGPA','EchecRatio'])
      self.dataset_bin.reset_index(inplace=True)
      ### init all models
      ridge_reg=Ridge(alpha=1, solver="cholesky")
      linSVM_reg=LinearSVR(dual=False,fit_intercept=False,loss='squared_epsilon_insensitive' )
      rbfSVM_reg=SVR(verbose=True)
      self.predictiveModels['Ridge']=ridge_reg
      self.predictiveModels['LinearSVR']=linSVM_reg
      self.predictiveModels['RbfSVR']=rbfSVM_reg
    else:
      raise TypeError('need only a DataFrame')
  def scale(self,numCols):

    """this function will scale the values of GPA and DIP percentage by divide them by 100"""
    self.dataset.loc[:,numCols[0]] = dataset[numCols[0]]/100
    self.dataset.loc[:,numCols[1]] = dataset[numCols[1]]/100
  def split(self):
    """the function will split the dataset into a train and a test one" and return X_Train and X_Test"""
    split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    for train_index, test_index in split.split(self.dataset_bin, self.dataset_bin.EchecRatio):
      dataset_Train_bin=self.dataset_bin.loc[train_index]
      dataset_Test_bin=self.dataset_bin.loc[test_index]
      dataset_Train_bin.set_index(keys='ID',inplace=True)
      dataset_Test_bin.set_index(keys='ID',inplace=True)
    self.Y_Train=dataset_Train_bin.CGPA
    self.X_Train=dataset_Train_bin.drop(labels=['CGPA','EchecRatio'],axis=1)
    self.Y_Test=dataset_Test_bin.CGPA
    self.X_Test=dataset_Test_bin.drop(labels=['CGPA','EchecRatio'],axis=1)  
    return dataset_Train_bin.describe()[['DIPPERC','CGPA']],dataset_Test_bin.describe()[['DIPPERC','CGPA']]
  def train(self):
    """will train diverents models with X , Y pass in parametes"""
    predictions={}
    for clf in self.predictiveModels.values:
      clf.fit(self.X_Train, self.Y_Train)
      predictions[clf.__class__.__name__]= clf.predict(self.X_Train)
    predictedVal=pd.DataFrame.from_dict(predictions,dtype=np.float)
    predictedVal.set_index(self.Y_Train.index,inplace=True)
    predictedVal.loc[:,'RealValue']=self.Y_Train
    return predictedVal
  def evaluate (self,model):
    """ this function will first do a evaluation of a mdels and return the RMSE score of it and some datat and their labesl
    """
    some_data = self.X_Train.iloc[:5]
    some_labels = self.Y_Train.iloc[:5]
    print("Predictions:\t", models.predict(some_data))
    print("Labels:\t\t", list(some_labels))
    CGPA_predictions = self.predictiveModels[model].predict(self.X_Train)
    lin_mse = mean_squared_error(self.Y_Train , CGPA_predictions)
    lin_rmse=np.sqrt(lin_mse)
    return lin_rmse
  def crossEvaluate(self,model):
    """this one will perfom a cross validation of the model"""
    scores = cross_val_score(self.predictiveModels[model], self.X_Train, self.Y_Train,scoring="neg_mean_squared_error", cv=10)
    rmse_scores = np.sqrt(-scores)
    return rmse_scores,rmse_scores.std(),rmse_scores.mean()

