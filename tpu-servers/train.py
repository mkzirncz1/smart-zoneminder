"""
Train an SVM face classifier from 128-d face encodings.

Part of the smart-zoneminder project:
See https://github.com/goruck/smart-zoneminder.

Copyright (c) 2019 Lindo St. Angel
"""

from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
import pickle

# Path to known face encodings.
# The pickle file needs to be generated by the 'encode_faces.py' program first.
KNOWN_FACE_ENCODINGS_PATH = './encodings.pickle'
# Path to save model to. 
SVM_MODEL_PATH = './face_recognizer.pickle'
# Path to save label encoder to. 
SVM_LABEL_PATH = './face_labels.pickle'

# Load the known faces and embeddings.
with open(KNOWN_FACE_ENCODINGS_PATH, 'rb') as fp:
	data = pickle.load(fp)

# Encode the labels.
print('Encoding labels...')
le = LabelEncoder()
labels = le.fit_transform(data['names'])

def svc_param_selection(x, y, nfolds):
    # Exhaustive search over specified parameter values for svm.
    Cs = [0.001, 0.01, 0.1, 1, 10]
    gammas = [0.001, 0.01, 0.1, 1]
    param_grid = {'C': Cs, 'gamma' : gammas}
    grid_search = GridSearchCV(SVC(kernel='rbf'), param_grid, iid=False, cv=nfolds)
    grid_search.fit(x, y)
    grid_search.best_params_
    return grid_search.best_params_

# Find best parameters.
print('Finding best parameters...')
best = svc_param_selection(data['encodings'], labels, 15)
best_C = best['C']
best_gamma = best['gamma']
print('C {}, gamma {}'.format(best_C, best_gamma))

# Train the model used to accept the 128-d embeddings of the face and
# then produce the actual face recognition model. 
print('Training model...')
recognizer = SVC(C=best_C, kernel='rbf', gamma=best_gamma, probability=True)
recognizer.fit(data['encodings'], labels)

# Write the face recognition model to disk.
print('Saving model...')
with open(SVM_MODEL_PATH, 'wb') as outfile:
	outfile.write(pickle.dumps(recognizer))

# Write the label encoder to disk.
print('Saving label encoder...')
with open(SVM_LABEL_PATH, 'wb') as outfile:
	outfile.write(pickle.dumps(le))