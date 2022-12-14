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
int steering, throttle;

// current time, previous time
unsigned long int t, pt = 0;
// channel no, time differance
int c, d = 0;
int ch[15];

unsigned long current_time;
unsigned long last_serial;
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
    // Default values for steering and throttle
    ch[1] = 1500;
    ch[3] = 1500;
    Serial.begin(115200);
}

void loop() {
    current_time = millis();
    // Reading serial input
    // Serial inputs shape: s(float)t(float)e
    if(Serial.available() > 0){
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
        last_serial = current_time;
    }
    else{
        // If python program stoped (no response for 50ms)
        if (current_time - last_serial > 50){
            pyserial_steering = 0;
            pyserial_throttle = 0;
        }
    }

    // If value equals to 0 we are in manuel mode
    if (pyserial_steering == 0 && ch[1] < 2000)
        steering = ch[1];
    else if (1000 < pyserial_steering && pyserial_steering < 2000)
        steering = pyserial_steering;
    
    if (pyserial_throttle == 0)
        throttle = ch[3];
    else if (1000 < pyserial_throttle && pyserial_throttle < 2000)
        throttle = pyserial_throttle;
    else
        throttle = 1500;

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

    // Sending data 100 times per second
    if (current_time - serialOut_last_time > 10){
        // sending transmitters steering pwm, transmitters throttle pwm, mode, mode, encoder pulses
        Serial.println("s" + String(ch[1]) + "t" + String(ch[3]) + "m" + String(mode(ch[5])) + "m" + String(mode(ch[6])) + "v" + String(dpulses) + "e");
        serialOut_last_time = current_time;
    }
}

// Reading ppm signal
void Read_Channels(){
    t = micros();
    d = t - pt;
    if (d > 3000)
        c = 0;
    ch[c] = d;
    c ++;
    pt = t;
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