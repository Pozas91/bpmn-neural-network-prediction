# Formal Modelling and Analysis of BPMN processes using Maude
# authors: Francisco Duran, Camilo Rocha, Gwen Salaun, and Nicolas Pozas

# How to execute the examples?

Located at the bpmn-neural-network-prediction/maude folder, just type 

  ~~~~
  maude examples/delivery/runs/bpmn-run-delivery-...
  ~~~~

completed by any of the files ready to execute the example with the different strategies and sample parameters.

If you want to run the ml-prediction-based strategy, you need to run the predictor in a separate terminal. 
The Maude process running the bpmn process specification and the python program executing the neural-network 
model communicate through sockets. Specifically, they assume they are both running on the same machine (local)
and used the port 8811. You can change this by assigning different values to the corresponding constants. 

Thus, you may run the two processes on corresponding terminals. The Python program assumes that the PYTHONPATH variable is set to the root of the project. If on a Mac, you may type 

  ~~~~
  % export PYTHONPATH=~/git/bpmn-neural-nework-prediction
  ~~~~

Then, if located at the root of the project (bpmn-neural-nework-prediction), you may run the python program with

  ~~~~
  % python3 maude/interaction/sockets+neural/predictor.py
  ~~~~

And then, in a second terminal, you can run the Maude process with 

  ~~~~
  % maude maude/examples/delivery/runs/bpmn-run-delivery-predictive-ml-usage.maude
  ~~~~

See other README files in the different subfolders to get further info. 

# Contents:

 - bpmn.maude contains the BPMN-SEM module with the specification of bpmn processes
 
 - bpmn-sockets.maude is exactly as bpmn.maude, but it sends events through a socket. It assumes a server socket running at localhost:8811 (see the socket-handler.maude file), on which creates a socket client and sends the events. 
 
 - supervisor-predictive-ml-usage.maude defines the supervisor. It operates as the supervisor in supervisor-predictive-usage, that is, every TBC time units creates a fork of the process, which runs for some time. Upon the completion of the execution, the resources are evaluated and the number of replicas updated. In supervisor-predictive-usage, the prediction run for some specific time (a timer was used), in this case a log-guided instance process is created, and the executions finishes when an END event is received. 
 
 - When the time for the predicction comes, creation events are submitted as if the process was executed. In this way, We could have new jobs in the prediction by letting the workload manager create new start events that we can put in the self. To make sure they won't be used in later predictions they must be consider as special events, e.g.: E1 E2 ... E1 predict [CE1 CE2 ... ]

# To dos:

- We can predict events in a running process, can we also predict workloads? New jobs should be arriving at differnet paces. 