# Clean Up A USB Thumb Drive

Honda's audio system is awfully brittle against macOS metadata:
Just the _presence_ of dotfiles seems to prevent the audio system
from recognizing and playing music from a USB drive.
This script/package provides a script `cleanusb` that removes
the stuff that was confusing my car's audio engine.

Specifically, the tool:

* Removes `LOST.DIR`
* Removes `.Spotlight-V100` (**NOTE: This requires `sudo`**)
* Applies `dot_clean` to deal with macOS-native resources.
* Removes additional dotfiles and directories, like `.DS_Store`, `.fseventsdb/`, et al.
* Organizes the music into an *Album* / *Artist* directory structure.

## Installation

```sh
$ git clone
pip install .
```

The script requires Python 3.10+, but only because that's what I'm using at the moment.
It could certainly be pushed down a few versions.

## Development

The project uses Poetry, so just `poetry install` to get started.
