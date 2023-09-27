# Formal Modelling and Analysis of BPMN processes using Maude
# authors: Francisco Duran, Camilo Rocha, Gwen Salaun, and Nicolas Pozas

The file-socket folder contains specs preparing the implementation of the interaction between processes. The idea is that the Maude process sends the self through a socket and gets a prediction through a different socket. The self sending is already working, but, in preparation for that interaction, we need to prepare the second part, making the process being able to read a self/prediction from a socket and advance its execution following it. 

- file-to-socket and socket-server go together

  - file-to-socket specifies an object that reads a self from a file self.csv and sends it through a socket. It opens a file to read from it, and creates a client TCP socket to send its readings to it. 

  - socket-server specifies a socket server that accepts connections, and reads traces through them.

- file-to-socket-server and socket-client go together, they work as before, but now is the server who reads the file and accepts connections from a client who receives the data. 

  - file-to-socket-server specifies an object that reads a self from a file self.csv and sends it through a socket. It creates a socket server, opens a file to read from, and accepts socket clients to send its readings to it. 

  - socket-client specifies a socket client that reads traces through it.
