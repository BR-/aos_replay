from __future__ import print_function

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
		self.pause_time = 0
		self.get_next_packet()
		self.spawned = False
		self.spam_time = False
		self.playerinfo = [[0,0] for _ in range(32)]
		self.playerid = None
	def get_next_packet(self):
		meta = self.fh.read(8)
		if len(meta) < 8:
			raise EOFError("replay file finished")
		self.timedelta, size = struct.unpack("fi", meta)
		self.data = self.fh.read(size)
		if ord(self.data[0]) == 15: # state data
			self.playerid = ord(self.data[1])
import struct
import enet
from time import time
host = enet.Host(enet.Address('localhost', args.port), 128, 1)
host.compress_with_range_coder()
clients = {}
client_id = 0
while True:
	for cl in clients.values():
		if cl.pause_time > 0:
			continue
		if cl.spam_time:
			pkt = struct.pack("bbb", 17, 35, 2) + str(cl.timedelta).encode('cp437', 'replace') #chat message
			cl.peer.send(0, enet.Packet(pkt, enet.PACKET_FLAG_RELIABLE))
		while cl.start_time + cl.timedelta <= time():
			if ord(cl.data[0]) == 3: #input data
				player, data = struct.unpack("xbb", cl.data)
				cl.playerinfo[player][0] = data
			elif ord(cl.data[0]) == 4: #weapon data
				player, data = struct.unpack("xbb", cl.data)
				cl.playerinfo[player][1] = data
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
		cl = clients[event.peer.data]
		if not cl.spawned:
			if cl.playerid is None:
				print("error: could not figure out player id, guessing! use the command 'id X' to fix")
				cl.playerid = 0
			cl.spawned = True
			pkt = struct.pack("bbbbfff16s", 12, cl.playerid, 1, -1, 255., 255., 1., "")
			event.peer.send(0, enet.Packet(pkt, enet.PACKET_FLAG_RELIABLE))
		elif ord(event.packet.data[0]) == 17:
			chat = event.packet.data[3:-1].decode('cp437', 'replace')
			if chat == "spawn":
				if cl.playerid is None:
					print("error: could not figure out player id, guessing! use the command 'id X' to fix")
					cl.playerid = 0
				cl.spawned = True
				pkt = struct.pack("bbbbfff16s", 12, cl.playerid, 1, -1, 255., 255., 1., "asd") #create player
				event.peer.send(0, enet.Packet(pkt, enet.PACKET_FLAG_RELIABLE))
			elif chat[:3] == "id ":
				try:
					playerid = int(chat[3:])
				except:
					pass
				else:
					cl.playerid = playerid
			elif chat == "pause" and cl.pause_time == 0:
				cl.pause_time = time()
				for i in range(32):
					pkt = struct.pack("bbb", 3, i, 0) #input data
					event.peer.send(0, enet.Packet(pkt, enet.PACKET_FLAG_RELIABLE))
					pkt = struct.pack("bbb", 4, i, 0) #weapon data
					event.peer.send(0, enet.Packet(pkt, enet.PACKET_FLAG_RELIABLE))
			elif chat == "unpause" and cl.pause_time > 0:
				cl.start_time += time() - cl.pause_time
				cl.pause_time = 0
				for i in range(32):
					pkt = struct.pack("bbb", 3, i, cl.playerinfo[i][0]) #input data
					event.peer.send(0, enet.Packet(pkt, enet.PACKET_FLAG_RELIABLE))
					pkt = struct.pack("bbb", 4, i, cl.playerinfo[i][1]) #weapon data
					event.peer.send(0, enet.Packet(pkt, enet.PACKET_FLAG_RELIABLE))
			elif chat[:3] == "ff ":
				try:
					skip = int(chat[3:])
				except:
					pass
				else:
					cl.start_time = cl.start_time - skip
			elif chat == "time":
				cl.spam_time = not cl.spam_time
