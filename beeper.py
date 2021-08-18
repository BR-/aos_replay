from __future__ import print_function

from array import array
from time import sleep

import pygame
from pygame.mixer import Sound, get_init, pre_init

pre_init(44100, -16, 1, 1024)
pygame.init()
import math
#https://gist.github.com/ohsqueezy/6540433
class Note(Sound):

    def __init__(self, frequency, volume=.1):
        self.frequency = frequency
        Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        sample_rate = pygame.mixer.get_init()[0]
        period = int(round(sample_rate / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(get_init()[1]) - 1) - 1
        for time in range(period):
            samples[time] = int(amplitude * math.sin(2 * 3.14159 * self.frequency * time / sample_rate))
        return samples
beep = Note(440)

import argparse
parser  = argparse.ArgumentParser(description="Beep beep beep beep beep")
parser.add_argument('ip', help="The server's IP")
parser.add_argument('port', type=int, nargs='?', default=-1, help="The server's port (default: 32887)")
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
peer = con.connect(enet.Address(bytes(args.ip, "utf-8"), args.port), 1, args.version)
times = [0]
try:
	while True:
		try:
			event = con.service(1000)
		except IOError:
			continue
		if event is None:
			continue
		elif event.type == enet.EVENT_TYPE_CONNECT:
			print('connected to server')
		elif event.type == enet.EVENT_TYPE_DISCONNECT:
			try:
				reason = ["generic error", "banned", "kicked", "wrong version", "server is full"][event.data]
			except KeyError:
				reason = "unknown reason (%s)" % event.data
			print('lost connection to server:', reason)
			break
		elif event.type == enet.EVENT_TYPE_RECEIVE:
			if event.packet.data[0] == 2: # world update
				beep.play(2)
				times.append(time())
				#print(time())
except KeyboardInterrupt:
	del times[0]
	with open("foo.txt", "w") as fh:
		fh.write("\n".join(map(str,times)))
