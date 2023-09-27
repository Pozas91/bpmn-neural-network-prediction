# BPMN Neural Network Prediction

## Formal Modelling and Analysis of BPMN processes using Maude
## authors: Francisco Duran, Camilo Rocha, Gwen Salaun, and Nicolas Pozas

  A significant task in business process optimization is concerned
  with streamlining the allocation and sharing of resources.
  This project analyzes business process
  provisioning under a resource prediction strategy based on deep
  learning.
  A timed and probabilistic rewrite theory specification formalizes
  the semantics of business processes. It is integrated with an
  external oracle in the form of a long short-term memory neural
  network that can be queried to predict how traces of the process may
  advance within a time frame.
  The repository includes several case studies, as well as details
  on their deep learning models and Maude
  integration.

### Execute neural model prediction
1. Run maude example
2. Run python ./maude/interaction/sockets+neural/predictor.py
3. Both programs start to communicate!