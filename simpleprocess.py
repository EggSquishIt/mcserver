import subprocess
import sys
import threading
import queue


class SimpleProcess(threading.Thread):
	def __init__(self, cmdline, cwd = "."):
		threading.Thread.__init__(self)
		self.queue = queue.Queue()
		self.program = subprocess.Popen(cmdline, shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE, cwd = cwd)
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
