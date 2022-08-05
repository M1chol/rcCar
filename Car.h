class Car{

  //zmienne prywatne

  //pinMode(LED_BUILTIN, OUTPUT);
  
  //silnik
  int R_EN = 2;
  int R_PWM = 3;
  int L_EN = 4;
  int L_PWM = 5;
  int R_IS = 6;
  int L_IS = 7;

  //serwo
  
  Servo serv; // stworzenie objektu serwa
  int SRW = 9; // pin do ktorego podlaczone jest serwo

  public:
    //zmienne publiczne
    int pos = 90-serv_err; // aktualna pozycja serwa
    int serv_err = 18; // kat serwa aby kola byly prosto
    int carSpeed;
    int startingSpeed=10;
  
    void Setup(){
      Serial.println("Starting");
      pinMode(SRW, OUTPUT);
      serv.attach(SRW); // podlaczenie serwa
      serv.write(pos); //poczatkowa pozycja kol
      pinMode(R_IS, OUTPUT);
      pinMode(R_EN, OUTPUT);
      pinMode(R_PWM, OUTPUT); // obroty przod 0-256
      pinMode(L_IS, OUTPUT); //
      pinMode(L_EN, OUTPUT); //
      pinMode(L_PWM, OUTPUT); // obroty tyl 0-256
      digitalWrite(R_IS, LOW);
      digitalWrite(L_IS, LOW);
      digitalWrite(R_EN, HIGH);
      digitalWrite(L_EN, HIGH);
      carSpeed = 0;
    }
      
    void Turn(int angle, int turnSpeed){
      angle-=serv_err;
      if(angle==pos){
        Serial.println(pos+serv_err);
        return;
      }
      if(turnSpeed == 0){
        serv.write(angle);
        pos=angle;
        Serial.println(pos+serv_err);
        return;
      }
      int dist=abs(angle-pos);
      int turnTime=turnSpeed/dist;
      
      if(angle>pos){
        for(pos;pos<angle;pos++){
          serv.write(pos);
          delay(turnTime);  
        }
      }else{
        for(pos;pos>angle;pos--){
          serv.write(pos);
          delay(turnTime);
        }
      }
      Serial.println(pos+serv_err);
    }

     void Stop(){
      Serial.println("Stoping");
      analogWrite(R_PWM, 0);
      analogWrite(L_PWM, 0);
      carSpeed=0;
    }
    
    void WriteSpeed(int Speed){
        Serial.println(Speed);
        if (Speed==0){
          Stop();
        }
        if (Speed>0){
          analogWrite(R_PWM, Speed);
        }else{
          analogWrite(L_PWM, abs(Speed));
        }
        carSpeed=Speed;
      }
    
    void Move(int toSpeed, int acceleration){
      
      int toDir=toSpeed/abs(toSpeed);
      if(toDir==1){
        Serial.println("Moving Forward");
      }else{
        Serial.println("Moving Backward");
      }
      
      int acceForm=500/acceleration;
      
      if(carSpeed==0){
        WriteSpeed(startingSpeed*toDir);
      }
      if(toSpeed == carSpeed){
        Serial.println("Same speed");
        return;
      }
      int dir=toDir;
      if(carSpeed>toSpeed && toDir==1){
        dir=-1*toDir;
      }
      //przyspieszanie
      if(dir==1){
        for(int i=carSpeed; i<=toSpeed; i+=acceleration*dir){
          WriteSpeed(i);
          delay(acceForm);
        }
      }
      //zwalnianie / cofanie
      else{
        for(int i=carSpeed; i>=toSpeed; i+=acceleration*dir){
          WriteSpeed(i);
          delay(acceForm);
        }
      }
      if (carSpeed!=toSpeed){
        WriteSpeed(toSpeed);
        Serial.println("Div_err, snapping speed");
      }
    }
    void Test(){
      Serial.print("Testing Servo");
      delay(1000);
      Turn(60,0);
      delay(500);
      Turn(90,0);
      delay(500);
      Turn(120,0);
      delay(500);
      Turn(90,0);
      delay(500);
      Turn(50,1);
      delay(500);
      Turn(130,1);
      delay(1000);
      Turn(90,0);
      delay(1000);

      Serial.println("Testing Engine");
      Move(50,5);
      delay(200);
      Move(20,2);
      delay(1000);
      Stop();
      delay(2000);
      Move(-30,2);
      delay(3000);
      Stop();
    }
};
