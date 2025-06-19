#include "base.h"
#include "Code.h"

uint8_t DA;

void main_init() {
    writeAddr(1);
    Apply();
    delay(waitTime);
    DA = getData();
    Reset();
    writeData(DA);
    setwriteAddr(1);
    Apply();
    delay(waitTime);
    Reset();
}

void main_tick() {
    setwriteAddr(0);
    writeAddr(0);
    Apply();
    delay(waitTime);
    Reset();
    setreadAddr(0);
    setwriteAddr(3);
    Apply();
    delay(waitTime);
    Reset();
    setreadAddr(0);
    setwriteAddr(1);
    Apply();
    delay(waitTime);
    Reset();
}
