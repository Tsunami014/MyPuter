// 0b0000
int Writing = 50;
int Reading = 51;

int ReadAddr = 34;
int RAddrSize = 4;
int WriteAddr = 30;
int WAddrSize = 4;

int DataBus = 40;
int DataSize = 8;

bool writing = false;
bool reading = false;

void setwriteAddr(int addr) {
  for(int k=0; k < WAddrSize; k++){
    int mask =  1 << k;
    int masked_n = addr & mask;
    int thebit = masked_n >> k;
    digitalWrite(WriteAddr+k, thebit);
  }
  writing = true;
}
void setreadAddr(int addr) {
  for(int k=0; k < RAddrSize; k++){
    int mask =  1 << k;
    int masked_n = addr & mask;
    int thebit = masked_n >> k;
    digitalWrite(ReadAddr+k, thebit);
  }
  reading = true;
}

void Apply() {
  digitalWrite(Writing, (uint8_t)(!writing));
  digitalWrite(Reading, (uint8_t)(!reading));
}

void writeData(int msg) {
  for (int i = DataBus; i < DataBus+DataSize; i++) {
    pinMode(i, OUTPUT);
  }
  for(int k=0; k < DataSize; k++){
    int mask =  1 << k;
    int masked_n = msg & mask;
    int thebit = masked_n >> k;
    digitalWrite(DataBus+k, thebit);
  }
}

int getData() {
  int data = 0;
  for(int k=0; k < DataSize; k++){
    data = data << 1;
    data += digitalRead(DataBus+k);
  }
  return data;
}

void Reset() {
  digitalWrite(Writing, HIGH);
  digitalWrite(Reading, HIGH);
  for (int i = DataBus; i < DataBus+DataSize; i++) {
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

int prev = 0;

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
}

void loop() {
  // put your main code here, to run repeatedly:
  setwriteAddr(0);
  prev = prev + 1;
  writeData(prev);
  Apply();
  delay(250);
  Reset();
  delay(250);
  setreadAddr(0);
  setwriteAddr(1);
  Apply();
  Serial.println(prev);
  delay(250);
  Reset();
  delay(250);
}
