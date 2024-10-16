int WRITEPINS[] = {30, 31, 32, 33, 34, 35, 36, 37};
int Writing = 50;

void setup() {
  // put your setup code here, to run once:
  for (int i = 0; i < sizeof(WRITEPINS) / sizeof(WRITEPINS[0]); i++) {
    pinMode(WRITEPINS[i], OUTPUT);  // Change to OUTPUT since you're writing to the pins
    if (WRITEPINS[i] == 33) {
      digitalWrite(WRITEPINS[i], HIGH);
    } else {
      digitalWrite(WRITEPINS[i], LOW);
    }
  }
  pinMode(Writing, OUTPUT);  // Set Writing pin as OUTPUT

  digitalWrite(Writing, HIGH);  // Set Writing pin to HIGH

  delay(1000);

  digitalWrite(Writing, LOW);  // Set Writing pin to HIGH
}

void loop() {
  // put your main code here, to run repeatedly:
}
