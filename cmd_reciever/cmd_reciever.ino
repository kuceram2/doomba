#include <Servo.h>

// int trigger = 5;
// int echo = 6;
int pos = 10;
int camServoPin = 8;


int IN3 = 5;
int IN4 = 4;
int IN1 = 7;
int IN2 = 6;
int ENA = 3;
int ENB = 11;
int LED1 = 10;
int LED2 = 13;

byte data;
long time; // čas od vyslání signálu
int distance; // vypočítaná vzdálenost
//int period = 200; // doba pohybu
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
// pinMode(trigger,OUTPUT);
// pinMode(echo,INPUT);
//pinMode(IN4,OUTPUT);

//servo.attach(3);
//servo.write(0);
camServo.attach(camServoPin);
camServo.write(90);
delay(3000);
}

void loop() {
  if(Serial.available()){
    data = Serial.read();
    //Serial.println(String(data));
    move(data);

    //Serial.flush();
  }

  if(millis() - timeActive > period){
    analogWrite(ENA, 0);
    analogWrite(ENB, 0);
    digitalWrite(IN2,LOW);
    digitalWrite(IN3,LOW);
    digitalWrite(IN1,LOW);
    digitalWrite(IN4,LOW);
    //Serial.println("stop");
  }
}

void move(byte data){
  if(data == 'w'){
  //Serial.println(speed);
  digitalWrite(IN1,LOW);
  digitalWrite(IN2,HIGH);
  digitalWrite(IN4,LOW);
  digitalWrite(IN3,HIGH);
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  timeActive = millis();
  // delay(period);
  // digitalWrite(IN2,LOW);
  // digitalWrite(IN3,LOW);
  // analogWrite(ENA, 0);
  // analogWrite(ENB, 0);
  }

  else if(data == 'a'){
  digitalWrite(IN1,LOW);
  digitalWrite(IN2,HIGH);
  digitalWrite(IN3,LOW);
  digitalWrite(IN4,HIGH);
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  timeActive = millis();
  // delay(period);
  // digitalWrite(IN2,LOW);
  // digitalWrite(IN4,LOW);
  // analogWrite(ENA, 0);
  // analogWrite(ENB, 0);
  }

  else if(data == 's'){
  digitalWrite(IN2,LOW);
  digitalWrite(IN1,HIGH);
  digitalWrite(IN3,LOW);
  digitalWrite(IN4,HIGH);
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  timeActive = millis();
  // delay(period);
  // digitalWrite(IN1,LOW);
  // digitalWrite(IN4,LOW);
  // analogWrite(ENA, 0);
  // analogWrite(ENB, 0);
  }

  else if(data == 'd'){

  digitalWrite(IN2,LOW);
  digitalWrite(IN1,HIGH);
  digitalWrite(IN4,LOW);
  digitalWrite(IN3,HIGH);
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  timeActive = millis();
  // delay(period);
  // digitalWrite(IN1,LOW);
  // digitalWrite(IN3,LOW);
  // analogWrite(ENA, 0);
  // analogWrite(ENB, 0);
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

  else if(data == 'r'){
    //Serial.println((char) data);
    int val = Serial.readStringUntil('r').toInt();
    //Serial.println(val);
    
    speed = map(val, 0, 100, 100, 255);
    //Serial.println(speed);
  }

  else if(data == 't'){
    digitalWrite(LED1,HIGH);
    digitalWrite(LED2, HIGH);
  }

  else if(data == 'f'){
    digitalWrite(LED1,LOW);
    digitalWrite(LED2,LOW); 
  }


}