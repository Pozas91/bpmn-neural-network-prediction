import socketserver
from datetime import datetime
from fractions import Fraction
from typing import Tuple

import tensorflow as tf

from pred_model import PredModel
from trace import Trace


# from code found at https://docs.python.org/3/library/socketserver.html
class Predictor(socketserver.StreamRequestHandler):
    """
    The request handler class for the server.

    It is instantiated once per connection to the server. It overrides
    the handle() method to implement communication to the client with
    streams, instead of the more common low-level direct socket reading.
    """
    __data = list()
    EPS = 1e-4
    LOT = 8
    INITIAL = 'initial'

    @staticmethod
    def extend(trc, act_name: str, act_time: Fraction, resources: Tuple):
        """this is one stupid method"""
        if len(trc) != 0 and trc.get_last_activity_name() == 'final':
            print('[PREDICTOR] ... trying to add new activity to an already finished session!!!')
        else:
            trc.append(act_name, act_time, resources)

    @staticmethod
    def get_delivery_model():
        return PredModel(model_name='delivery', n_sequence=6)

    @staticmethod
    def get_visa_model():
        return PredModel(model_name='visa', n_sequence=15)

    @staticmethod
    def get_recruitment_model():
        return PredModel(model_name='recruitment', n_sequence=18)

    def rebuild_trace_suffix(self, time_shift, acts):
        ans, ctime = list(), time_shift
        for sid, aid, time in acts:
            ctime += time
            if aid != self.INITIAL:
                ans.append((sid, aid, ctime))
            else:
                print('[PREDICTOR] ... bad prediction for session {0} (ignoring)!!!'.format(sid))
        return ans

    def predict(self, model, session, time_limit):
        """
        return a list of data (actid, timestm) whose timestm is at most
        t from the prediction run from each trace in the session
        """
        answer = list()
        for session_id in session:
            trace, d = session[session_id], self.LOT
            assert len(trace) != 0
            ok = trace.get_last_timestamp() + self.EPS < time_limit and trace.get_last_activity_name() != 'final'
            pred = None
            while ok:
                # Extract prediction
                pred = model.predict_from_prefix_case(
                    session_id, trace.get_activities(), d + 1,
                    [datetime.fromtimestamp(float(t)) for t in trace.get_timestamps()]
                )
                # Correct timestamp of traces
                pred = self.rebuild_trace_suffix(trace.get_last_timestamp(), pred)

                if len(pred) < d + 1:
                    # Extract more prediction data
                    ok = False
                elif pred[-1][2] + self.EPS < time_limit:
                    # We have enough data, but it does not meet the desired time window.
                    d = d << 1
                else:
                    # We have enough data, but we have exceeded the desired time window.
                    while len(pred) != 0 and pred[-1][2] + self.EPS >= time_limit:
                        pred.pop()

                    ok = False

            if pred is not None:
                answer.extend(pred)

        answer.sort(key=lambda x: x[2])

        return answer

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # one can use e.g. readline() instead of raw recv() calls
        session, time = dict(), Fraction(0)

        # Select model to make predictions
        model = self.get_recruitment_model()

        ended = False
        print("{0} wrote:".format(self.client_address[0]))

        while not ended:
            self.data = self.rfile.readline().strip()
            decode_data = self.data.decode()
            print('[PREDICTOR] The server received the line: {0}'.format(decode_data))

            if decode_data[:len('PREDICT')] == 'PREDICT':
                tok = [x.strip() for x in decode_data.split()]

                # Define branches and probability
                n_branches: int = int(tok[2]) if len(tok) == 3 else 1
                min_prob: float = int(tok[3]) if len(tok) == 4 else 0.
                answers = model.predict(
                    session, float(Fraction(tok[1])), self.EPS, min_prob=min_prob, n_branches=n_branches
                )

                show_prob = len(answers) > 1

                if show_prob:
                    header = f'PREDICTIONS {len(answers)}\n'
                    print(f'[PREDICTOR] The server is sending signal: {header}')
                else:
                    header = ''

                for item in answers:
                    # Extract probability and answer
                    prob, answer = item

                    # Append probability
                    answer_str = f'PROBABILITY {prob:.4f}\n' if show_prob else ''

                    # Convert into string
                    answer_str += Trace.trace2maude(answer, len(answer))

                    if len(answer) == 0:
                        answer_str = 'END\n'
                    else:
                        answer_str += '\nEND\n'

                    # Concat
                    answer_str = header + answer_str

                    print('[PREDICTOR] The server is sending {0} events: \n{1}'.format(len(answer), answer_str))
                    self.wfile.write(answer_str.encode('utf-8'))
            elif decode_data[:len('END')] == 'END' or decode_data == '':
                ended = True
                print('Ending prediction for {0}'.format(self.client_address[0]))
            else:
                # Preprocessing data
                tok = model.split_data(decode_data)
                session_id, act_name, time = tok[0], tok[1], tok[2]

                if session_id not in session:
                    session[session_id] = Trace(session_id)
                    print('[PREDICTOR] ... creating new session for process {0}'.format(session_id))

                if act_name == 'final':
                    print('[PREDICTOR] ... closing session for process {0}'.format(session_id))

                self.extend(session[session_id], act_name, time, tok[3:])

        # Clear keras backend session
        # Tensorflow backend is a singleton and its memory grows with each iteration, this line avoid that behaviour
        tf.keras.backend.clear_session()


if __name__ == "__main__":
    IP, PORT = 'localhost', 8811
    # Create the server, binding to `IP` on port `PORT`
    with socketserver.TCPServer((IP, PORT), Predictor) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
