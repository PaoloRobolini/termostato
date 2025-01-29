#include <DHT11.h>

DHT11 dht11(2);

#define LED_ROSSO 8
#define LED_VERDE 9

void accendiLed(const int TEMPERATURA, const int SOGLIA_INFERIORE, const int SOGLIA_SUPERIORE){
  if (TEMPERATURA > SOGLIA_SUPERIORE){
      digitalWrite(LED_ROSSO, HIGH);
      digitalWrite(LED_VERDE, LOW);
    } else if (TEMPERATURA > SOGLIA_INFERIORE){
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
  
    int lettura = 0;
}

void loop() {

    //LEGGE LA TEMPERATURA E L'UMIDITA
    int temp = 0;
    int umid = 0;

    // Attempt to read the temperature and humidity values from the DHT11 sensor.
   int result = dht11.readTemperatureHumidity(temp, umid);

    if (result == 0) {
      String messaggio = String(temp) + " " + String(umid);
        Serial.println(messaggio);
    } else {
        Serial.println(DHT11::getErrorString(result));
    }


    int SOGLIA_SUPERIORE = 27;
    int SOGLIA_INFERIORE = 25;

    accendiLed(temp, SOGLIA_INFERIORE, SOGLIA_SUPERIORE);
  
}
