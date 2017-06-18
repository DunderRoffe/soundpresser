SoundPresser
============

SoundPresser is a program written in Python3 that reads a file source using
aubio and triggers keyboard presses. For instance this could be used to control
a video game using a guitar or write emails by singing in to a microphone.

License: GPLv3

Usage
-----
SoundPresser takes a json file that maps frequencies to keyboard actions. For
instance, look in example.json. It contains mappings from notes in different
octaves to the key representing the name of that note. In other words, 440 which
is the frequency of A4 is mapped to "a".

```json
{
    "440": "a"
}
```

Note: Some notes appear in two chunks. In these cases the second listed chunk
represents the sharp version of the note.

Dependencies
------------
* aubio
* pyuserinput
