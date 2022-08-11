#include <Servo.h>
#include "Car.h"

Car car;

//dioda do debugowania
void diodeBlink(int num){
  for(int i=1; i<=num; i+=1){
    digitalWrite(LED_BUILTIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);
    delay(200);
  }
 }

//setup
void setup() {
 Serial.begin(9600);
 car.Setup();
 while(!Serial){;}
}

//glowna petla
void loop() {
  if (Serial.available()){
    String cmd = Serial.readStringUntil(' ');
    
    if(cmd.startsWith("stop")){
      car.Stop();
    }
    else if (cmd.startsWith("rMove")){
      int spe=Serial.parseInt();
      car.rapidMove(spe);
    }
    else if (cmd.startsWith("rTurn")){
      int ang = Serial.parseInt();
      car.rapidTurn(ang);
    }
    else if(cmd.startsWith("move")){
      int spe=Serial.parseInt();
      int acc=Serial.parseInt();
      car.Move(spe,acc);
    }
    else if(cmd.startsWith("turn")){
      int ang=Serial.parseInt();
      int spe=Serial.parseInt();
      car.Turn(ang,spe);
    }
    else if(cmd.startsWith("test")){
      car.Test();
  }
}
