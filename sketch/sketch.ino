/*
  TCLab Temperature Control Lab Firmware
  Jeffrey Kantor
  January, 2018

  This firmware provides a high level interface to the Temperature Control Lab. The
  firmware scans the serial port for case-insensitive commands. Each command returns
  a result string.

  A         software restart. Returns "Start".
  P1 float  set pwm limit on heater 1, range 0 to 255. Default 200. Returns P1.
  P2 float  set pwm limit on heater 2, range 0 to 255. Default 100. Returns P2.
  Q1 float  set Heater 1, range 0 to 100. Returns value of Q1.
  Q2 float  set Heater 2, range 0 to 100. Returns value of Q2.
  R1        get value of Heater 1, range 0 to 100
  R2        get value of Heater 2, range 0 to 100
  T1        get Temperature T1. Returns value of T1 in deg C.
  T2        get Temperature T2. Returns value of T2 in deg C.
  VER       get firmware version string
  X         stop, enter sleep mode. Returns "Stop".

  Limits on the heater can be configured with the constants below.

  Status is indicated by LED1 on the Temperature Control Lab. Status conditions are:

      LED1        LED1
      Brightness  State
      ----------  -----
      dim         steady     Normal operation, heaters off
      bright      steady     Normal operation, heaters on
      dim         blinking   High temperature alarm on, heaters off
      bright      blinking   High temperature alarm on, heaters on

  The Temperature Control Lab shuts down the heaters if it receives no host commands
  during a timeout period (configure below), receives an "X" command, or receives
  an unrecognized command from the host.

  The constants can be used to configure the firmware.
*/

// constants
const String vers = "1.1.0";   // version of this firmware
const int baud = 9600;         // serial baud rate
const char sp = ' ';           // command separator
const char nl = '\n';          // command terminator

// pin numbers corresponding to signals on the TC Lab Shield
const int pinT1   = 0;         // T1
const int pinT2   = 2;         // T2
const int pinQ1   = 3;         // Q1
const int pinQ2   = 5;         // Q2
const int pinLED1 = 9;         // LED1

// temperature alarm limits expressed (units of pin values)
const int limT1   = 310;       // T1 high alarm (50 deg C)
const int limT2   = 310;       // T2 high alarm (50 deg C)

// LED1 levels
const int hiLED   =  60;       // hi LED
const int loLED   = hiLED/16;  // lo LED

// global variables
char Buffer[64];               // buffer for parsing serial input
int buffer_index = 0;          // index for Buffer
String cmd;                    // command 
int val;                       // command value
int ledStatus;                 // 1: loLED
                               // 2: hiLED
                               // 3: loLED blink
                               // 4: hiLED blink
float P1 = 200;                // heater 1 power limit in units of pwm. Range 0 to 255
float P2 = 100;                // heater 2 power limit in units in pwm, range 0 to 255
int Q1 = 0;                    // last value written to heater 1 in units of percent
int Q2 = 0;                    // last value written to heater 2 in units of percent
int alarmStatus;               // hi temperature alarm status
boolean newData = false;       // boolean flag indicating new command

void readCommand() {
  while (Serial && (Serial.available() > 0) && (newData == false)) {
    int byte = Serial.read();
    if ( (byte != '\r') && (byte != '\n') && (buffer_index < 64)) {
      Buffer[buffer_index] = byte;
      buffer_index++;
    }
    else {
      newData = true;
    }
  }
}

void echoCommand() {
  if (newData) {
    Serial.write("Received Command: ");
    Serial.write(Buffer, buffer_index);
    Serial.write("\r\n");
    Serial.flush();
  }
}

void parseCommand(void) {
  if (newData) {
    String read_ = String(Buffer);

    // separate command from associated data
    int idx = read_.indexOf(sp);
    cmd = read_.substring(0, idx);
    cmd.trim();
    cmd.toUpperCase();

    // extract data. toInt() returns 0 on error
    String data = read_.substring(idx + 1);
    data.trim();
    val = data.toFloat();

    // reset parameter for next command
    memset(Buffer, 0, sizeof(Buffer));
    buffer_index = 0;
    newData = false;
  }
}

void dispatchCommand(void) {
  if (cmd == "A") {
    setHeater1(0);
    setHeater2(0);
    Serial.println("Start");
  }
  else if (cmd == "P1") {
    P1 = max(0, min(255, val));
    Serial.println(P1);
  }
  else if (cmd == "P2") {
    P2 = max(0, min(255, val));
    Serial.println(P2);
  }
  else if (cmd == "Q1") {
    Q1 = max(0, min(100, val));
    setHeater1(Q1);
    Serial.println(Q1);
  }
  else if (cmd == "Q2") {
    Q2 = max(0, min(100, val));
    setHeater2(Q2);
    Serial.println(Q2);
  }
  else if (cmd == "R1") {
    Serial.println(Q1);
  }
  else if (cmd == "R2") {
    Serial.println(Q2);
  }
  else if (cmd == "T1") {
    float mV = (float) analogRead(pinT1) * (3300.0/1024.0);
    float degC = (mV - 500.0)/10.0;
    Serial.println(degC);
  }
  else if (cmd == "T2") {
    float mV = (float) analogRead(pinT2) * (3300.0/1024.0);
    float degC = (mV - 500.0)/10.0;
    Serial.println(degC);
  }
  else if (cmd == "VER") {
    Serial.println("TCLab Firmware Version " + vers);
  }
  else if ((cmd == "X") or (cmd.length() > 0)) {
    setHeater1(0);
    setHeater2(0);
    Serial.println(cmd);
  }
  Serial.flush();
  cmd = "";
}

void checkAlarm(void) {
  if ((analogRead(pinT1) > limT1) or (analogRead(pinT2) > limT2)) {
    alarmStatus = 1;
  }
  else {
    alarmStatus = 0;
  }
}

void updateStatus(void) {
  // determine led status
  ledStatus = 1;
  if ((Q1 > 0) or (Q2 > 0)) {
    ledStatus = 2;
  }
  if (alarmStatus > 0) {
    ledStatus += 2;
  }
  // update led depending on ledStatus
  if (ledStatus == 1) {               // normal operation, heaters off
    analogWrite(pinLED1, loLED);
  }
  else if (ledStatus == 2) {          // normal operation, heater on
    analogWrite(pinLED1, hiLED);
  }
  else if (ledStatus == 3) {          // high temperature alarm, heater off
    if ((millis() % 2000) > 1000) {
      analogWrite(pinLED1, loLED);
    } else {
      analogWrite(pinLED1, loLED/4);
    }
  }
  else if (ledStatus == 4) {          // hight temperature alarm, heater on
    if ((millis() % 2000) > 1000) {
      analogWrite(pinLED1, hiLED);
    } else {
      analogWrite(pinLED1, loLED);
    }
  }
}

// set Heater 1
void setHeater1(float qval) {
  analogWrite(pinQ1, qval*P1/100);
}

// set Heater 2
void setHeater2(float qval) {
  analogWrite(pinQ2, qval*P2/100);
}

// arduino startup
void setup() {
  analogReference(EXTERNAL);
  while (!Serial) {
    ; // wait for serial port to connect.
  }
  Serial.begin(baud); 
  Serial.flush();
  setHeater1(0);
  setHeater2(0);
}

// arduino main event loop
void loop() {
  readCommand();
  //echoCommand();
  parseCommand();
  dispatchCommand();
  checkAlarm();
  updateStatus();
}
