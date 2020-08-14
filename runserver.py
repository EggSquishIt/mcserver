
# Some modules we need to use
import subprocess
import sys
import re
import threading
import queue


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


# Generic function to run commands (from main window, player chat or Twitch chat)
def runcmd(user, cmd):
  print("Running command \"" + cmd + "\" by " + user)
  if cmd.startswith("server "):
    minecraft.send(cmd[7:] + "\r\n")

  if cmd.startswith("say "):
    minecraft.send("say " + cmd[4:] + "\r\n")

  if cmd == "gs":
    minecraft.send("give " + user + " glowstone\r\n")


# Infinite loop
while True:

  ##################### Direct console command stuff ######################

  # Get one line from text window (stdin of python program)
  line = stdin.getline()

  # Check that line is not empty
  if line != "":
    print("Got cmdline from main window: " + line)
    runcmd("server", line)


  ##################### Twitch chat stuff ######################

  # Get a single line from the Twitch chat
  line = twitch.getline()

  # Check that line is not empty
  if line != "":
    print("Got chat line from twitch: " + line)

    # Extract twitch chat info
    match = re.search("(.*): (.*)$", line)
    if match:
      # A chat message was received
      chatter = "twitch:" + match.group(1)
      chatmsg = match.group(2)

      minecraft.send("say <" + chatter + "> " + chatmsg + "\r\n")


  ##################### Server log stuff ######################

  # Get a single line from the Minecraft server
  line = minecraft.getline()

  # Check that line is not empty
  if line != "":
    print("Server: " + line)

    # Check if it's a chat message
    match = re.search("<(.*)> (.*)$", line)
    if match:
      # A chat message was received
      chatter = match.group(1)
      chatmsg = match.group(2)

      if chatmsg.startswith("!"):
        runcmd(chatter, chatmsg[1:])
