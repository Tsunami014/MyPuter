#include "base.h"
#include "Code.h"

void main_init() {
  //AllUnitTests();

  setwriteAddr(1);
  writeData(2);
  Execute();
  setwriteAddr(2);
  writeData(0);
  Execute();
}

void main_tick() {
  setwriteAddr(0);
  writeAddr(0b101001);
  Execute();
  setreadAddr(0);
  setwriteAddr(3);
  Apply();
  delay(waitTime);
  printData();
  Reset();
  delay(waitTime);
  setreadAddr(0);
  setwriteAddr(2);
  Execute();
}
