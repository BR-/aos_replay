from __future__ import print_function

VIEWER_PLAYER_ID = 31

import argparse
parser  = argparse.ArgumentParser(description="Playback some gameplay")
parser.add_argument('file', default='replay.demo', help="File to read from")
parser.add_argument('port', default=32887, type=int, help="The port to run on")
args = parser.parse_args()

class Client(object):
	def __init__(self, peer, fh, start_time):
		self.peer = peer
		self.fh = fh
		self.start_time = start_time
		self.get_next_packet()
		self.spawned = False
	def get_next_packet(self):
		meta = self.fh.read(8)
		if len(meta) < 8:
			raise EOFError("replay file finished")
		self.timedelta, size = struct.unpack("fi", meta)
		self.data = self.fh.read(size)
		if ord(self.data[0]) == 15: # state data
			self.data = self.data[0] + chr(VIEWER_PLAYER_ID) + self.data[2:] #overwrite player id with 32
import struct
import enet
from time import time
host = enet.Host(enet.Address('localhost', args.port), 128, 1)
host.compress_with_range_coder()
clients = {}
client_id = 0
while True:
	for cl in clients.values():
		while cl.start_time + cl.timedelta <= time():
			cl.peer.send(0, enet.Packet(cl.data, enet.PACKET_FLAG_RELIABLE))
			try:
				cl.get_next_packet()
			except EOFError:
				print(cl.peer.data, "finished playback")
				cl.peer.disconnect(0) #ERROR_UNDEFINED
				cl.fh.close()
				del clients[cl.peer.data]
				break
	try:
		event = host.service(0)
	except IOError:
		continue
	if event is None:
		continue
	elif event.type == enet.EVENT_TYPE_CONNECT:
		event.peer.data = str(client_id)
		client_id += 1
		clients[event.peer.data] = Client(event.peer, open(args.file, "rb"), time())
		print("received client connection", event.peer.data)
	elif event.type == enet.EVENT_TYPE_DISCONNECT:
		if event.peer.data in clients:
			clients[event.peer.data].fh.close()
			del clients[event.peer.data]
		print("lost client connection", event.peer.data)
	elif event.type == enet.EVENT_TYPE_RECEIVE:
		if not clients[event.peer.data].spawned:
			clients[event.peer.data].spawned = True
			pkt = struct.pack("bbbbfff16s", 12, VIEWER_PLAYER_ID, 1, -1, 255., 255., 1., "asd")
			event.peer.send(0, enet.Packet(pkt, enet.PACKET_FLAG_RELIABLE))
