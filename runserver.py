
# Some modules we need to use
import subprocess
import sys
import re

server = subprocess.Popen("java -Xmx2048M -Xms2048M -jar server.jar nogui", shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
twitch = subprocess.Popen("node twitch_chat.js", shell = True, stdout = subprocess.PIPE)

while True:
#  cmdline = sys.stdin.readline()[:-1]
#  print("Command: " + cmdline)

  # Get a single line from the Twitch chat
  line = twitch.stdout.readline().decode("utf-8")[:-1]

  if line != "":
    server.stdin.write(bytes("say <Twitch> " + line + "\r\n", "utf-8"))
    server.stdin.flush()    

  # Get a single line from the Minecraft server
  line = server.stdout.readline().decode("utf-8")[:-1]

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
        server.stdin.write(bytes(chatmsg[8:] + "\r\n", "utf-8"))
        server.stdin.flush()

# <Hexchild> Something I said

      print(chatter + ": " + chatmsg)



#      server.stdin.write(bytes("say foo\r", "utf-8"))
