#!/usr/bin/env python3

import pickle as pk
import numpy as np
import warnings
import csv

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import cross_val_score, KFold
from sklearn.cross_validation import train_test_split
from sklearn import linear_model
from sklearn import metrics

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def trainAndEvaluate(clf, xTrain, yTrain):
    clf.fit(xTrain, yTrain)
    print("Coefficient of determination on training set: " + clf.score(xTrain, yTrain))
    # create a k-fold cross validation iterator off k=5 folds
    cv = KFold(xTrain.shape[0], 5, shuffle=True, random_state=33)
    scores = cross_val_score(clf, xTrain, yTrain, cv = cv)
    print("Average coefficient of determination using 5-fold crossvalidation:" + np.mean(scores))

def evaluateErrorVarianceAndR2(clf, xTrain, xTest, yTrain, yTest):
    clf.fit(xTrain, yTrain)
    yPred = clf.predict(xTest)
    yTestTranspose = np.transpose(yTest) # Transposing these matrices for easier looping
    yPredTranspose = np.transpose(yPred)
    predictorScores = []
    
    # Add successive rows for four/three/two/one/unclassified scores
    for i in range(5):
        predictorScores.append(np.sqrt(metrics.mean_squared_error(yTestTranspose[i], yPredTranspose[i])))
        predictorScores.append(metrics.mean_absolute_error(yTestTranspose[i], yPredTranspose[i]))
        predictorScores.append(metrics.explained_variance_score(yTestTranspose[i], yPredTranspose[i]))
        predictorScores.append(metrics.r2_score(yTestTranspose[i], yPredTranspose[i]))
        
    # Last row is average score across all fields
    predictorScores.append(np.sqrt(metrics.mean_squared_error(yTestTranspose, yPredTranspose)))
    predictorScores.append(metrics.mean_absolute_error(yTestTranspose, yPredTranspose))
    predictorScores.append(metrics.explained_variance_score(yTestTranspose, yPredTranspose))
    predictorScores.append(metrics.r2_score(yTestTranspose, yPredTranspose, multioutput='uniform_average'))
    
    predictorScores = [predictorScores[i:i+4] for i in range(0, len(predictorScores), 4)] # Reshape from 1D list to 2D list    
    return predictorScores
    
fullCollection = pk.load(open("../../OutputData/outputs/pickles/fullCollection.pickle", "rb"))

with open("../classifierOutput/titlePredictor/titleScorePrediction.csv", "w", encoding="utf-8") as csvfile: 
        for key in fullCollection:
            collection = fullCollection[key]            # Update this field to get the different schools
                
            vectorizer = CountVectorizer(encoding='windows-1252')
            corpus = collection['filteredTitle']
            X = vectorizer.fit_transform(corpus) # Create a sparse matrix of our titles/count
            
            fourStar = np.array(collection['fourStar'], dtype=float)
            threeStar = np.array(collection['threeStar'], dtype=float)
            twoStar = np.array(collection['twoStar'], dtype=float)
            oneStar = np.array(collection['oneStar'], dtype=float)
            unclassified = np.array(collection['unclassified'], dtype=float)
            
            predictorScoreCategories = ["fourStar", "threeStar", "twoStar", "oneStar", "unclassified", "average"]
            
            rating = np.stack((fourStar, threeStar, twoStar, oneStar, unclassified), axis = 1)
            
            xTrain, xTest, yTrain, yTest = train_test_split(X, rating, test_size = 0.25, random_state = 33)
                
            clf0 = linear_model.LinearRegression()
            clf1 = linear_model.Ridge()
            clf2 = linear_model.Lasso()
            
            clf = [clf1]    # From analysing the data we found that the Ridge classifier is the best here, was originally 
            
             # First do predictions using our trained data only
            print("\n######################################################################\n \
            Predicitons of training data based on fitted training data for {0} \
                  #####################################################################\n".format(key))
            for classifier in clf:
                print(classifier)
                predictorScores = evaluateErrorVarianceAndR2(classifier, xTrain, xTrain, yTrain, yTrain)
                for i in range(len(predictorScores)):
                    print(predictorScores[i])
                    keyAndClassifier = [str(key), str(classifier), str(predictorScoreCategories[i])]
                    listToWrite = keyAndClassifier + predictorScores[i]
                    writer = csv.writer(csvfileTraining, delimiter = ',')
                    writer.writerow(listToWrite)
        
            # Next do prediction on testing data
            print("\n######################################################################\n \
            Predictions of testing data based on unfitted testing data for {0}\
                   ######################################################################\n".format(key))
            for classifier in clf:
                print(classifier)
                predictorScores = evaluateErrorVarianceAndR2(classifier, xTrain, xTest, yTrain, yTest)
                for i in range(len(predictorScores)):
                    print(predictorScores[i])
                    keyAndClassifier = [str(key), str(classifier), str(predictorScoreCategories[i])]
                    listToWrite = keyAndClassifier + predictorScores[i]
                    writer = csv.writer(csvfileTesting, delimiter = ',')
                    writer.writerow(listToWrite)
            
            # Finally make a (poor) prediction for liverpool universities scores in this field
            print("\n######################################################################\n \
        Predictions of Liverpool university REF Scores for {0}\
                   ######################################################################\n".format(key))
            for classifier in clf:
                print(classifier)
        
                indices = np.array([i for i, x in enumerate(collection['institutionName']) if x != "University of Liverpool"])
                xTrain = X[indices]
                
                fourStar = np.take(collection['fourStar'], indices).astype(float)
                threeStar = np.take(collection['threeStar'], indices).astype(float)
                twoStar = np.take(collection['twoStar'], indices).astype(float)
                oneStar = np.take(collection['oneStar'], indices).astype(float)
                unclassified = np.take(collection['unclassified'], indices).astype(float)
                
                yTrain = np.stack((fourStar, threeStar, twoStar, oneStar, unclassified), axis = 1)
                
                indices = [i for i, x in enumerate(collection['institutionName']) if x == "University of Liverpool"]            
                xTest = X[indices]
                liverpoolTitles = np.take(collection['title'], indices)
                
                fourStar = np.take(collection['fourStar'], indices).astype(float)
                threeStar = np.take(collection['threeStar'], indices).astype(float)
                twoStar = np.take(collection['twoStar'], indices).astype(float)
                oneStar = np.take(collection['oneStar'], indices).astype(float)
                unclassified = np.take(collection['unclassified'], indices).astype(float)
                
                yTest = np.stack((fourStar, threeStar, twoStar, oneStar, unclassified), axis = 1) # Unused
                
                classifier.fit(xTrain, yTrain)
                for title, i in zip(liverpoolTitles, range(len(liverpoolTitles))):
                    predictedScores = classifier.predict(xTest[i])
                    print(title)
                    print(predictedScores)
                    listToWrite=[key] + [title] + predictedScores.tolist()[0]
                    writer = csv.writer(csvfile, delimiter = ',')
                    writer.writerow(listToWrite)
                    
