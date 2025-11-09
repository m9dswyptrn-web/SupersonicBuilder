// Teensy 4.1 ID Discovery Mode v2.2.2
#include <FlexCAN_T4.h>
#include <Arduino.h>
#include <cstdint>

FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> CAN_HS;
FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_16> CAN_SW;

const uint32_t BAUD_CAN_HS = 500000;
const uint32_t BAUD_CAN_SW = 33333;

#define MAX_IDS 1024
uint32_t ids_seen[MAX_IDS];
uint16_t ids_count = 0;

bool has_id(uint32_t id) {
  for (uint16_t i=0;i<ids_count;i++) if (ids_seen[i]==id) return true;
  return false;
}

void add_id(uint32_t id) {
  if (ids_count < MAX_IDS) ids_seen[ids_count++] = id;
}

void print_ids_csv() {
  Serial.print("timestamp,ids_count,ids_list\n");
  Serial.print(millis()); Serial.print(","); Serial.print(ids_count); Serial.print(",\""); 
  for (uint16_t i=0;i<ids_count;i++) {
    if (i) Serial.print(" ");
    Serial.print("0x"); Serial.print(ids_seen[i], HEX);
  }
  Serial.print("\"\n");
}

void setup() {
  Serial.begin(115200);
  delay(400);
  CAN_HS.begin(); CAN_HS.setBaudRate(BAUD_CAN_HS);
  CAN_SW.begin(); CAN_SW.setBaudRate(BAUD_CAN_SW);
  Serial.println("# Teensy ID Discovery v2.2.2 READY");
}

void loop() {
  CAN_message_t m;
  while (CAN_HS.read(m)) {
    if (!has_id(m.id)) add_id(m.id);
  }
  while (CAN_SW.read(m)) {
    if (!has_id(m.id)) add_id(m.id);
  }
  static uint32_t last_print = 0;
  if (millis() - last_print > 5000) {
    last_print = millis();
    print_ids_csv();
  }
}
