import pandas as pd
import numpy as np
import glob, sys
from datetime import date
import pickle
from random import randint

from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor 
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

from sklearn.ensemble import RandomForestClassifier

from sklearn.tree import export_graphviz 
from sklearn.decomposition import PCA
from sklearn.metrics import recall_score

from scipy.stats import randint as sp_randint
import matplotlib.pyplot as plt

class Trainer():
	def __init__(self):
		self.load_data('data.pickle')
		self.drop_columns()
		self.split_train_test()

	def load_data(self, fileName):
		print "Loading %s" %fileName
		f = open(fileName, 'rb')
		self.loanData = pickle.load(f)

	def drop_columns(self):
		self.loanData = self.loanData.drop(['funded_amnt', 
								  'funded_amnt_inv', 
								  'addr_state', 
								  'total_pymnt',
								  'last_pymnt_month', 
								  'last_pymnt_year', 
								  'total_pymnt', 
								  'days_active'], 1)

	def split_train_test(self, test_size=0.2):

		features = self.loanData.drop(['loan_status'], 1).values
		targets = self.loanData['loan_status'].values
		self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(features, 
																	targets, 
																	test_size=test_size)
		self.X_train = self.X_train.astype(float)
		self.y_train = self.y_train.astype(float)
		self.X_test = self.X_test.astype(float)
		self.y_test = self.y_test.astype(float)

	def scale(self):
		self.scalerX = StandardScaler().fit(self.X_train)
		self.X_train, self.X_test = self.scalerX.transform(self.X_train), \
									self.scalerX.transform(self.X_test)

	def standardize_samples(self):
		##0 mean, unit variance
		self.X_train = preprocessing.scale(self.X_train)
		self.X_test = preprocessing.scale(self.X_test)

	def scale_samples_to_range(self):
		##Samples lie in range between 0 and 1
		minMaxScaler = preprocessing.MinMaxScaler()
		self.X_train = minMaxScaler.fit_transform(self.X_train)
		self.X_test = minMaxScaler.fit_transform(self.X_test)

	def run_pca(self, n_components):
		self.pca = PCA(n_components=20)
		self.X_train = self.pca.fit_transform(self.X_train)
		print "Reduced data down to ", self.pca.n_components_, " dimensions: "
		print "Transforming test data ..."
		self.X_test = self.pca.transform(self.X_test)

	def define_rfc(self, n_estimators=20):
		self.clf = RandomForestClassifier(n_estimators=n_estimators)
		self.clf.fit(self.X_train, self.y_train)
		print self.clf.get_params()

	def defineSVC(self, C=1.0, kernel='rbf', degree=3, gamma=0.0, coef0=0.0, shrinking=True, 
				  probability=False, tol=0.01, cache_size=200, class_weight='auto', verbose=True, 
				  max_iter=-1, random_state=None):

		print "Using a Support Vector Machine Classifier ..."
		self.clf = SVC(C=C, kernel=kernel, degree=degree, gamma=gamma, coef0=coef0, shrinking=shrinking, 
				  probability=probability, tol=tol, cache_size=cache_size, class_weight=class_weight, verbose=verbose, 
				  max_iter=max_iter, random_state=random_state)
		print self.clf.get_params()

	def score(self):
		print classification_report(self.y_test, self.prediction)
		print "predict 0: ", np.sum(self.prediction == 0)
		print "predict 1: ", np.sum(self.prediction == 1)
		print "actual 0: ", np.sum(self.y_test == 0)
		print "actual 0: ", np.sum(self.y_test == 1)
		#print "feature importances:"
		#print self.clf.feature_importances_

	def predict(self):
		self.prediction = self.clf.predict(self.X_test)

	def confusion_mat(self):
		cm = confusion_matrix(self.y_test, self.prediction)
		plt.matshow(cm)
		plt.title('Confusion matrix')
		plt.colorbar()
		plt.ylabel('True label')
		plt.xlabel('Predicted label')
		plt.show()

	def runSVCGridSearch(self):
		C_vals = [0.001, 0.01, 0.1, 1, 10, 100]
		gamma_vals = [1E-4, 1E-3, 1E-2, 1E-1, 1, 1E1, 1E2, 1E3, 1E4]

		for C in C_vals:
			for gamma in gamma_vals:
				print "\n\n C: ", C, "  gamma: ", gamma
				self.defineSVC(C=C, gamma=gamma)
				self.trainCLF()
				print "Training Scores:"
				self.getScores(self.X_train, self.y_train)
				print "Testing Scores:"
				self.getScores(self.X_cv, self.y_cv)

trainer = Trainer()
trainer.standardize_samples()
trainer.scale_samples_to_range()
n_trees = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
for n in n_trees:
	trainer.define_rfc(n_estimators=n)
	trainer.predict()
	trainer.score()