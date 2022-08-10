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
 while(!Serial){;}
 car.Setup();
 car.Test(); 
}

//glowna petla
void loop() {
  if (Serial.available()){
    String cmd = Serial.readStringUntil(' ');
    
    if(cmd.startsWith("stop")){
      car.Stop;
    }
    
    else if(cmd.startsWith("move")){
      int spe=Serial.parseInt();
      int acc=Serial.parseInt();
      car.Move(spe,acce);
    }

    else if(cmd.startsWith("turn")){
      int ang=Serial.parseInt();
      int spe=Serial.parseInt();
      car.Turn(ang,spe);
    }
  }
  
}
