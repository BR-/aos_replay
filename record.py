from __future__ import print_function

FILE_VERSION = 1

import argparse
parser  = argparse.ArgumentParser(description="Record some gameplay")
parser.add_argument('ip', default='localhost', help="The server's IP")
parser.add_argument('port', default=32887, type=int, help="The server's port")
parser.add_argument('file', default='replay.demo', help="File to save to")
versiongroup = parser.add_mutually_exclusive_group()
versiongroup.add_argument('-75', action='store_const', dest='version', const=3, help="Use if the server is 0.75 (default)")
versiongroup.add_argument('-76', action='store_const', dest='version', const=4, help="Use if the server is 0.76")
parser.set_defaults(version=3)
args = parser.parse_args()

import struct
import enet
from time import time
con = enet.Host(None, 1, 1)
con.compress_with_range_coder()
peer = con.connect(enet.Address(args.ip, args.port), 1, args.version)
with open(args.file, "wb") as fh:
	fh.write(struct.pack('BB', FILE_VERSION, args.version))
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
			try:
				reason = ["generic error", "banned", "kicked", "wrong version", "server is full"][event.data]
			except KeyError:
				reason = "unknown reason (%s)" % event.data
			print('lost connection to server:', reason)
			break
		elif event.type == enet.EVENT_TYPE_RECEIVE:
			#print(hex(ord(event.packet.data[0])))
			fh.write(struct.pack('fH', time() - start_time, len(event.packet.data)))
			fh.write(event.packet.data)
