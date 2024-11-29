#include "MIDIUSB.h"

// First parameter is the event type (0x09 = note on, 0x08 = note off).
// Second parameter is note-on/note-off, combined with the channel.
// Channel can be anything between 0-15. Typically reported to the user as 1-16.
// Third parameter is the note number (48 = middle C).
// Fourth parameter is the velocity (64 = normal, 127 = fastest).

void noteOn(byte channel, byte pitch, byte velocity) {
  midiEventPacket_t noteOn = {0x09, 0x90 | channel, pitch, velocity};
  MidiUSB.sendMIDI(noteOn);
}

void noteOff(byte channel, byte pitch, byte velocity) {
  midiEventPacket_t noteOff = {0x08, 0x80 | channel, pitch, velocity};
  MidiUSB.sendMIDI(noteOff);
}

void setup() {
  Serial.begin(115200);
  // Wait for the serial monitor to open
  while (!Serial) delay(10);
}

void loop() {
  Serial.println("Sending note on");

  // Channel 0 (MIDI Channel 1), middle C (note 60), normal velocity
  noteOn(0, 60, 64);   
  MidiUSB.flush();  // Ensure MIDI data is sent
  delay(500);

  Serial.println("Sending note off");
  noteOff(0, 60, 64);  
  MidiUSB.flush();  // Ensure MIDI data is sent
  delay(1500);

  Serial.println("Sending note on");
  // Channel 1 (MIDI Channel 2), middle C (note 60), normal velocity
  noteOn(1, 60, 64);   
  MidiUSB.flush();  // Ensure MIDI data is sent
  delay(500);

  Serial.println("Sending note off");
  noteOff(1, 60, 64);  
  MidiUSB.flush();  // Ensure MIDI data is sent
  delay(1500);
}
