/*
    When pulseIn command is waiting for input main loop is blocked hence our loop will be slow.
    We can use interrupts for faster loop (interrupts are non blocking).
    But arduino Nano only supports 2 pin for interrupts (2, 3). Since we have 3 channels + 1 channel for encoder = 4 we have to use
    pulseIn. If ypu want to get true 100+ fps you have to use Arduino Micro it has 5 interrupt usable pin.

*/

#include <Servo.h>
#include <Ewma.h>

#define CH1_PIN 3
#define CH2_PIN 5
#define CH3_PIN 6
#define ESC_PIN 9
#define Servo_PIN 10
#define ENCODER_PIN 2

// Rc receiver filters (Exponentially Weighted Moving Average)
Ewma Steering_Filter(0.5);
Ewma Thorttle_Filter(0.2);
Ewma Encoder_Filter(0.15);

Servo throttle;
Servo steering;

String pyserial_data;
int pyserial_throttle, pyserial_steering;
int steering_value, throttle_value, ch3_value, mode_button;

volatile long Ch1_StartTime = 0;
volatile long Ch1_CurrentTime = 0;
volatile long Ch1_Pulses = 1500;
int Ch1_PulseWidth = 0;

unsigned long current_time;
unsigned long serialOut_last_time;
unsigned long encoder_last_time;
unsigned int pulses = 0;
float dpulses = 0;


int readChannel(int channelInput, int defaultValue);
void Ch1_PulseTimer();

void setup() {
    pinMode(CH1_PIN, INPUT);
    pinMode(CH2_PIN, INPUT);
    pinMode(CH3_PIN, INPUT);
    pinMode(ENCODER_PIN, INPUT);
    throttle.attach(ESC_PIN);
    steering.attach(Servo_PIN);
    attachInterrupt(digitalPinToInterrupt(CH1_PIN), Ch1_PulseTimer, CHANGE);
    attachInterrupt(digitalPinToInterrupt(ENCODER_PIN), []{pulses++;}, FALLING);
    Serial.begin(115200);
}

void loop() {
    current_time = millis();
    // Reading serial input
    // Serial inputs shape: s(float)t(float)e
    if(Serial.available() > 0) {
        pyserial_data =  Serial.readStringUntil('\r');
        int deliminator_index = 0;
        if (pyserial_data[0] == 's'){
            for (int i = 1; i < pyserial_data.length(); i++) {
                if (pyserial_data[i] == 't'){
                    pyserial_steering = pyserial_data.substring(1, i).toFloat();
                    deliminator_index = i;
                }
                else if (pyserial_data[i] == 'e'){
                    pyserial_throttle = pyserial_data.substring(deliminator_index+1, i).toFloat();
                    break;
                }
            }
        }
    }

    // If value equals to 0 that means we are in manuel mode
    if (pyserial_steering == 0 && Ch1_Pulses < 2000)
        steering_value = Steering_Filter.filter(Ch1_Pulses);
    else if (900 < pyserial_steering && pyserial_steering < 2100)
        steering_value = pyserial_steering;
    
    if (pyserial_throttle == 0)
        throttle_value = Thorttle_Filter.filter(readChannel(CH2_PIN, 0));
    else if (900 < pyserial_throttle && pyserial_throttle < 2100)
        throttle_value = 1500; // tmp for safety
        // throttle_value = pyserial_throttle; // not tested
    // else
    //     throttle_value = 1500 // not tested

    ch3_value = readChannel(CH3_PIN, 0);
    if (ch3_value > 500 && ch3_value < 1500)
        mode_button = 1;
    else if (ch3_value > 1500 && ch3_value < 2100)
        mode_button = 2;
    else
        mode_button = 0;

    steering.writeMicroseconds(steering_value);
    throttle.writeMicroseconds(throttle_value);

    // Calculating speed at certain rate
    if (current_time - encoder_last_time > 10){
        dpulses = Encoder_Filter.filter(1000 * pulses / (current_time - encoder_last_time));
        pulses = 0;
        encoder_last_time = current_time;
    }

    // Sending data 100fps
    if (current_time - serialOut_last_time > 10){
        Serial.println("s" + String(steering_value) + "t" + String(throttle_value) + "m" + String(mode_button) + "v" + String(dpulses) + "e");
        serialOut_last_time = current_time;
    }
}

void Ch1_PulseTimer(){
    Ch1_CurrentTime = micros();
    if (Ch1_CurrentTime > Ch1_StartTime){
        Ch1_Pulses = Ch1_CurrentTime - Ch1_StartTime;
        Ch1_StartTime = Ch1_CurrentTime;
    }
}

int readChannel(int channelInput, int defaultValue){
    int ch = pulseIn(channelInput, HIGH, 30000);
    // If the channel is off, return the default value
    if (ch < 100) return defaultValue;
    return ch;
}