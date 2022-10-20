#include <Servo.h>

int readChannel(int channelInput, int defaultValue);

#define CH1_PIN 3
#define CH2_PIN 5
#define CH3_PIN 6
#define ESC_PIN 9
#define Servo_PIN 10
#define ENCODER_PIN 2

String pyserial_data;
int pyserial_throttle, pyserial_steering;
int steering_value, throttle_value;

unsigned long encoder_last_time;
unsigned int pulses = 0;
float dpulses = 0;

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
    if (pyserial_throttle == 10000)
        throttle_value = readChannel(CH2_PIN, 0);
    else if (pyserial_throttle < 2100 && pyserial_throttle > 900)
        throttle_value = readChannel(CH2_PIN, 0); // tmp for safety
        // throttle_value = -pyserial_throttle; // not tested
    // else
    //     throttle_value = THROTTLE_STOPPED_PWM // not tested

    if (pyserial_steering == 10000)
        steering_value = readChannel(CH1_PIN, 1500);
    else if (pyserial_steering < 2100 && pyserial_steering > 900)
        steering_value = -pyserial_steering;

    throttle.writeMicroseconds(throttle_value);
    steering.writeMicroseconds(steering_value);

    // Calculating speed at certain rate
    if (millis() - encoder_last_time > 100){
        dpulses = 1000 * pulses / (millis() - encoder_last_time);
        pulses = 0;
        encoder_last_time = millis();
    }

    Serial.println("t" + String(throttle_value) + "s" + String(steering_value) + "v" + String(dpulses) + "e");

}

int readChannel(int channelInput, int defaultValue){
    int ch = pulseIn(channelInput, HIGH, 30000);
    // If the channel is off, return the default value
    if (ch < 100) return defaultValue;
    return ch;
}