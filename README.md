# Ace of Spades Replay Recorder

This project is a demo recorder and playback of Ace of Spades games.

## Installation

### Prerequisites

#### PyEnet

If you've got a copy of PySpades or PySnip, you can copy the `enet` folder to your `aos_replay` folder, or copy the `aos_replay` files to your PySnip folder.

Otherwise, install PyEnet from [PyPi](https://pypi.python.org/pypi/pyenet) or [GitHub](https://github.com/aresch/pyenet).

## Usage

### Recording

The recording script runs as a game client. It connects to a server and saves everything to a file.  
It will take up a player slot on the server!

For example, to record aloha's hallway server, use the following command:  
`python record.py central.aloha.pk 32887 hallway.demo`

AoS 0.76 is supported as well:  
`python record.py -76 central.aloha.pk 31897 pinpoint.demo`

Close the window or press Ctrl-C to stop recording.

### Playback

The playback script runs as a game server. Connect with your Ace of Spades client, and it will be as if you joined the spectator team on the server you recorded, but in the future!

To replay the pinpoint recording made above:  
  
* Run `python playback.py pinpoint.demo 32888`
* Point your AoS client at `aos://16777343:32888`

Note that the playback script does not need to be told which AoS version to use, and that the port given is the port it will host the replay on (not the port that the record script used). 

While ingame, there are several commands:

* `pause` / `unpause` - stop and start the action
* `ff #` - fast forward (in seconds). Be careful going too far at once! (for example, OpenSpades will crash if it receives too many chat messages at once)
* `time` - sends chat messages telling you how far into the replay you are
* `spawn` - if you get stuck somehow, will respawn you as a spectator (should not be necessary)
* `id #` - if the script can't figure out what ID to give you, this might fix it (should not be necessary)

## Old Replays

Occasionally a breaking change will be made to the file format. There is currently no way to watch an old replay file without having an old copy of the playback script.