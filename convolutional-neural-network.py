from functools import reduce
from keras import metrics
from keras.callbacks import ReduceLROnPlateau
from keras.models import Sequential
from keras.optimizers import Adam
from keras.utils import to_categorical
from pandas import read_csv
from pandas import DataFrame
from keras import regularizers
from keras.layers import Conv1D, Dense, MaxPooling1D, Dropout, Flatten
from glob import glob
import numpy as np

model = Sequential()
model.add(Conv1D(32, kernel_size=(2,), activation='relu', input_shape=(8, 8,),
                 kernel_regularizer=regularizers.l2(0.01),
                 activity_regularizer=regularizers.l1(0.01)
                 ))
model.add(Dropout(0.5))
for i in range(3):
	model.add(Conv1D(32, kernel_size=(2,), activation='relu',
	                 kernel_regularizer=regularizers.l2(0.01),
	                 activity_regularizer=regularizers.l1(0.01)
	                 ))
	model.add(Dropout(0.5))
model.add(Flatten())
for j in range(4):
	model.add(Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.01),
                activity_regularizer=regularizers.l1(0.01)))
	model.add(Dropout(0.5))
model.add(Dense(1, activation='tanh'))
model.compile(optimizer=Adam(), loss="mse")

# from keras.utils import plot_model
# plot_model(model, show_shapes=True, to_file='model.png')

# exit()

df = DataFrame()
for file in glob("csv/*pgn*.csv"):
	print("Processing '{}'.".format(file.split("/")[-1]))
	tf = read_csv(file, index_col=None)
	classes = [-1, 0, 1]
	lengths = [len(tf[tf["result"] == c]) for c in classes]
	minimum_length = min(lengths)
	class_tfs = [tf[tf["result"] == c].copy().sample(minimum_length) for c in classes]
	tf = reduce(lambda x, y: x.append(y, ignore_index=True), class_tfs)
	df = df.append(tf, ignore_index=True)
	print("Length is now {}.".format(len(df)))
print("\n")

training_columns = list(set(list(df)) - {"result"})
X, Y = df[training_columns].values, df["result"].values
X = X.reshape((X.shape[0], 8, 8,))

mean, std = np.mean(X), np.std(X)
X = (X - mean) / std
minimum, maximum = np.min(X), np.max(X)
X = (X + minimum) / (maximum + minimum)

#Y = to_categorical(Y + 1, num_classes=3)

model.fit(X, Y, epochs=100, validation_split=0.25, )
