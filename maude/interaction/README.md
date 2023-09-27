# Formal Modelling and Analysis of BPMN processes using Maude
# authors: Francisco Duran, Camilo Rocha, Gwen Salaun, and Nicolas Pozas

This folder contains several attempts to make the interaction between a Maude process
and a neural-network-based predictor interact to be able to define an adaptable
strategy for the assignment of resources to bpmn processes.

- file-socket contains files for a preliminary attempt on moving from files into sockets
- files contains a failed attempt of using files to communicate between the Maude
  and the python prediction
- sandbox contains output files
- sockets contains files for an intermediate implementation in which both the  
  the bpmn process and the predictor communicate through sockets, but in which
  the predictor is written in maude
- sockets-interaction contains the final implementation of the interaction.  
  A Maude spec specifies the interaction with the python object so that the
  intermediate implementation in sockets is still usable.
