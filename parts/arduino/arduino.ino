#include <Servo.h>
#include <Ewma.h>

#define PPM_PIN 3
#define ESC_PIN 9
#define Servo_PIN 10
#define ENCODER_PIN 2

// Exponentially Weighted Moving Average Filter
Ewma Encoder_Filter(0.15);

Servo ESC;
Servo SERVO;

String pyserial_data;
int pyserial_throttle, pyserial_steering;
int steering, throttle, mod1, mod2;

// current time, previous time, channel no, time differance
unsigned long int t, tp, c, d = 0;
int ch[15];

unsigned long current_time;
unsigned long serialOut_last_time;
unsigned long encoder_last_time;
unsigned int pulses = 0;
float dpulses = 0;

void Read_Channels();
int mode(int pwm);

void setup() {
    pinMode(PPM_PIN, INPUT_PULLUP);
    pinMode(ENCODER_PIN, INPUT);
    ESC.attach(ESC_PIN);
    SERVO.attach(Servo_PIN);
    attachInterrupt(digitalPinToInterrupt(PPM_PIN), Read_Channels, FALLING);
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
                    pyserial_steering = pyserial_data.substring(1, i).toInt();
                    deliminator_index = i;
                }
                else if (pyserial_data[i] == 'e'){
                    pyserial_throttle = pyserial_data.substring(deliminator_index+1, i).toInt();
                    break;
                }
            }
        }
    }

    // If value equals to 0 that means we are in manuel mode
    if (pyserial_steering == 0 && ch[1] < 2000)
        steering = ch[1];
    else if (1000 < pyserial_steering && pyserial_steering < 2000)
        steering = pyserial_steering;
    
    if (pyserial_throttle == 0)
        throttle = ch[3];
    else if (1000 < pyserial_throttle && pyserial_throttle < 2000)
        throttle = 1500; // tmp for safety
        // throttle = pyserial_throttle; // not tested
    // else
    //     throttle = 1500 // not tested

    mod1 = mode(ch[5]);
    mod2 = mode(ch[6]);

    // Arming the esc according to ch7
    SERVO.writeMicroseconds(steering);
    if (ch[7] > 1900 && ch[7] < 2100)
        ESC.writeMicroseconds(throttle);
    else
        ESC.writeMicroseconds(1500);

    // Calculating speed at certain rate
    if (current_time - encoder_last_time > 10){
        dpulses = Encoder_Filter.filter(1000 * pulses / (current_time - encoder_last_time));
        pulses = 0;
        encoder_last_time = current_time;
    }

    // Sending data 100fps
    if (current_time - serialOut_last_time > 10){
        Serial.println("s" + String(steering) + "t" + String(throttle) + "m" + String(mod1) + "m" + String(mod2) + "v" + String(dpulses) + "e");
        serialOut_last_time = current_time;
    }
}

// For reading ppm signal
void Read_Channels(){
    t = micros();
    d = t - tp;
    if (d > 3000)
        c = 0;
    ch[c] = d;
    c ++;
    tp = t;
}

int mode(int pwm){
    if (pwm > 900 && pwm < 1100)
        return 1;
    else if (pwm > 1400 && pwm < 1600)
        return 2;
    else if (pwm > 1900 && pwm < 2100)
        return 3;
    else
        return 0;
}