#include "MIDIUSB.h"

int trigger1 = 0;         // Used for the vibration sensor
int trigger2 = 0;         // Used to store trigger value from vibration sensor on D7
int trigger3 = 0;         // Used to store trigger value from vibration sensor on D8
int trigger4 = 0;         // Used to store trigger value from vibration sensor on D9

void setup(void) {
  Serial.begin(115200);
  while (!Serial)
    delay(10);  // will pause Zero, Leonardo, etc until serial console opens

  // Set up vibration sensor pins as inputs
  pinMode(6, INPUT);  // Vibration sensor 1
  pinMode(7, INPUT);  // Vibration sensor 2
  pinMode(8, INPUT);  // Vibration sensor 3
  pinMode(9, INPUT);  // Vibration sensor 4

  Serial.println("");  // Print a blank line for better readability
  delay(100);
}

void noteOn(byte channel, byte pitch, byte velocity) {
  midiEventPacket_t noteOn = { 0x09, 0x90 | channel, pitch, velocity };
  MidiUSB.sendMIDI(noteOn);
}

void noteOff(byte channel, byte pitch, byte velocity) {
  midiEventPacket_t noteOff = { 0x08, 0x80 | channel, pitch, velocity };
  MidiUSB.sendMIDI(noteOff);
}

void loop() {

  // Get vibration sensor input values (D7, D8, D9)
  trigger1 = digitalRead(6);  // Read vibration sensor 1
  trigger2 = !digitalRead(7);  // Read vibration sensor 2 (inverted logic)
  trigger3 = !digitalRead(8);  // Read vibration sensor 3 (horn, inverted logic)
  trigger4 = digitalRead(9);  // Read vibration sensor 4

  // Print trigger values to serial monitor
  Serial.print(trigger1);  // acc harp
  Serial.print(",");
  Serial.print(trigger2);  // zhen bell
  Serial.print(",");
  Serial.print(trigger3);  // mico horn
  Serial.print(",");
  Serial.println(trigger4);  // zhen drum

  // If vibration sensor 1 is triggered (HIGH)
  if (trigger1 == HIGH) {
    noteOn(0, 60, 64);  // Channel 1, Note 60 (Middle C), Velocity 64
    MidiUSB.flush();
    delay(500);         // Wait for 500ms
    noteOff(0, 60, 64);  // Channel 1, Note 60 (Middle C), Velocity 64
    MidiUSB.flush();
  }

  // If vibration sensor 2 is triggered (HIGH)
  if (trigger2 == HIGH) {
    noteOn(1, 62, 64);  // Channel 2, Note 62 (D), Velocity 64
    MidiUSB.flush();
    delay(500);         // Wait for 500ms
    noteOff(1, 62, 64);  // Channel 2, Note 62 (D), Velocity 64
    MidiUSB.flush();
  }

  // If vibration sensor 3 is triggered (HIGH)
  if (trigger3 == HIGH) {
    noteOn(2, 64, 64);  // Channel 3, Note 64 (E), Velocity 64
    MidiUSB.flush();
    delay(500);         // Wait for 500ms
    noteOff(2, 64, 64);  // Channel 3, Note 64 (E), Velocity 64
    MidiUSB.flush();
  }

  // If vibration sensor 4 is triggered (HIGH)
  if (trigger4 == HIGH) {
    noteOn(3, 65, 64);  // Channel 4, Note 65 (F), Velocity 64
    MidiUSB.flush();
    delay(500);         // Wait for 500ms
    noteOff(3, 65, 64);  // Channel 4, Note 65 (F), Velocity 64
    MidiUSB.flush();
  }

  delay(50);  // Small delay to debounce the input
}
