from fractions import Fraction
from typing import Tuple, List

DEN_LIMIT = 1000


class Trace:
    """implements a BPMN trace with a unique identifier"""

    def __init__(self, sid):
        """creates the empty trace"""
        self.__id = sid
        self.__trace = list()

    def __len__(self):
        """return the number of elements in the trace"""
        return len(self.__trace)

    def __str__(self):
        """return a string representation of the trace"""
        return str(self.__id) + ": " + ''.join(['({0}, {1})'.format(x[0], x[1]) for x in self.__trace])

    def append(self, act, timestamp, extras: Tuple):
        """adds an element to the end of the trace"""
        self.__trace.append((act, timestamp, *extras))

    def get_trace(self):
        """return the trace detail"""
        return self.__trace

    def get_activities(self, n: int = 0):
        """return the list of activities"""

        # Define sequence necessary
        seq = self.__trace[-n:] if n > 0 else self.__trace
        return [x[0] for x in seq]

    def get_timestamps(self, n: int = 0):
        """return the list of timestamps"""

        # Define sequence necessary
        seq = self.__trace[-n:] if n > 0 else self.__trace
        return [x[1] for x in seq]

    def get_resources(self, res_id: int, n: int = 0) -> List:
        assert res_id > 0
        offset, features_n = 2, 4
        i = offset + (res_id - 1) * features_n

        # Define sequence necessary
        seq = self.__trace[-n:] if n > 0 else self.__trace

        # Skip resource name
        return [(x[i + 1], x[i + 2], x[i + 3]) for x in seq]

    def get_last_resources(self, res_id: int) -> Tuple:
        return tuple(self.get_resources(res_id, 1))

    def get_last_timestamp(self):
        """return the time of the last timestamp; if empty, then 0"""
        return 0 if len(self.__trace) == 0 else self.__trace[-1][1]

    def get_last_activity_name(self):
        """return the name of the last activity -- the trace cannot be empty"""
        assert len(self.__trace) != 0
        return self.__trace[-1][0]

    def get_id(self):
        """return the trace id"""
        return self.__id

    def clone(self):
        """return a clone of the trace"""
        ans = Trace(self.get_id())
        for x in self.__trace:
            ans.append(x)
        return ans

    @staticmethod
    def trace2maude(trace, n):
        """static method to generate a string with the representation of the trace that can be parsed in Maude"""
        assert 0 <= n <= len(trace)
        ans = list()

        for session_id, act_name, act_time in trace:
            if act_name in ('final1', 'final2'):
                continue
            ans.append('{0}, {1}, {2:.4f}'.format(session_id, act_name, float(Fraction(act_time))))

        return '\n'.join(ans)
