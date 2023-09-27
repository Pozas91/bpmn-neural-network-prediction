import socketserver

# from code found at https://docs.python.org/3/library/socketserver.html
class Predictor(socketserver.StreamRequestHandler):
  """The request handler class for the server.

  It is instantiated once per connection to the server. It overrides
  the handle() method to implement communication to the client with
  streams, instead of the more common low-level direct socket reading.

  """
  __data = list()
  
  def handle(self):
    # self.rfile is a file-like object created by the handler;
    # one can use e.g. readline() instead of raw recv() calls
    ended = False
    print("{0} wrote:".format(self.client_address[0]))
    while not(ended):
      self.data = self.rfile.readline().strip()
      decdata = self.data.decode()
      print(':::', decdata)
      if decdata=='PREDICT':
        for _ in range(10):
          ans = 'event(token(RUN), task, TIME)\n'
          self.wfile.write(ans.encode('utf-8'))
        self.wfile.write('END\n'.encode('utf-8'))
      elif decdata=='END':
        ended = True
      elif len(decdata)!=0:
        self.__data.append(decdata)
  
if __name__ == "__main__":
  IP,PORT = 'localhost',8811
  # Create the server, binding to IP on port PORT
  with socketserver.TCPServer((IP, PORT), Predictor) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
