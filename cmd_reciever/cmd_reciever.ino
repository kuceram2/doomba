#include <Servo.h>

int pos = 10;
int camServoPin = 8;
int druheservo = 9;


int IN3 = 5;
int IN4 = 4;
int IN1 = 7;
int IN2 = 6;
int ENA = 3;
int ENB = 11;
int LED1 = 10;
int LED2 = 13;
int SPOTLIGHT = A0;

byte data;
int camPos = 90;
int speed = 100;
Servo servo;
Servo camServo;

int period = 500;
unsigned long timeActive = 0;

void setup() {
Serial.begin(9600);
pinMode(IN1,OUTPUT);
pinMode(IN2,OUTPUT);
pinMode(IN3,OUTPUT);
pinMode(IN4,OUTPUT);
pinMode(ENA,OUTPUT);
pinMode(ENB,OUTPUT);
pinMode(LED1, OUTPUT);
pinMode(LED2, OUTPUT);
pinMode(SPOTLIGHT, OUTPUT);

camServo.attach(camServoPin);
camServo.write(90);
}

void loop() {
  if(Serial.available()){
    data = Serial.read();
    move(data);

    //Serial.flush();
  }

  if(millis() - timeActive > period){
    analogWrite(ENA, 0);
    analogWrite(ENB, 0);
    digitalWrite(IN1,LOW);
    digitalWrite(IN2,LOW);
    digitalWrite(IN3,LOW);
    digitalWrite(IN4,LOW);
  }
}

void move(byte data){
  // pohyb dopředu
  if(data == 'w'){
  digitalWrite(IN1,LOW);
  digitalWrite(IN2,HIGH);
  digitalWrite(IN4,LOW);
  digitalWrite(IN3,HIGH);
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  timeActive = millis();
  }
  // pohyb doleva
  else if(data == 'a'){
  digitalWrite(IN1,LOW);
  digitalWrite(IN2,HIGH);
  digitalWrite(IN3,LOW);
  digitalWrite(IN4,HIGH);
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  timeActive = millis();
  }
  // pohyb dozadu
  else if(data == 's'){
  digitalWrite(IN2,LOW);
  digitalWrite(IN1,HIGH);
  digitalWrite(IN3,LOW);
  digitalWrite(IN4,HIGH);
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  timeActive = millis();
  }
  // pohyb doprava
  else if(data == 'd'){
  digitalWrite(IN2,LOW);
  digitalWrite(IN1,HIGH);
  digitalWrite(IN4,LOW);
  digitalWrite(IN3,HIGH);
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  timeActive = millis();
  }
  // kamera nahoru
  else if(data == 'n' and camPos < 135){
    camPos += 5;
    camServo.write(camPos);
    delay(20);
  }
  // kamera dolu
  else if(data == 'm' and camPos > 45){
    camPos -= 5;
    camServo.write(camPos);
    delay(20);
  }
  // změna rychlosti
  else if(data == 'r'){
    int val = Serial.readStringUntil('r').toInt();    
    speed = map(val, 0, 100, 100, 250);
  }
  // zapnout podsvícení
  else if(data == 't'){
    digitalWrite(LED1,HIGH);
    digitalWrite(LED2, HIGH);
  }
  // vypnout podsvícení
  else if(data == 'f'){
    digitalWrite(LED1,LOW);
    digitalWrite(LED2,LOW); 
  }
  // zapnout hledáček
  else if (data == 'g'){
    digitalWrite(SPOTLIGHT, HIGH);
  }
  // vypnout hledáček
  else if (data == 'h'){
    digitalWrite(SPOTLIGHT, LOW);
  }


}