#include <Arduino.h>
#include <project_config.h>

void setup() {
    Serial.begin(115200);
}

void loop() {
    #ifdef DRIVER_ILI9341
    Serial.println("Using ILI9341 driver.");
    #elif defined(DRIVER_ST7789)    
    Serial.println("Using ST7789 driver.");
    #endif
    delay(1000);
}