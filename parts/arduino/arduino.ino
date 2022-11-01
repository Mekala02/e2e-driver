#include <Servo.h>
#include <Ewma.h>

#define CH1_PIN 3
#define CH2_PIN 5
#define CH3_PIN 6
#define ESC_PIN 9
#define Servo_PIN 10
#define ENCODER_PIN 2

// Rc receiver filters (Exponentially Weighted Moving Average)
Ewma Steering_Filter(0.25);
Ewma Thorttle_Filter(0.2);
Ewma Encoder_Filter(0.15);

Servo throttle;
Servo steering;

String pyserial_data;
int pyserial_throttle, pyserial_steering;
int steering_value, throttle_value;

unsigned long current_time;
unsigned long encoder_last_time;
unsigned int pulses = 0;
float dpulses = 0;


int readChannel(int channelInput, int defaultValue);

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
    if (pyserial_steering == 0)
        steering_value = Steering_Filter.filter(readChannel(CH1_PIN, 1500));
    else if (900 < pyserial_steering && pyserial_steering < 2100)
        steering_value = pyserial_steering;
    
    if (pyserial_throttle == 0)
        throttle_value = Thorttle_Filter.filter(readChannel(CH2_PIN, 0));
    else if (900 < pyserial_throttle && pyserial_throttle < 2100)
        throttle_value = readChannel(CH2_PIN, 0); // tmp for safety
        // throttle_value = pyserial_throttle; // not tested
    // else
    //     throttle_value = THROTTLE_STOPPED_PWM // not tested

    steering.writeMicroseconds(steering_value);
    throttle.writeMicroseconds(throttle_value);

    current_time = millis();
    // Calculating speed at certain rate
    if (current_time - encoder_last_time > 10){
        dpulses = Encoder_Filter.filter(1000 * pulses / (current_time - encoder_last_time));
        pulses = 0;
        encoder_last_time = current_time;
    }

    Serial.println("s" + String(steering_value) + "t" + String(throttle_value) + "v" + String(dpulses) + "e");
}

int readChannel(int channelInput, int defaultValue){
    int ch = pulseIn(channelInput, HIGH, 30000);
    // If the channel is off, return the default value
    if (ch < 100) return defaultValue;
    return ch;
}