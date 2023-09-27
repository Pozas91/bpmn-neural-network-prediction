DEN_LIMIT = 1000


class Trace(object):
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

  def append(self, act, timest):
    """adds an element to the end of the trace"""
    self.__trace.append((act, timest))

  def get_trace(self):
    """return the trace detail"""
    return self.__trace

  def get_activities(self):
    """return the list of activities"""
    return [x[0] for x in self.__trace]

  def get_timestamps(self):
    """return the list of timestamps"""
    return [x[1] for x in self.__trace]

  def get_id(self):
    """return the trace id"""
    return self.__id

  def clone(self):
    """return a clone of the trace"""
    ans = Trace(self.get_id())
    for x in self.__trace: ans.append(x)
    return ans

  def trace2maude(self, n):
    """static method to generate a string with the representation of the trace that can be parsed in Maude"""
    assert 0 <= n <= len(self)
    ans = list()
    for sesid, actname, acttime in self:
      ans.append('{0}, {1}, {2}'.format(sesid, actname, acttime))
    return '\n'.join(ans)
