int Writing = 50;

int Address = 30;
int AddrSize = 4;

void write(int msg) {
  for(int k=0; k < AddrSize; k++){
    int mask =  1 << k;
    int masked_n = msg & mask;
    int thebit = masked_n >> k;
    digitalWrite(Address+k, thebit);
  }
  digitalWrite(Writing, LOW);
}

void setup() {
  // put your setup code here, to run once:
  pinMode(Writing, OUTPUT);
  digitalWrite(Writing, HIGH);

  for (int i = Address; i < Address+AddrSize; i++) {
    pinMode(i, OUTPUT);  // Change to OUTPUT since you're writing to the pins
  }

  write(0b0001);
}

void loop() {
  // put your main code here, to run repeatedly:
}
