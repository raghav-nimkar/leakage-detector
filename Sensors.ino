#include "HX711.h"

// Define Pins for all 6 Sensors
const int CP1 = 2; const int DP1 = 3;
const int CP2 = 4; const int DP2 = 5;
const int CP3 = 6; const int DP3 = 7;
const int CP4 = 8; const int DP4 = 9;
const int CP5 = 10; const int DP5 = 11;
const int CP6 = 12; const int DP6 = 13;

HX711 sensor1, sensor2, sensor3, sensor4, sensor5, sensor6;

// Put your real calibration factor here!
float calibration_factor = 4500.0; 

void setup() {
  Serial.begin(9600);
  
  sensor1.begin(DP1, CP1);
  sensor2.begin(DP2, CP2);
  sensor3.begin(DP3, CP3);
  sensor4.begin(DP4, CP4);
  sensor5.begin(DP5, CP5);
  sensor6.begin(DP6, CP6);

  sensor1.set_scale(calibration_factor);
  sensor2.set_scale(calibration_factor);
  sensor3.set_scale(calibration_factor);
  sensor4.set_scale(calibration_factor);
  sensor5.set_scale(calibration_factor);
  sensor6.set_scale(calibration_factor);

  sensor1.tare();
  sensor2.tare();
  sensor3.tare();
  sensor4.tare();
  sensor5.tare();
  sensor6.tare();
}

void loop() {
  float p1 = 0, p2 = 0, p3 = 0, p4 = 0, p5 = 0, p6 = 0;
  
  // Read 3 samples from each to balance smoothness and speed
  if(sensor1.is_ready()) p1 = sensor1.get_units(3);
  if(sensor2.is_ready()) p2 = sensor2.get_units(3);
  if(sensor3.is_ready()) p3 = sensor3.get_units(3);
  if(sensor4.is_ready()) p4 = sensor4.get_units(3);
  if(sensor5.is_ready()) p5 = sensor5.get_units(3);
  if(sensor6.is_ready()) p6 = sensor6.get_units(3);

  // Print as a clean JSON string with 6 variables
  Serial.print("{\"p1\":"); Serial.print(p1);
  Serial.print(",\"p2\":"); Serial.print(p2);
  Serial.print(",\"p3\":"); Serial.print(p3);
  Serial.print(",\"p4\":"); Serial.print(p4);
  Serial.print(",\"p5\":"); Serial.print(p5);
  Serial.print(",\"p6\":"); Serial.print(p6);
  Serial.println("}");

  delay(500); 
}