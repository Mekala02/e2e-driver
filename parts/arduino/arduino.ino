#include <Servo.h>

int readChannel(int channelInput, int defaultValue);
float mapfloat(float x, float in_min, float in_max, float out_min, float out_max);

#define CH1_PIN 3
#define CH2_PIN 5
#define CH3_PIN 6
#define ESC_PIN 9
#define Servo_PIN 10
#define ENCODER_PIN 2

#define THROTTLE_FORWARD_PWM 500
#define THROTTLE_STOPPED_PWM 370
#define THROTTLE_REVERSE_PWM 220

#define STEERING_FULL_RIGHT_VALUE 1200
#define STEERING_MID_VALUE 1540
#define STEERING_FULL_LEFT_VALUE 1900

String pyserial_data;
float pyserial_throttle;
float pyserial_steering;

unsigned long encoder_last_time;
unsigned int pulses = 0;
float speed = 0;

Servo throttle;
Servo steering;

void setup() {
    pinMode(CH1_PIN, INPUT);
    pinMode(CH2_PIN, INPUT);
    throttle.attach(ESC_PIN);
    steering.attach(Servo_PIN);
    pinMode(ENCODER_PIN, INPUT);
    attachInterrupt(digitalPinToInterrupt(ENCODER_PIN), []{pulses++;}, FALLING );
    Serial.begin(115200);
}

float steering_value, throttle_value;

void loop() {
    // Reading serial input
	if(Serial.available() > 0) {
		pyserial_data =  Serial.readStringUntil('\r');
		// Serial.print(pyserial_data);
	}

    int deliminator_index = 0;
    if (pyserial_data[0] == 't'){
        for (int i = 1; i < pyserial_data.length(); i++) {
            if (pyserial_data[i] == 's'){
                pyserial_throttle = pyserial_data.substring(1, i).toFloat();
                // Serial.print(pyserial_throttle);
                deliminator_index = i;
            }
            else if (pyserial_data[i] == 'e'){
                pyserial_steering = pyserial_data.substring(deliminator_index+1, i).toFloat();
                break;
            }
        }
    }
    // If value equals to 10 that means we are in manuel mode
    // Received steering and throttle values are between -1 and 1
    // We have to convert them to pwm
    // multiplying with 1 for reversing left and right
    if (pyserial_throttle == 10)
        throttle_value = readChannel(CH2_PIN, 0);
    else if (pyserial_throttle < 1 && pyserial_throttle > -1)
        throttle_value = readChannel(CH2_PIN, 0); // tmp for safety
        // throttle_value = mapfloat(-pyserial_throttle, -1, 1, THROTTLE_FORWARD_PWM, THROTTLE_REVERSE_PWM); // not tested
    // else
    //     throttle_value = THROTTLE_STOPPED_PWM // not tested

    if (pyserial_steering == 10)
        steering_value = readChannel(CH1_PIN, STEERING_MID_VALUE);
    else if (pyserial_steering < 1 && pyserial_steering > -1)
        steering_value = mapfloat(-pyserial_steering, -1, 1, STEERING_FULL_RIGHT_VALUE, STEERING_FULL_LEFT_VALUE);

    throttle.writeMicroseconds(throttle_value);
    steering.writeMicroseconds(steering_value);

    // Calculating speed at certain rate
    if (millis() - encoder_last_time > 100){
        speed = (60 * 100 / 20) / (millis() - encoder_last_time) * pulses;
        pulses = 0;
        encoder_last_time = millis();
    }

    Serial.println("t" + String(mapfloat(throttle_value, 900, 2000, -1, 1)) + "s" + String(mapfloat(steering_value, 900, 2000, -1, 1)) + "v" + String(speed) + "e");

}

float mapfloat(float x, float in_min, float in_max, float out_min, float out_max)
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

int readChannel(int channelInput, int defaultValue){
    int ch = pulseIn(channelInput, HIGH, 30000);
    // If the channel is off, return the default value
    if (ch < 100) return defaultValue;
    return ch;
}