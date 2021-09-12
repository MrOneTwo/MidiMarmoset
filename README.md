# MidiMarmoset

This is an attempt at using a midi controller with Marmoset Toolbag 4. It's not working right now because of
threading issue. Unfortunately the built-in Marmoset Toolbag callbacks fire so infrequently (several times
per second) that it's impossible to pop all the midi messages fast enough... adding a second thread for
parsing messages didn't help since it doesn't work atm.
