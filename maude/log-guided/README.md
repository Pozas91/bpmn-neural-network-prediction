# Formal Modelling and Analysis of BPMN processes using Maude
# authors: Francisco Duran, Camilo Rocha, Gwen Salaun, and Nicolas Pozas

This folder contains files to make the process run guided by a sequence of events received from a socket. 
Since it expects a socket server running, you may run one on a terminal, for example, the file in maude/interaction/file-socket would read a self (for the delivery example) from a csv file and will send it through socket connections it listens to

~~~~
  maude file-to-socket-server.maude -trust
~~~~

Once the server is running (at localhost, port 8811), you can run the log-guided bpmn process in this forlder as 

~~~~
  maude bpmn-log-guided-run.maude 
~~~~

Note that 
 - This spec goes until the end of the self, when no further events are available (socket closed and events list is empty) it stops
 - Events for which no resources are available are shifted (as for tokens)
 - A similar shifting was written for events with no corresponding tokens, but the code is currently commented out; it was introduced as a way to handle non-executable predictions, but situations in which events with corresponding tokens not being yet available were detected (the specific case that was seen was a loop in which events for several iterations of the loop were left un-used, jumping directly to a end task)
 - Initially, the global time was updated as dictated by the events' time, but shifting of events led to situations in which time went backwards. To avoid this situation the maximum time (global time, event time, and token time) is taken to update