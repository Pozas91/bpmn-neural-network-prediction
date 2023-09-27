# Formal Modelling and Analysis of BPMN processes using Maude
# authors: Francisco Duran, Camilo Rocha, Gwen Salaun, and Nicolas Pozas

# Interaction between the BPMN process and the predictor

These modules specify the interaction betwen the BPMN process and the Predictor process.
The communication is carried on using sockets.
The Predictor object plays the role of the server, it is intended to attend requests from BPMN process analysis tool.
The BPMN process plays the role of the client.
It requests a connection on the server port and, once the connection is initiated, they interact as follows:
 1. The BPMN process sends events with the form "event(N, St, T)", where
   - N is a run identifier, a natural number between 0 a the number of actual executions,
   - St is a string with a description of the event, and
   - T is a time value, a rational number of the form 345/4523.
 2. Eventually, the BPMN process will send a "PREDICT\n" command, at which time it will expect a prediction sequence from the predictor process.
 3. The BPMN process expects a sequence of events, sent by the predictor process, in the same format, and terminated by an "END\n".
 4. Upon the end of the prediction sequence, the BPMN process re-takes the submission of the event self in 1.
 5. The interaction terminates when the BPMN process decides so, and does so sending an "END\n" to the predictor.

 A few aditional notes:

 - TCP sockets do not preserve message boundaries. That means that even though sents take only one event at a time, it may happen that received messages arrive with mixed strings. To simplify the handling of messages, we keep an incoming buffer in each of the sides, and use Receive-Received messages to split inputs. The idea is impired in the buffered sockets in the Maude manual (9.3.2), but simplified to get just what we needed.

 - Port 8811 is currently used, and processes are run in the same machine, but any other configuration might be used as well. There are constants IP and PORT in the COMMONS module.

 - To run the example, just open two terminals in your machine. In one of them run maude with the predictor module (it has the command initiating the process) 

   ~~~~
   > maude predictor.maude
   ~~~~

and in the other one run the bpmn process:

   ~~~~
   > maude bpmn.maude
   ~~~~

 - For the specification they do not interchange actual events. All events submitted for both of them have the form "event(token(RUN), task, TIME)\n"

 - The print attribute flag is set on, so as output of the execution you should see, in the predictor terminal,

    ~~~~~
    erewrite in PREDICTOR : <> PREDICTOR .
    ::: "event(token(RUN), task, TIME)\n"
    ...
    ::: "event(token(RUN), task, TIME)\n"
    ::: "PREDICT\n"
    ::: "event(token(RUN), task, TIME)\n"
    ...
    ::: "event(token(RUN), task, TIME)\n"
    ::: "PREDICT\n"
    ::: "event(token(RUN), task, TIME)\n"
    ...
    ::: "event(token(RUN), task, TIME)\n"
    ::: "END\n"
    ~~~~

and in the bpmn process side:

    ~~~~~
    erewrite in PREDICTOR : <> PREDICTOR .
    ::: "event(token(RUN), task, TIME)\n"
    ....
    ::: "event(token(RUN), task, TIME)\n"
    ::: "END\n"
    ::: "event(token(RUN), task, TIME)\n"
    ....
    ::: "event(token(RUN), task, TIME)\n"
    ::: "END\n"
    ::: "event(token(RUN), task, TIME)\n"
    ...
    ::: "event(token(RUN), task, TIME)\n"
    ::: "END\n"
    ~~~~
