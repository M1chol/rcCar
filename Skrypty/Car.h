class Car{

  //zmienne prywatne  
  //silnik
  int R_EN = 2;
  int R_PWM = 3;
  int L_EN = 4;
  int L_PWM = 5;
  int R_IS = 6;
  int L_IS = 7;

  //serwo
  Servo serv;                     // stworzenie objektu serwa
  int SRW = 9;                    // pin do ktorego podlaczone jest serwo

  public:
    //zmienne publiczne
    int pos = 90-serv_err;        // aktualna pozycja serwa
    int serv_err = 18;            // kat serwa aby kola byly prosto
    int carSpeed;                 // predkosc pojazdu
    int startingSpeed=10;         // predkosc minimalna
  
    void Setup(){
      pinMode(SRW, OUTPUT);
      serv.attach(SRW);           // podlaczenie serwa
      pinMode(R_IS, OUTPUT);      // wyjscie alarmu
      pinMode(R_EN, OUTPUT);      // zgoda na obrot
      pinMode(R_PWM, OUTPUT);     // obroty przod 0-256
      pinMode(L_IS, OUTPUT);      // wyjscie alarmu
      pinMode(L_EN, OUTPUT);      // zgoda na obrot
      pinMode(L_PWM, OUTPUT);     // obroty tyl 0-256
      digitalWrite(R_IS, LOW);
      digitalWrite(L_IS, LOW);
      digitalWrite(R_EN, HIGH);
      digitalWrite(L_EN, HIGH);
      carSpeed = 0;               // poczatkowa predkosc auta
      serv.write(pos);            // poczatkowa pozycja kol
    }
      
    void Turn(int angle, int turnSpeed){
      angle-=serv_err;
      if(angle==pos){
        return;
      }
      if(turnSpeed == 0){
        serv.write(angle);
        pos=angle;
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
    }

     void Stop(){
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
    
    void rapidMove(int toSpeed){
      if (abs(toSpeed)>startingSpeed){
        WriteSpeed(toSpeed);
        carSpeed=toSpeed;
      }
    }
    void rapidTurn(int angle){
        serv.write(angle);
        pos=angle;
    }
    
  
    void Move(int toSpeed, int acceleration){
      
      int toDir=toSpeed/abs(toSpeed);      
      int acceForm=500/acceleration;
      
      if(carSpeed==0){
        WriteSpeed(startingSpeed*toDir);
      }
      if(toSpeed == carSpeed){
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
      }
    }
    
    void Test(){
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
      Move(30,5);
      delay(2000);
      Stop();
      delay(2000);
      Move(-30,5);
      delay(2000);
      Stop();
    }
};
