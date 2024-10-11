#include "AccelStepper.h"
#include "avr/sleep.h"
#include <Wire.h>
#define SLAVE_ADDRESS 0x04  // I2C address for Arduino

// Define stepper motor connections and motor interface type. Motor interface type must be set to 1 when using a driver:
#define dirPin 4
#define stepPin 5
#define SleepModePin 6
#define wakeUpPin 3
#define LedPin A3

// paramètres d'interruption ils
#define interrupt_pin 2
#define motorInterfaceType 1
volatile unsigned long button_time = 0;
volatile unsigned long last_button_time = 0;
int debounce = 1000;

//état de l'interrupteur ILS
bool state_auto = 0;
//état commandé par la Raspberry via i2c
bool state_i2c = 0;
//état de la connexion i2c
bool i2c_detected = false;
//indicateur de fin de rotation moteur
bool rotation_done = true;
//indicateur pour se mettre en deep sleep
bool goToSleep = 0;

// structures pour les infos i2c
int Data = 1;
int Data_indent = 0;
int i2cData[6] = {};

// paramètres rotation moteur transmissibles par la Raspberry
int number_of_revolutions = 10,
    max_speed = 150,
    max_acceleration = 150,
    pause_time = 5,
    step_mode = 4;  // 1 pour full_step, 2 pour 1/2 microstep, 4 pour 1/4 microstep, 16 pour 1/16 microstep etc

// Création d'une instance de classe AccelStepper:
AccelStepper stepper = AccelStepper(motorInterfaceType, stepPin, dirPin);

void setup() {
  pinMode(wakeUpPin, INPUT);
  pinMode(SleepModePin, OUTPUT);
  pinMode(LedPin, OUTPUT);
  digitalWrite(SleepModePin, LOW);  //au démarrage, on met le contrôleur moteur en mode sleep

  // Set the maximum speed and acceleration:
  stepper.setMaxSpeed(max_speed * step_mode * 10);
  stepper.setAcceleration(max_acceleration * step_mode * 10);
  stepper.disableOutputs();

  // définition de l'interruption liée à l'ILS pour déclencher le fonctionnement moteur indépendant
  attachInterrupt(digitalPinToInterrupt(interrupt_pin), change_state, RISING);

  // setup de la communication i2c avec la Raspberry
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);

  //setup communication série avec l'ordinateur
  //Serial.begin(9600);
}

void loop() {
  if (!i2c_detected & state_auto) {
    motorRotate();
    // Attente entre 2 rotations
    delay(pause_time * 1000);
  }

  if (i2c_detected) {
    if (state_i2c & !rotation_done) {
      motorRotate();
      rotation_done = true;
    }
    if (goToSleep) {
      goToSleep = 0;

      bool isAwake = 0;
      while (!isAwake) {
        attachInterrupt(digitalPinToInterrupt(wakeUpPin), wakeUp, HIGH);
        set_sleep_mode(SLEEP_MODE_PWR_DOWN);
        sleep_enable();
        sleep_cpu();
        detachInterrupt(digitalPinToInterrupt(wakeUpPin));
        delay(100);
        isAwake = digitalRead(wakeUpPin);
      }
    }
  }
}

void wakeUp() {}

// fonction appelée par l’interruption externe n°0
void change_state() {
  button_time = millis();
  if (button_time > last_button_time + debounce) {
    state_auto = !state_auto;  // inverse l’état de la variable
    last_button_time = button_time;
  }
}

// fonction appelée à la réception d'un octet i2c
void receiveData(int byteCount) {
  while (Wire.available()) {
    if (!i2c_detected) {
      i2c_detected = true;
      detachInterrupt(digitalPinToInterrupt(interrupt_pin));
    }
    Data = Wire.read();
    if (!Data) {
      Data_indent = 0;
    } else {
      i2cData[Data_indent] = Data;
      Data_indent += 1;
    }
    if (Data_indent == 6) {
      state_i2c = bool(i2cData[0] - 1);
      step_mode = i2cData[5];
      number_of_revolutions = i2cData[1];
      stepper.setMaxSpeed(i2cData[2] * step_mode * 10);
      stepper.setAcceleration(i2cData[3] * step_mode * 10);
      goToSleep = bool(i2cData[4] - 1);
      rotation_done = !state_i2c;
    }
  }
}

void motorRotate() {
  // led allumée
  digitalWrite(LedPin, HIGH);
  
  //désactivation du mode sleep du driver moteur
  digitalWrite(SleepModePin, HIGH);
  //définition de la prochaine position
  stepper.move(-400 * number_of_revolutions * step_mode); //le "-" qui définit le sens de rotation anti-horaire est important pour que les efforts axiaux sur la vis sans fin soient dirigés vers le moteur,
                                                          //ainsi la vis est contrainte contre le pignon moteur et ne se désengage pas.
  //déplacement jusqu'à la position précédemment définie, à la vitesse et accélération définie
  stepper.runToPosition();
  //réactivation du mode sleep
  digitalWrite(SleepModePin, LOW);

  //led éteinte
  digitalWrite(LedPin, LOW);
}

// fonction appelée par requête de la Raspberry
void sendData() {
  Wire.write(rotation_done);
}
