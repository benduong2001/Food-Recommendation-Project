#!/usr/bin/env python
# coding: utf-8

# In[1]:


import logging as logger

from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import logging
from sklearn.metrics import roc_auc_score

from sklearn.metrics import confusion_matrix
import seaborn as sns

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use("ggplot")

import os
from collections import defaultdict
from bs4 import BeautifulSoup  
import requests
import zipfile
import io
import nltk
from nltk.corpus import stopwords
#from nltk.stem.porter import PorterStemmer
#from nltk.tokenize import word_tokenize
nltk.download('stopwords')
stop_words = stopwords.words('english')
#import geopandas as gpd|
#import shapely
import gensim
import tqdm
import tensorflow as tf
import keras

from sklearn.linear_model import LogisticRegression

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.manifold import SpectralEmbedding
from sklearn.preprocessing import normalize
import sys

path_folder = (os.path.abspath(os.path.join((os.path.abspath(os.path.join(os.getcwd(), os.pardir))),os.pardir)))

google_colab = 0
if google_colab == 1:
    from google.colab import drive
    drive.mount('/content/drive/')
    path_folder = "/content/drive/MyDrive/dsprojects/dsproject_grev/"
    
sys.path.insert(0, path_folder+"/src/"#+features/"
                )
import util
import features.data_preparation_interaction as dpi


print(dpi.Temp_Interaction_Data_Preparation_Builder)

import tqdm
import pickle

from keras.applications.vgg16 import VGG16
#vggnet_model = VGG16()
pics_link_header = "https://lh5.googleusercontent.com/p/"
from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import decode_predictions

from PIL import Image
import requests
from io import BytesIO

from sklearn.preprocessing import LabelEncoder

import string

USING_SPARK = 0
SPARK_SESSION_VERSION = 1
if USING_SPARK == 1:
    import findspark
    import pyspark
    import pyspark.sql.functions as F
    import pyspark.sql.types as T
    import pyspark.ml as M
    from pyspark.sql.window import Window
    from pyspark.sql import SparkSession
    findspark.init()
    if SPARK_SESSION_VERSION == 1:
        spark = SparkSession.builder.getOrCreate()
    elif SPARK_SESSION_VERSION == 2:
        spark = (SparkSession.builder
        .master('local[*]')
        .config("spark.driver.memory", "3g")
        .appName('food_rec')
        .getOrCreate()
)

class Temp_Interaction_Model_Builder:
    def __init__(
        self,
        data_preparation
    ):
        self.data_preparation = data_preparation
    def set_up(self, reviews_df):
        
        X_seen = self.data_preparation.conjoin_embeddings(self.self.data_preparation.id2vec_df)
        y_seen = np.ones(X_seen.shape[0])
    
        X_unseen = self.data_preparation.conjoin_embeddings(self.data_preparation.id2vec_df_unseen)
        y_unseen = np.zeros(X_unseen.shape[0])

        train_dataset_size = len(y_seen)+len(y_unseen)
        train_dataset_indexer = np.arange(train_dataset_size)
        np.random.shuffle(train_dataset_indexer)

        X = np.vstack((X_seen,X_unseen))
        y = np.hstack((y_seen,y_unseen))
        X = X[train_dataset_indexer]
        y = y[train_dataset_indexer]
        
        X_train, X_val, y_train, y_val = train_test_split(X, y, stratify=y, test_size=0.25)
        
        pca = PCA(2)
        temp_X_pca_input = X_train
        temp_y_pca_input = y_train

        Z = pca.fit_transform(temp_X_pca_input)
        fig, ax = plt.subplots(figsize=(8,8))
        ax.scatter(Z[:,0], Z[:,1],c=temp_y_pca_input, alpha=0.1, s=5, cmap="winter")

        self.X_train = X_train
        self.X_val = X_val
        self.y_train = y_train
        self.y_val = y_val
        return X_train, X_val, y_train, y_val
    def logistic_regression(self, C=1, max_iter=800):
        model = LogisticRegression(max_iter=max_iter, C=C, class_weight="balanced")
        return model
    def neural_network(self,input_shape):
        model = Sequential()
        model.add(Dense(50, input_shape=input_shape, activation='relu'))
        model.add(Dense(100, activation='relu'))
        #model.add(Dense(100, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))
        # Compile model
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model
    def train_model(self, model=None):
        if model is None:
            model = self.model 
        model.fit(self.X_train, self.y_train)
        return model
    def evaluate_metrics(self, y_true, y_pred):
        conf_matrix = confusion_matrix(self.y_val, y_predictions,normalize="true")
        print(conf_matrix)
        print("AUC:", roc_auc_score(y_predictions.astype(int), self.y_val.astype(int)))
    def validate_model(self, model=None):
        if model is None:
            model = self.model 
        y_predictions = model.predict(self.X_val)
        self.evaluate_metrics(self.y_val, y_predictions)
        return model

    def baseline(self, reviews_df):
        self.data_preparation.with_concatenated = 0
        self.set_up(reviews_df)
        model = self.logistic_regression(C=1, max_iter=800)
        model = self.train_model(model)
        model = self.validate_model(model)
    def deep_learning(self, reviews_df):
        self.data_preparation.with_concatenated = 1
        self.set_up(reviews_df)
        model = self.neural_network(input_shape=(self.X_train.shape[1],))
        model.fit(X_train, y_train, epochs=5, batch_size=100)
        y_predictions = model.predict(self.X_val)
        y_predictions = np.squeeze((y_predictions>=0.5).astype(int))
        self.evaluate_metrics(self.y_val, y_predictions)
        return model
    
