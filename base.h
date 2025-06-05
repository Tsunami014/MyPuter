#pragma once
#include <Arduino.h>

static int waitTime = 100;

void base_setup();

void setwriteAddr(uint8_t addr);
void setreadAddr(uint8_t addr);

void writeAddr(uint8_t addr);

void Apply();

void writeData(uint8_t msg);
int getData();

void getDataBits(int* data);

void printData();

void Execute();

void Reset();

void unitTest(int A, int B, int op, int XpectedOut);

void AllUnitTests();
