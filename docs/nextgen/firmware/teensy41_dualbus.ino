// Teensy 4.1 Dual CAN Bridge for GMLAN
// Purpose: Bridge HS-GMLAN (500 kbps) ↔ SW-GMLAN (33.333 kbps)
// Hardware: Teensy 4.1 (600 MHz ARM Cortex-M7)
// Library: FlexCAN_T4 by tonton81
// Author: SonicBuilder NextGen Engineering
// Version: v2.2.0-SB-NEXTGEN
// License: MIT

#include <FlexCAN_T4.h>

FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> CAN_HS;
FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_16> CAN_SW;

#define LED_PIN 13
#define BAUD_HS 500000
#define BAUD_SW 33333

unsigned long msgCount_HS = 0;
unsigned long msgCount_SW = 0;
unsigned long lastPrint = 0;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  
  delay(1000);
  Serial.println("═══════════════════════════════════════");
  Serial.println("Teensy 4.1 Dual-Bus CAN Bridge");
  Serial.println("SonicBuilder NextGen Engineering");
  Serial.println("Version: v2.2.0-SB-NEXTGEN");
  Serial.println("═══════════════════════════════════════");
  
  CAN_HS.begin();
  CAN_SW.begin();
  
  CAN_HS.setBaudRate(BAUD_HS);
  CAN_SW.setBaudRate(BAUD_SW);
  
  CAN_HS.setMaxMB(16);
  CAN_SW.setMaxMB(16);
  
  CAN_HS.enableFIFO();
  CAN_SW.enableFIFO();
  
  CAN_HS.enableFIFOInterrupt();
  CAN_SW.enableFIFOInterrupt();
  
  CAN_HS.onReceive(canSniff_HS);
  CAN_SW.onReceive(canSniff_SW);
  
  Serial.println("CAN1 (HS-GMLAN): 500 kbps");
  Serial.println("CAN2 (SW-GMLAN): 33.333 kbps");
  Serial.println("Bridge active - forwarding all messages");
  Serial.println("═══════════════════════════════════════\n");
  
  digitalWrite(LED_PIN, HIGH);
}

void canSniff_HS(const CAN_message_t &msg) {
  CAN_SW.write(msg);
  msgCount_HS++;
}

void canSniff_SW(const CAN_message_t &msg) {
  CAN_HS.write(msg);
  msgCount_SW++;
}

void loop() {
  CAN_HS.events();
  CAN_SW.events();
  
  if (millis() - lastPrint > 5000) {
    Serial.print("Messages forwarded - HS→SW: ");
    Serial.print(msgCount_HS);
    Serial.print(" | SW→HS: ");
    Serial.println(msgCount_SW);
    
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    lastPrint = millis();
  }
}
