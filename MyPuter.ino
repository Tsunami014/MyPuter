#include "Code.h"
#include "base.h"
#include <Arduino.h>

void setup() {
  base_setup();

  main_init();
}

void loop() {
  main_tick();
}
