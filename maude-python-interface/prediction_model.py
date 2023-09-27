import pandas as pd
import random
import time
from fractions import Fraction

import numpy as np
import pandas as pd
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Nadam


class Lstm_model(object):
    """implements a LSTM model to predict future activities in a trace"""

    def __init__(self):
        self.df = pd.read_csv('./Data/trace-250.csv', delimiter=',', error_bad_lines=False, header=None,
                              names=['CaseID', 'ActivityID', 'Timestamp'])
        self.df['Timestamp'] = self.df['Timestamp'].apply(lambda x: self.timestamp_adjustment(x))
        self.df['ActivityID'] = self.df['ActivityID'].apply(lambda x: x.strip())

    def generate_dict_activities(self):
        '''Creates dictionaries to encode and decode the sequence of activities and returns both dictionaries'''
        self.dict_activities = dict()
        self.dict_index_activities = dict()
        activities = self.df['ActivityID'].unique()
        for i, activity in enumerate(activities):
            activity = activity.strip()
            self.dict_activities[activity] = i
            self.dict_index_activities[i] = activity

    def timestamp_adjustment(self, x):
        '''Convert rational in date format and returns the element converted to timestamp.'''
        x = float(Fraction(x))
        return x

    def split(self, train_size):
        cases_list = list(self.df['CaseID'].unique())
        training_percentage = int(train_size * len(cases_list))
        self.train_cases = random.sample(cases_list, training_percentage)
        self.test_cases = [case for case in cases_list if case not in self.train_cases]

    def calculate_timedifference_next_activity(self, df_case):
        '''Static method that calculates the difference in seconds between two events using their corresponding timestamp and returns
           their difference as a 1D-array'''
        previous_activity = ''
        present_activity = ''
        previous_time = 0
        present_time = 0
        times = []
        for i, element in df_case[['ActivityID', 'Timestamp']].iterrows():
            activity = element.ActivityID.strip()
            time = element.Timestamp
            if (activity == 'initial'):
                t = 0
                times.append(t)
            else:
                present_activity = activity
                present_time = time
                if (previous_activity == ''):
                    previous_activity = present_activity
                    previous_time = time
                t = (present_time - previous_time)
                times.append(t)
            previous_activity = activity
            previous_time = time
        return times

    def generate_sequences(self):
        '''Method that generates sequences of activities'''
        self.sequence_cases = []
        self.sequence_duration = []
        self.sequence_times = []
        self.next_activities = []
        for case in self.train_cases:
            list_activities_by_case = self.df[self.df['CaseID'] == case]['ActivityID'].to_list()
            timestamp_by_case = self.df[self.df['CaseID'] == case][['ActivityID', 'Timestamp']]
            # print('The case number is: '+str(case))
            # print('The timestamps for this case are: '+str(timestamp_by_case.Timestamp.values))
            time_differences_by_case = self.calculate_timedifference_next_activity(timestamp_by_case)
            duration = []
            for i in range(len(list_activities_by_case) + 1):
                if i > 0:
                    self.sequence_cases.append(list_activities_by_case[0:i])
                    duration.append(time_differences_by_case[i - 1])
                    self.sequence_times.append(time_differences_by_case[0:i])
                    if i < len(list_activities_by_case):
                        self.next_activities.append(list_activities_by_case[i])
            self.sequence_duration.append(duration)
            # print('The duration between activies at the end is: '+str(duration))
            self.next_activities.append('initial')

    def get_dimensions(self):
        self.max_length_case = max([len(sublist) for sublist in self.sequence_cases])
        self.max_features = max(self.dict_index_activities.keys()) + 2

    def one_hot_encoder(self, activity_name):
        '''Function to perform one hot encoding, returns a vector that represents the activity received.'''
        vector_zeros = np.zeros(self.max_features)
        k = self.dict_activities[activity_name]
        vector_zeros[k] = 1
        return vector_zeros

    def set_training_data(self):
        len_sequences = len(self.sequence_cases)
        self.X_train = np.zeros((len_sequences, self.max_length_case, self.max_features), dtype=np.float32)
        self.y_a_train = np.zeros((len_sequences, self.max_features), dtype=np.float32)
        self.y_t_train = np.zeros(len_sequences, dtype=np.float32)
        self.max_featuresy_t_train = [time for subsequence in self.sequence_duration for time in subsequence]
        for i, sequence in enumerate(self.sequence_cases):
            for k, activity in enumerate(sequence):
                leftpad = self.max_length_case - 1 - k
                self.X_train[i, leftpad] = self.one_hot_encoder(activity.strip())
                self.X_train[i, leftpad, self.max_features - 1] = self.sequence_times[i][k]
            self.y_a_train[i] = self.one_hot_encoder(self.next_activities[i].strip())

    def model_prediction(self):
        '''Function to construct the neural network'''
        main_input = Input(shape=(self.max_length_case, self.max_features), name='main_input')
        # train a 2-layer LSTM with one shared layer
        l1 = LSTM(100, return_sequences=True, dropout=0.2)(main_input)  # the shared layer
        b1 = BatchNormalization()(l1)
        l2_1 = LSTM(100, return_sequences=False, dropout=0.2)(b1)  # the layer specialized in activity prediction
        b2_1 = BatchNormalization()(l2_1)
        l2_2 = LSTM(100, return_sequences=False, dropout=0.2)(b1)  # the layer specialized in time prediction
        b2_2 = BatchNormalization()(l2_2)
        act_output = Dense(self.max_features, activation='softmax', name='act_output')(b2_1)
        time_output = Dense(1, name="time_output", kernel_initializer="glorot_uniform")(b2_2)
        self.lstm_model = Model(inputs=[main_input], outputs=[act_output, time_output])
        opt = Nadam(lr=0.002, beta_1=0.9, beta_2=0.999, schedule_decay=0.004, clipvalue=3)
        self.lstm_model.compile(loss={'act_output': 'categorical_crossentropy', 'time_output': 'mae'}, optimizer=opt)
        early_stopping = EarlyStopping(monitor='val_loss', patience=42)
        path_to_model = 'model_{epoch:02d}-{val_loss:.2f}.h5'
        model_checkpoint = ModelCheckpoint(path_to_model, monitor='val_loss', verbose=0, save_best_only=True,
                                           save_weights_only=False, mode='auto')
        lr_reducer = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, verbose=0, mode='auto', cooldown=0,
                                       min_lr=0)
        start_time = time.time()
        preload = False  # Change in case you want to train again the model
        if not preload:
            self.lstm_model.fit(np.array(self.X_train),
                                {'act_output': np.array(self.y_a_train), 'time_output': np.array(self.y_t_train)},
                                validation_split=0.2, verbose=2,
                                callbacks=[early_stopping, model_checkpoint, lr_reducer],
                                batch_size=self.max_length_case, epochs=500)
            print("--- %s seconds ---" % (time.time() - start_time))
            self.lstm_model.save_weights('./models/model250.h5')
        self.lstm_model.load_weights('./models/model250.h5')

    def cycle(self, list_input):
        i = 0
        j = 1
        count = 0
        end = ''
        cycles = []
        while (j < len(list_input)):
            tortoise = list_input[i]
            hare = list_input[j]
            if tortoise == hare:
                cycles.append(tortoise)
                end = list_input[i + 1]
            i += 1
            j = i + 2
        if (len(cycles) != 0):
            count = 1 + (len(cycles) / 2)
        return count, end

    def encode_for_prediction(self, partial_sequence, partial_times):
        '''Function to convert partial sequence in input to the neural network for next activity prediction'''
        X_test = np.zeros((1, self.max_length_case, self.max_features), dtype=np.float32)
        for i, activity in enumerate(partial_sequence):
            leftpad = self.max_length_case - 1 - i
            X_test[0][leftpad] = self.one_hot_encoder(activity)
            X_test[0, leftpad, self.max_features - 1] = partial_times[i]
        return X_test

    def calculate_seconds_difference_next_activity(self, list_timestamp, list_activities):
        previous_activity = ''
        present_activity = ''
        previous_time = 0
        present_time = 0
        times = []
        for i, time in enumerate(list_timestamp):
            activity = list_activities[i]
            if (activity == 'initial'):
                t = 0
                times.append(t)
            else:
                present_activity = activity
                present_time = time
                if (previous_activity == ''):
                    previous_activity = present_activity
                    previous_time = time
                t = present_time - previous_time
                times.append(t)
            previous_activity = activity
            previous_time = time
        return times

    def predict_from_prefix_case(self, sesid, s, n, t):
        '''Function to predict the next activities of a given incomplete trace'''
        cropped_sequence = [element for element in s]
        cropped_times = self.calculate_seconds_difference_next_activity(t, s)
        y_t_predicted = list()
        result = list()
        for j in range(n):
            X_test = self.encode_for_prediction(cropped_sequence, cropped_times)
            y = self.lstm_model.predict(X_test, verbose=0)
            if (len(s)) >= 1:
                count, cycle_next = self.cycle(cropped_sequence)
                if (count >= 2):
                    weak_probability_index = self.dict_activities[cycle_next]
                    c = 1 / np.exp(count)
                    y[0][0][weak_probability_index] = c * y[0][0][weak_probability_index]
            character_prediction_index = np.argmax(y[0][0])
            next_activity = self.dict_index_activities[character_prediction_index]
            y_t = y[1][0][0]
            if y_t < 0:
                y_t = 0
            y_t_predicted.append(y_t)
            cropped_sequence.append(next_activity)
            cropped_times.append(y_t)
            result.append((sesid, next_activity, sum(cropped_times)))
            if next_activity == 'final':
                break
        return result
