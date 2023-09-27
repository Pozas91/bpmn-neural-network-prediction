#!/usr/bin/env python
# coding: utf-8
from datetime import datetime
from fractions import Fraction
from sys import stdin

from prediction_model import Lstm_model
from trace import Trace

END = '*'
TRSEP = ','
PRPRE = '+'

session = None


def extend(trc, aid, atime): trc.append(aid, atime)


def predict(model, session, n, m):
  '''return a list of data (actid, timestm) of size at most n
     with the prediction of at most n activities with time stamps
     starting from the prefix in trc'''
  ans = list()
  heap = list()
  EPS = 1e-4
  LOT = 8
  for sesid in session:
    trc, d = session[sesid], LOT
    ok = len(trc) == 0 or (len(trc) != 0 and trc.get_last_time_stamp() + self.EPS < t)
    while ok:
      pred = model.predict_from_prefix_case(
        sesid,
        trc.get_activities(),
        d + 1,
        [datetime.fromtimestamp(float(t)) for t in trc.get_timestamps()])
      if len(pred) < d + 1:
        ok = False
      elif pred[-1][2] + EPS < t:
        d = d << 1
      else:
        while len(pred) != 0 and pred[-1][2] + EPS >= t: pred.pop()
        ok = False
    ans.extend(pred)
  ans.sort(key=lambda x: x[2])

  #   trc = session[sesid]
  #   act = model.predict_from_prefix_case(
  #     sesid,
  #     trc.get_activities(),
  #     1,
  #     [ datetime.fromtimestamp(float(t)) for t in trc.get_timestamps() ])[0]
  #   heappush(heap, (act[2], 1, sesid, act))
  # while len(ans)!=n:
  #   t,d,sesid,act = heappop(heap)
  #   ans.append(act)
  #   nact = model.predict_from_prefix_case(
  #     sesid,
  #     trc.get_activities(),
  #     d+1,
  #     [ datetime.fromtimestamp(float(t)) for t in trc.get_timestamps() ])[d]
  #   heappush(heap, (nact[2], d+1, sesid, nact))
  # return ans

  # for sesid in session:
  #   trc = session[sesid]
  #   ans.extend(
  #     model.predict_from_prefix_case(
  #       sesid,
  #       trc.get_activities(),
  #       n,
  #       [ datetime.fromtimestamp(float(t)) for t in trc.get_timestamps() ]))
  # ans.sort(key = lambda x : x[2])
  # if (len(ans)>n):
  #   return ans[0:n]
  # return ans
  return ans


def model_initialization():
  '''returns model of prediction fitted with training data'''
  lstm = Lstm_model()
  lstm.generate_dict_activities()
  lstm.split(1.0)
  lstm.generate_sequences()
  lstm.get_dimensions()
  lstm.set_training_data()
  lstm.model_prediction()
  return lstm


def main():
  global session
  session = dict()
  line = stdin.readline()
  model = model_initialization()
  while line[0] != END:
    if line[0] == PRPRE:
      tok = line.split()
      tok = [x.strip() for x in tok]
      ans = predict(model, session, int(tok[1]), int(tok[2]))
      print(Trace.trace2maude(ans, len(ans)))
    else:
      tok = line.split(TRSEP)
      tok = [x.strip() for x in tok]
      sesid, actname, acttime = int(tok[0]), tok[1], Fraction(tok[2])
      if sesid not in session: session[sesid] = Trace(sesid)
      trc = session[sesid]
      extend(trc, actname, acttime)
    line = stdin.readline()


main()
