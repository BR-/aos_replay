from __future__ import print_function
import sys

FILE_VERSION = 1

import argparse
parser  = argparse.ArgumentParser(description="Playback some gameplay")
parser.add_argument('file', default='replay.demo', help="File to read from")
args = parser.parse_args()

import struct
fh = open(args.file, "rb")

header_fmt = "BB"
header_fmtlen = struct.calcsize(header_fmt)
data = fh.read(header_fmtlen)
file_version, aos_version = struct.unpack(header_fmt, data)
if FILE_VERSION != file_version:
	if FILE_VERSION < file_version:
		print("This demo was recorded on a newer version of aos_replay.")
	elif FILE_VERSION > file_version:
		print("This demo was recorded on an older version of aos_replay.")
	print("aos_replay version: %d" % FILE_VERSION)
	print("Demo version: %d" % file_version)
	sys.exit(1)

print("Replay version:", file_version)
print("AoS version:", {3: "0.75", 4: "0.76"}[aos_version])

from collections import defaultdict
players = defaultdict(lambda: ("?", "?"))
team_names = defaultdict(lambda: "?")
team_names[0] = "Blue"
team_names[1] = "Green"
team_names[-1] = "Spectator"

meta_fmt = "fH"
meta_fmtlen = struct.calcsize(meta_fmt)

while True:
	meta = fh.read(meta_fmtlen)
	if len(meta) < meta_fmtlen:
		break
	timedelta, size = struct.unpack(meta_fmt, meta)
	data = fh.read(size)
	packetid = ord(data[0])
	if packetid == 12: #create player
		_, pid, _, team, _, _, _ = struct.unpack("<BBBbfff", data[:struct.calcsize("<BBBbfff")])
		name = data[struct.calcsize("<BBBbfff"):].rstrip('\0').decode('cp437', 'replace')
		players[pid] = (team_names[team], name)
		print("{0:.0f}\t({2} has joined {1} team)".format(timedelta, *players[pid]))
	elif packetid == 15: #state data
		_, _, _, _, _, _, _, _, _, _, _, team1, team2, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = struct.unpack("<BBBBBBBBBBB10s10sBBBBBffffffffffff", data)
		team_names[0] = team1.rstrip('\0').decode('cp437', 'replace')
		team_names[1] = team2.rstrip('\0').decode('cp437', 'replace')
	elif packetid == 17: #chat msg
		_, pid, type = struct.unpack("BBB", data[:3])
		msg = data[struct.calcsize("BBB"):].rstrip('\0').decode('cp437', 'replace')
		if type == 0: #all chat
			print("{:.0f}\t[{}] {}: {}".format(timedelta, *(players[pid] + (msg,))))
		elif type == 1: #team chat - not supported by current recorder, but best to plan ahead
			print("{:.0f}\t(TEAM) [{}] {}: {}".format(timedelta, *(players[pid] + (msg,))))
		elif type == 2: #system msg
			print("{:.0f}\t[SYSTEM] {}".format(timedelta, msg))

print("{:.0f}\treplay file finished".format(timedelta))