import tensorflow as tf
import numpy as np
import pickle
import os
import pandas as pd
from keras.layers import Conv1D, Add, Input, Flatten, Dense
from keras.models import Model
from keras import backend as K
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


#df = pd.DataFrame(columns=['filename','frame','pose set','emotion','pose','pictures'])

path = '.\FORK_EMOT\PoseEMOT\GEMEP Classification\\fullGEMEP.csv'
#print("Loading data...")
#for file in os.listdir(path):
#	if file.endswith('.pkl') and file.startswith('full'):
#		with open(path+file, 'rb') as f:
#			data = pickle.load(f)
#			df = pd.concat([df, data])
#			print(file)



df = pd.read_csv(path)





prev_emotions = []
pose_frames = []
frame_set = []
emotions = []
emotion_set = []
videos = []


for idx, row in df.iterrows():
	pose_frames.append(row['pose'])
	emotions.append(row['emotion'])
	if len(pose_frames) == 11:
		pose_frames.pop(0)
		emotions.pop(0)
		frame_set.append(pose_frames.copy())
		emotion_set.append(emotions.copy())



def most_frequent(List):
    counter = 0
    num = List[0]
     
    for i in List:
        curr_frequency = List.count(i)
        if(curr_frequency> counter):
            counter = curr_frequency
            num = i
 
    return num


most_common_emotions = []
for set in emotion_set:
	most_common_emotion = most_frequent(set)
	if most_common_emotion == "happy":
		most_common_emotions.append([1,0,0,0,0,0,0])
	elif most_common_emotion == "neutral":
		most_common_emotions.append([0,1,0,0,0,0,0])
	elif most_common_emotion == "sad":
		most_common_emotions.append([0,0,1,0,0,0,0])
	elif most_common_emotion == "surprise":
		most_common_emotions.append([0,0,0,1,0,0,0])
	elif most_common_emotion == "angry":
		most_common_emotions.append([0,0,0,0,1,0,0])
	elif most_common_emotion == "fear":
		most_common_emotions.append([0,0,0,0,0,1,0])
	elif most_common_emotion == "disgust":
		most_common_emotions.append([0,0,0,0,0,0,1])
		


print(len(frame_set)) # Nx10x33x3
print(len(most_common_emotions)) # N


# convert to numpy arrays
train_x = np.array(frame_set)
train_x = tf.reshape(train_x, (-1, 10, 33*3))
most_common_emotions = np.array(most_common_emotions)


print(f"Train data shape:{train_x.shape}")


# load model
encoder = tf.keras.models.load_model('.\FORK_EMOT\PoseEMOT\GEMEP Classification\\affect_encoder_l128.h5')



# build sequential model
input_seq = Input(shape=(10, 33*3))
x = encoder(input_seq)
x = Dense(64, activation='relu')(x)
x = Dense(32, activation='relu')(x)
x = tf.keras.layers.Dropout(0.2)(x)
output = Dense(7, activation='softmax')(x)

model = Model(inputs=input_seq, outputs=output)

# freeze encoder layers
for layer in encoder.layers:
	layer.trainable = False

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=7)
model.fit(train_x, most_common_emotions, epochs=800, batch_size=32)


model.save('.\FORK_EMOT\PoseEMOT\GEMEP Classification\\Emot_classifier_l128.h5')


