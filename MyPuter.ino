// 0b0000
// But it's in reverse, so b careful
int Writing = 50;
int Reading = 51;

int ReadAddr = 34;
int RAddrSize = 4;
int WriteAddr = 30;
int WAddrSize = 4;

int DataBus = 40;
int DataSize = 8;
int AddrBus = 22;
int AddrSize = 8;

bool writing = false;
bool reading = false;

int waitTime = 200;

void setwriteAddr(uint8_t addr) {
  for(int k=0; k < WAddrSize; k++){
    int mask =  1 << k;
    int masked_n = addr & mask;
    int thebit = masked_n >> k;
    digitalWrite(WriteAddr+k, thebit);
  }
  writing = true;
}
void setreadAddr(uint8_t addr) {
  for(int k=0; k < RAddrSize; k++){
    int mask =  1 << k;
    int masked_n = addr & mask;
    int thebit = masked_n >> k;
    digitalWrite(ReadAddr+k, thebit);
  }
  reading = true;
}

void writeAddr(uint8_t addr) {
  //Serial.print('>');
  for(int k=0; k < AddrSize; k++){
    int mask =  1 << k;
    int masked_n = addr & mask;
    int thebit = masked_n >> k;
    //Serial.print(thebit);
    //Serial.print(',');
    pinMode(AddrBus+k, OUTPUT);
    digitalWrite(AddrBus+k, thebit);
  }
  //Serial.println();
}

void Apply() {
  digitalWrite(Writing, (uint8_t)(!writing));
  digitalWrite(Reading, (uint8_t)(!reading));
}

void writeData(uint8_t msg) {
  for(int k=0; k < DataSize; k++){
    int mask =  1 << k;
    int masked_n = msg & mask;
    int thebit = masked_n >> k;
    pinMode(DataBus+k, OUTPUT);
    digitalWrite(DataBus+k, thebit);
  }
}

int getData() {
  int data = 0;
  for(int k=0; k < DataSize; k++){
    data = (data << 1) | digitalRead(DataBus + (DataSize - 1 - k));
  }
  return data;
}

void getDataBits(int* data) {
  for(int k=0; k < DataSize; k++){
    data[k] = digitalRead(DataBus+k);
  }
}

void printData() {
  int datas[DataSize];
  getDataBits(datas);
  for (int i=0;i<sizeof(datas)/sizeof(int);i++) {
    Serial.print(datas[i]);
    Serial.print(',');
  }
  Serial.println(getData());
}

void Reset() {
  digitalWrite(Writing, HIGH);
  digitalWrite(Reading, HIGH);
  for (int i = DataBus; i < DataBus+DataSize; i++) {
    pinMode(i, INPUT);
  }
  for (int i = AddrBus; i < AddrBus+AddrSize; i++) {
    pinMode(i, INPUT);
  }
  writing = false;
  reading = false;

  /*for (int i = ReadAddr; i < ReadAddr+RAddrSize; i++) {
    digitalWrite(i, HIGH);
  }
  for (int i = WriteAddr; i < WriteAddr+WAddrSize; i++) {
    digitalWrite(i, HIGH);
  }*/
}

int testnum;
void unitTest(int A, int B, int op, int XpectedOut) {
  testnum++;
  setwriteAddr(1);
  writeData(A);
  Apply();
  delay(waitTime);
  Reset();
  delay(waitTime);
  setwriteAddr(2);
  writeData(B);
  Apply();
  delay(waitTime);
  Reset();
  delay(waitTime);
  setwriteAddr(0);
  writeAddr(op);
  Apply();
  delay(waitTime);
  Reset();
  delay(waitTime);
  setreadAddr(0);
  setwriteAddr(3);
  Apply();
  delay(waitTime);
  int datas[DataSize];
  getDataBits(datas);

  bool corr = true;
  int xpecteds[DataSize];

  Serial.print(testnum);
  Serial.println(":");

  Serial.print("< ");
  for (int i=0;i<sizeof(datas)/sizeof(int);i++) {
    Serial.print(((1 << i) & A) >> i);
  }
  Serial.println();
  Serial.print("< ");
  for (int i=0;i<sizeof(datas)/sizeof(int);i++) {
    Serial.print(((1 << i) & B) >> i);
  }
  Serial.println();

  Serial.print("> ");
  for (int i=0;i<sizeof(datas)/sizeof(int);i++) {
    xpecteds[i] = ((1 << i) & XpectedOut) >> i;
    if (datas[i] != xpecteds[i]) {
      corr = false;
    }
    Serial.print(datas[i]);
  }
  Serial.println();
  if (corr) {
    Serial.print("+ ");
  } else {
    Serial.print("! ");
  }
  for (int i=0;i<sizeof(datas)/sizeof(int);i++) {
    Serial.print(xpecteds[i]);
  }
  Serial.println();
  Reset();
  delay(waitTime);
}

void AllUnitTests() {
  // for (int i = 0;i < 16;i++) {
  //   unitTest(i, 0, 0b000000, i);
  // }
  for (int i = 0;i < 8;i++) {
    for (int j = 0;j < 8;j++) {
      unitTest(i, j, 0b101001, i+j);
    }
  }
}

void setup() {
  Serial.begin(9600);
  // put your setup code here, to run once:
  pinMode(Writing, OUTPUT);
  pinMode(Reading, OUTPUT);

  for (int i = ReadAddr; i < ReadAddr+RAddrSize; i++) {
    pinMode(i, OUTPUT);
  }
  for (int i = WriteAddr; i < WriteAddr+WAddrSize; i++) {
    pinMode(i, OUTPUT);
  }

  Reset();

  AllUnitTests();

}

void loop() {
  // put your main code here, to run repeatedly:
  /*setwriteAddr(0);
  writeAddr(0b101);
  Apply();
  delay(waitTime);
  Reset();
  delay(waitTime);
  setreadAddr(0);
  setwriteAddr(3);
  Apply();
  delay(waitTime);
  printData();
  Reset();
  delay(waitTime);
  setreadAddr(0);
  setwriteAddr(1);
  Apply();
  delay(waitTime);
  Reset();
  delay(waitTime);*/
}
