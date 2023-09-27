import pickle
from collections import deque
from fractions import Fraction
from itertools import product
from typing import Tuple, List

import numpy as np
import tensorflow as tf

from utils.paths import MODELS_PATH


class PredModel:
    def __init__(self, model_name: str = 'visa', n_sequence: int = 15):
        # Define path
        path = MODELS_PATH.joinpath(model_name)

        self.n_sequence = n_sequence
        model_path = path.joinpath(str(self.n_sequence))

        self.model = tf.keras.models.load_model(model_path)
        self.info = pickle.load(open(path.joinpath('data_info.bak'), 'rb'))
        self.labels = self.info['labels']
        self.final_labels = {'final'}
        self.n_labels = len(self.labels)
        self.n_resources = self.info['n_resources']
        self.norm = self.info['norm']

    def encode_to_predict(self, token: int, sequence: deque, times: deque, resources: List[deque]):
        # Convert sequence into categorical sequence
        cat_sequence = [self.labels.index(x) for x in sequence]

        # Convert categorical sequence into OHE encoding to predict.
        x_activities = tf.keras.utils.to_categorical(cat_sequence, num_classes=self.n_labels)

        # Convert into a numpy array of times
        x_durations = np.array(times).reshape(-1, 1)

        # Convert into a numpy array of tokens
        x_tokens = np.array([token] * self.n_sequence).reshape(-1, 1)

        # Convert into a numpy array of resources
        x_resources = np.concatenate(tuple(map(lambda r: np.array(r), resources)), axis=1)

        # Prepare data
        # x_encoded = None

        # # Join all info
        # for x in zip(x_activities, times, *resources):
        #     # Append to local `x` (act, token, duration)
        #     x_local = np.append(x[0], token)
        #     x_local = np.append(x_local, x[1])
        #
        #     for i in range(self.n_resources):
        #         # Extract information
        #         available, queue, usage = x[i + 2]
        #         norm = self.norm[i + 1]
        #
        #         # Normalize information
        #         n_available = (available - norm['available']['mean']) / norm['available']['std']
        #         n_queue = (queue - norm['queue']['mean']) / norm['queue']['std']
        #         n_usage = (usage - norm['usage']['mean']) / norm['usage']['std']
        #
        #         # Append to local `x`
        #         x_local = np.append(x_local, [n_available, n_queue, n_usage])
        #
        #     # Prepare full x
        #     x_encoded = x_local.reshape(1, -1) if x_encoded is None else np.vstack((x_encoded, x_local))

        return x_activities, x_durations, x_tokens, x_resources

    def make_prediction(self, token: int, activities: deque, durations: deque, resources: list, n_branches: int):
        # Get sequence encoding
        x_activities, x_durations, x_tokens, x_resources = self.encode_to_predict(
            token, activities, durations, resources
        )

        # Get predictions
        y_act, y_duration, y_resources = self.model.predict([
            x_activities[np.newaxis, :], x_tokens[np.newaxis, :], x_resources[np.newaxis, :]
        ], verbose=0)

        """
        Get last activity. It is not possible for the next activity to be the same as the current activity, therefore, 
        I remove the last activity from the list of possible next activities.
        """
        last_cat = self.labels.index(activities[-1])
        # Obtain the most probable activities
        sorted_pred = np.argsort(y_act[0])
        # Remove that categorical activity
        sorted_pred = np.delete(sorted_pred, np.where(sorted_pred == last_cat))
        # Sort in reverse order (from higher to lower) and get `n_branches´ elements
        top_i_activities = sorted_pred[::-1][:n_branches]
        top_activities = {self.labels[i]: y_act[0][i] for i in top_i_activities}

        # Extract next duration (Add some min duration to avoid infinite loop)
        next_duration = max(y_duration[0][0], .1)

        # Extract resources info (3 is for the resource information -> available, queue, usage)
        res = tuple(y_resources.reshape(-1, 3).tolist())

        # Return prediction
        return top_activities, next_duration, *res

    def predict(self, session: dict, time_limit: float, t_eps: float, min_prob: float = 0., n_branches: int = 3):
        """
        Alternative prediction where ONLY the time limit is looked at
        :param min_prob: Minimum probability to be reached to take a branch into account
        :param n_branches: Maximum number of branches to be stored
        :param t_eps: Epsilon time
        :param session:
        :param time_limit:
        :return:
        """

        # With this variable we can store different branches, each one with a specific probability.
        possible_combinations = list()
        sessions = list()

        # For each session and trace
        for session_id, trace in session.items():
            # Check if trace has information
            assert len(trace) != 0

            # Get last timestamp and activity as reference
            last_timestamp, last_activity = trace.get_last_timestamp(), trace.get_last_activity_name()

            # Check if not last activity
            ok = last_activity not in self.final_labels

            if not ok:
                # Skip this session
                continue

            # Get last `n_sequence` elements of sequence
            activities = deque(trace.get_activities(self.n_sequence), maxlen=self.n_sequence)

            # Extract trace features
            timestamps = [float(t) for t in trace.get_timestamps(self.n_sequence)]

            # Extract length of t list
            t_len = len(timestamps)

            # Calculates the difference between each time step of the last n elements
            durations = deque([
                0. if i == 0 else (timestamps[i] - timestamps[i - 1])
                for i in range(max(t_len - self.n_sequence, 0), t_len)
            ], maxlen=self.n_sequence)

            # Prepare resource information to normalize
            resources = [
                deque(trace.get_resources(i, self.n_sequence), maxlen=self.n_sequence)
                for i in range(1, self.n_resources + 1)
            ]

            # Fill with waiting activities
            for _ in range(len(activities), self.n_sequence):
                activities.appendleft('padding')
                durations.appendleft(0.)

                for i in range(self.n_resources):
                    resources[i].appendleft((0, 0, 0.))

            # Create variable to save all predictions for this session
            predictions = []
            # Save timestamp
            current_timestamp = last_timestamp
            # Total duration
            total_duration = 0.

            # From here we can start to explore all probabilities. Estimate an initial prediction
            pred = self.make_prediction(session_id, activities, durations, resources, n_branches=n_branches)

            # Extract all possible branches
            branches = list(map(lambda x: self.extract_branches(
                session_id, (x, *pred[1:]), activities, durations, current_timestamp, total_duration, n_branches,
                predictions, t_eps, time_limit, resources
            ), pred[0].items()))

            # Extract batch that satisfied with the requirements
            branches = list(self.filter_branches(
                branches=[e for branch in branches for e in branch], min_prob=min_prob, max_branches=n_branches
            ))

            if len(branches) > 0:
                sessions.append(session_id)
                possible_combinations.append(branches)

        # Collect answer
        answers = list()

        for comb in product(*possible_combinations):
            prob: float = 1.
            prediction = list()

            for i, s in enumerate(sessions):
                # Extract trace info and probability
                info = comb[i][0]
                prob *= comb[i][1]

                # Extract prediction info
                prediction.extend((s, *line) for line in info)

            # Sort predictions
            prediction.sort(key=lambda x: x[2])

            # Add answer information
            answers.append((prob, prediction))

        # Sort by probability
        answers.sort(key=lambda x: x[0], reverse=True)

        # Keep only best `n_branches` and with min probabilities
        return list(filter(lambda x: x[0] >= min_prob, answers[:n_branches]))

    def extract_branches(
            self, session_id: int, pred, activities: deque, durations: deque, c_timestamp: float, total_duration: float,
            n_branches: int, predictions: list, t_eps: float, time_limit: float, resources: list, probs: list = None
    ):
        if probs is None:
            probs = []

        # Split pred information
        activity, prob = pred[0]

        # Update timestamp and duration variables
        c_timestamp += pred[1]
        total_duration += pred[1]

        # Make copies
        c_pred = predictions.copy()
        c_probs = probs.copy()

        c_pred.append((activity, c_timestamp))
        c_probs.append(prob)

        if (total_duration + t_eps) > time_limit:
            # Eliminate the last prediction to avoid exceeding time
            c_pred.pop()
            c_probs.pop()
            # Calculate branch probability
            f_prob = np.prod(c_probs) ** (1 / len(c_probs)) if len(c_probs) > 0 else 0.
            # Stop to predict
            return c_pred, f_prob
        elif activity in self.final_labels:
            # If is final, then stops!
            f_prob = np.prod(c_probs) ** (1 / len(c_probs))
            # Stop to predict
            return c_pred, f_prob
        else:
            # Make copy to continue explore
            c_act = activities.copy()
            c_act.append(activity)

            c_dur = durations.copy()
            c_dur.append(pred[1])

            # Make a copy of resources
            c_res = []
            for i, r in enumerate(resources):
                c_r = r.copy()
                c_r.append(pred[2 + i])
                c_res.append(c_r)

            # Complete next step
            next_pred = self.make_prediction(
                token=session_id, activities=c_act, durations=c_dur, resources=c_res, n_branches=n_branches
            )

            # Extract all branches
            branches = map(lambda x: self.extract_branches(
                session_id, (x, *next_pred[1:]), c_act, c_dur, c_timestamp, total_duration, n_branches, c_pred, t_eps,
                time_limit, c_res, c_probs
            ), next_pred[0].items())

            # Flatten branches
            flatten_branches = []

            for branch in branches:
                if isinstance(branch, list):
                    flatten_branches.extend([*branch])
                else:
                    flatten_branches.append(branch)

            return flatten_branches

    def filter_branches(self, branches: list, min_prob: float, max_branches: int):
        # Reduce getting only uniques branches
        branches = self.reduce_branches(branches)

        # Fix problem
        if not isinstance(branches[0], tuple):
            branches = [tuple(branches)]

        # 1. We sort all branches by probability
        branches.sort(key=lambda x: x[1], reverse=True)
        """
        2. We take only the best `max_branches`
        3. Now, we can filter by probability
        """
        # Return best branches
        return filter(lambda x: x[1] >= min_prob, branches[:max_branches])

    @staticmethod
    def reduce_branches(branches: list):
        new_branches = []

        for branch in branches:
            if branch not in new_branches:
                new_branches.append(branch)

        return new_branches

    @staticmethod
    def split_data(line: str) -> Tuple:
        # Cleaning tokens
        tokens = [x.strip() for x in line.split(',')]

        # Extract and parse resources fields
        # Zip resources (depends on number of information elements we want to extract: name, available, queue, usage)
        zip_res = zip(*[tokens[(3 + i)::4] for i in range(4)])
        # Parsing attributes
        parsing_res = ((name, int(available), int(queue), float(usage)) for name, available, queue, usage in zip_res)
        # Flatten list
        resources = tuple(item for sub_item in parsing_res for item in sub_item)

        # Token, activity, timestamp,
        # (resources)
        # name, available, queue, usage
        return int(tokens[0]), tokens[1], Fraction(tokens[2]), *resources
