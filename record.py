FILE_VERSION = 0

import argparse
parser  = argparse.ArgumentParser(description="Record some gameplay")
parser.add_argument('ip', default='localhost', help="The server's IP")
parser.add_argument('port', default=32887, type=int, help="The server's port")
parser.add_argument('file', default='replay.demo', help="File to save to")
args = parser.parse_args()

import struct
import enet
from time import time
con = enet.Host(None, 1, 1)
con.compress_with_range_coder()
peer = con.connect(enet.Address(args.ip, args.port), 1, 3)
with open(args.file, "wb") as fh:
	fh.write(struct.pack('B', FILE_VERSION))
	while True:
		try:
			event = con.service(0)
		except IOError:
			continue
		if event is None:
			continue
		elif event.type == enet.EVENT_TYPE_CONNECT:
			print('connected to server')
			start_time = time()
		elif event.type == enet.EVENT_TYPE_DISCONNECT:
			print('lost connection to server')
			break
		elif event.type == enet.EVENT_TYPE_RECEIVE:
			#print(hex(ord(event.packet.data[0])))
			fh.write(struct.pack('fH', time() - start_time, len(event.packet.data)))
			fh.write(event.packet.data)
