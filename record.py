from __future__ import print_function

FILE_VERSION = 1

import argparse
parser  = argparse.ArgumentParser(description="Record some gameplay")
parser.add_argument('ip', help="The server's IP")
parser.add_argument('port', type=int, nargs='?', default=-1, help="The server's port (default: 32887)")
parser.add_argument('file', help="File to save to")
versiongroup = parser.add_mutually_exclusive_group()
versiongroup.add_argument('-75', action='store_const', dest='version', const=3, help="Use if the server is 0.75 (default)")
versiongroup.add_argument('-76', action='store_const', dest='version', const=4, help="Use if the server is 0.76")
parser.set_defaults(version=3)
args = parser.parse_args()

do_aos_conversion = args.ip.startswith("aos://")
if do_aos_conversion:
	args.ip = args.ip[6:]

if args.port == -1:
	try:
		ip, port = args.ip.rsplit(':', 1)
		args.port = int(port)
		args.ip = ip
	except ValueError:
		args.port = 32887

if do_aos_conversion:
	dec = int(args.ip)
	ip = ""
	for _ in range(4):
		ip += str(dec % 256) + "."
		dec //= 256
	if dec != 0:
		print("ERROR: AoS address not valid?")
		import sys
		sys.exit()
	args.ip = ip[:-1]

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
