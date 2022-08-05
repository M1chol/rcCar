#include <Servo.h>
#include "Car.h"

//piny

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
 Serial.println(car.pos);
 car.Test();
 
}

//glowna petla
void loop() {
  
  
}
