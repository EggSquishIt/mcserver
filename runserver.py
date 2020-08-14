
# Some modules we need to use
import subprocess
import sys
import re
import threading
import queue

#server = subprocess.Popen("java -Xmx1024M -Xms1024M -jar server.jar nogui", shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
#twitch = subprocess.Popen("node twitch_chat.js", shell = True, stdout = subprocess.PIPE)


class SimpleProcess(threading.Thread):
  def __init__(self, cmdline):
    threading.Thread.__init__(self)
    self.queue = queue.Queue()
    self.program = subprocess.Popen(cmdline, shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
    self.start()

  def run(self):
    while True:
      line = self.program.stdout.readline().decode("utf-8")[:-1]
      self.queue.put(line)

  def getline(self):
    try:
      return self.queue.get(block = False)
    except:
      return ""

  def send(self, line):
    self.program.stdin.write(bytes(line, "utf-8"))
    self.program.stdin.flush()



class SimpleStdin(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.queue = queue.Queue()
    self.start()

  def run(self):
    while True:
      line = sys.stdin.readline()[:-1]
      self.queue.put(line)

  def getline(self):
    try:
      return self.queue.get(block = False)
    except:
      return ""


twitch = SimpleProcess("node twitch_chat.js")
minecraft = SimpleProcess("java -Xmx1024M -Xms1024M -jar server.jar nogui")
stdin = SimpleStdin()


# Infinite loop
while True:

  ##################### Direct console command stuff ######################

  # Get one line from text window (stdin of python program)
  cmdline = stdin.getline()
  if cmdline != "":
    print("Command: " + cmdline)


  ##################### Twitch chat stuff ######################

  # Get a single line from the Twitch chat
  line = twitch.getline()

  if line != "":
    minecraft.send("say <Twitch> " + line + "\r\n")


  ##################### Server log stuff ######################

  # Get a single line from the Minecraft server
  line = minecraft.getline()

  # Check that line is not empty
  if line != "":
    print("Server: " + line)

    # Check if it's a chat message
    match = re.search("<(.*)> (.*)$", line)
    if match:
      chatter = match.group(1)
      chatmsg = match.group(2)

      if chatmsg.startswith("!server "):
        print("Server command by " + chatter + ": " + chatmsg[8:])
        minecraft.send(chatmsg[8:] + "\r\n")

      print(chatter + ": " + chatmsg)

