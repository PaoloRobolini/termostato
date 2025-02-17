#include <DHT11.h>

DHT11 dht11(2);

const int LED_ROSSO = 8;
const int LED_VERDE = 9;

const int SOGLIA_SUPERIORE = 27;
const int SOGLIA_INFERIORE = 23;

int temp, umid;

void accendiLed(const int TEMPERATURA, const int SOGLIA_INFERIORE, const int SOGLIA_SUPERIORE) {

  digitalWrite(LED_ROSSO, LOW);
  digitalWrite(LED_VERDE, LOW);

  if (TEMPERATURA >= SOGLIA_SUPERIORE) {
    digitalWrite(LED_ROSSO, HIGH);
    digitalWrite(LED_VERDE, LOW);

  } else if (TEMPERATURA > SOGLIA_INFERIORE) {
    digitalWrite(LED_ROSSO, LOW);
    digitalWrite(LED_VERDE, HIGH);

  } else {
    digitalWrite(LED_ROSSO, LOW);
    digitalWrite(LED_VERDE, LOW);
  }
}

void setup() {
  pinMode(LED_ROSSO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);

  Serial.begin(9600);
}

void loop() {

  //LEGGE LA TEMPERATURA E L'UMIDITA
  temp = 0;
  umid = 0;

  // Attempt to read the temperature and humidity values from the DHT11 sensor.
  int result = dht11.readTemperatureHumidity(temp, umid);

  if (result == 0) {
    String messaggio = String(temp) + " " + String(umid);
    Serial.println(messaggio);

  } else Serial.println(DHT11::getErrorString(result));

  accendiLed(temp, SOGLIA_INFERIORE, SOGLIA_SUPERIORE);

  delay(500);
}