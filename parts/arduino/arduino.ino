#include <Servo.h>

#define CH1_PIN 3
#define CH2_PIN 5
#define CH3_PIN 6
#define ESC_PIN 9
#define Servo_PIN 10

#define THROTTLE_FORWARD_PWM 500
#define THROTTLE_STOPPED_PWM 370
#define THROTTLE_REVERSE_PWM 220

#define STEERING_FULL_RIGHT_VALUE 1200
#define STEERING_MID_VALUE 1540
#define STEERING_FULL_LEFT_VALUE 1900

int readChannel(int channelInput, int defaultValue);

Servo throttle;
Servo steering;

void setup() {
    pinMode(CH1_PIN, INPUT);
    pinMode(CH2_PIN, INPUT);
    throttle.attach(ESC_PIN);
    steering.attach(Servo_PIN);
    Serial.begin(9600);
}

float steering_value, throttle_value;

void loop() {
    steering_value = readChannel(CH1_PIN, STEERING_MID_VALUE);
    throttle_value = readChannel(CH2_PIN, 0);
    steering.writeMicroseconds(steering_value);
    throttle.writeMicroseconds(throttle_value);
}

int readChannel(int channelInput, int defaultValue){
    int ch = pulseIn(channelInput, HIGH, 30000);
    // If the channel is off, return the default value
    if (ch < 100) return defaultValue;
    return ch;
}