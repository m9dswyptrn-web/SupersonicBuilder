// SonicBuilder Teensy 4.1 Dual-Bus CAN Bridge (Tagged) v2.2.1
#include <FlexCAN_T4.h>
FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_64> CAN_HS;
FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_64> CAN_SW;
uint32_t BAUD_CAN_HS = 500000, BAUD_CAN_SW = 33333;
struct NameMap { uint32_t id; const char* name; };
NameMap GM_HS_MAP[] = {{0x100,"IGNITION_STATUS"},{0x1A0,"ILLUM_DIMMER"},{0x2F0,"SWC"},{0x3E0,"RADIO"},{0x0,nullptr}};
NameMap GM_SW_MAP[] = {{0x201,"BCM_STATUS"},{0x285,"DOOR_LOCKS"},{0x2A1,"HVAC"},{0x0,nullptr}};
const char* tag_id(const NameMap* m, uint32_t id){ for(int i=0;m[i].name;++i) if(m[i].id==id) return m[i].name; return "UNKNOWN"; }
void setup(){ Serial.begin(115200); delay(400); CAN_HS.begin(); CAN_SW.begin(); CAN_HS.setBaudRate(BAUD_CAN_HS); CAN_SW.setBaudRate(BAUD_CAN_SW); Serial.println("# Tagged Bridge ready"); }
void print_msg(const char* bus, const CAN_message_t& msg, const char* tag){
  Serial.print("{\"bus\":\""); Serial.print(bus); Serial.print("\",\"id\":\"0x"); Serial.print(msg.id,HEX);
  Serial.print("\",\"tag\":\""); Serial.print(tag); Serial.print("\",\"dlc\":"); Serial.print(msg.len); Serial.print(",\"data\":\"");
  for(int i=0;i<msg.len;i++){ if(i) Serial.print(" "); Serial.print(msg.buf[i],HEX); } Serial.print("\"}"); Serial.println();
}
void loop(){ CAN_message_t m; while(CAN_HS.read(m)) print_msg("HS",m,tag_id(GM_HS_MAP,m.id)); while(CAN_SW.read(m)) print_msg("SW",m,tag_id(GM_SW_MAP,m.id)); }
