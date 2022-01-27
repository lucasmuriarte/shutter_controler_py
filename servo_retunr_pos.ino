/* Servo motor with Arduino example code. Position and sweep. More info: https://www.makerguides.com/ */
// Include the servo library:
#include <Servo.h>
// Create a new servo object:
Servo myservo;
Servo irrservo;
Servo aliservo;
// Define the servo pin:
#define aliPinirr 10
#define servoPin 9
#define servoPinirr 8


// Create a variable to store the servo position:
int angle = 0;

// Create a variable to store the LED position:
String message;
int pos;


void setup() {
  // put your setup code here, to run once:
  myservo.attach(servoPin);
  irrservo.attach(servoPinirr);
  aliservo.attach(aliPinirr);
  Serial.begin(9600);
  // Attach the Servo variable to a pin:
  myservo.write(0);
  irrservo.write(0);
  aliservo.write(0);
  delay(250);
}

void loop() {
// put your main code here, to run repeatedly:
  if (Serial.available()>0){
    message = Serial.readStringUntil('\n');
    if (message == "OO"){
      myservo.write(90);
      Serial.print("SHUTTERDRIVER");
    }
    if (message == "OFF1"){
      myservo.write(0);
      pos = myservo.read();
      Serial.print(pos);
    }
    if (message == "ON1"){
      myservo.write(90);
      pos = myservo.read();
      Serial.print(pos);
    }
    if (message == "OFF2"){
      irrservo.write(0);
      pos = irrservo.read();
      Serial.print(pos);
    }
    if (message == "ON2"){
      irrservo.write(90);
      pos = irrservo.read();
      Serial.print(pos);
    }
    if (message == "OFF3"){
      aliservo.write(0);
      pos = aliservo.read();
      Serial.print(pos);
    }
    if (message == "ON3"){
      aliservo.write(90);
      pos = aliservo.read();
      Serial.print(pos);
    }
   delay(10);
  }
}
