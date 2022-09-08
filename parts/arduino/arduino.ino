#define PPM_PIN 3

int steering, throttle;

unsigned long int t, pt = 0;
int c, d = 0;
int ch[15];

unsigned long current_time;
unsigned long serialOut_last_time;
float dpulses = 0;

void Read_Channels();
int mode(int pwm);

void setup() {
    pinMode(PPM_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PPM_PIN), Read_Channels, FALLING);
    // Default values for steering and throttle
    ch[1] = 1500;
    ch[3] = 1500;
    Serial.begin(115200);
}

void loop() {
    current_time = millis();

    if (ch[1] < 2000)
        steering = ch[1];

    throttle = ch[3];

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