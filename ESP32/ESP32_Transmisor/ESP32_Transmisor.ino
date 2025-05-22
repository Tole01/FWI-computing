#include <WiFi.h>

#define MAX_HEIGHT 120
#define MAX_WIDTH 160
#define LED_PIN 2
#define SERVER_PORT 3333

float matriz[MAX_HEIGHT][MAX_WIDTH];
int rows = MAX_HEIGHT;
int cols = MAX_WIDTH;
bool matrizLista = false;

WiFiServer server(SERVER_PORT);
WiFiClient client;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  WiFi.softAP("ESP32_AP", "esp32pass");
  WiFi.setTxPower(WIFI_POWER_19_5dBm);
  Serial.print("✅ AP activo. IP: ");
  Serial.println(WiFi.softAPIP());

  server.begin();
}

void loop() {
  // Verificar si un cliente TCP se conecta
  if (!client || !client.connected()) {
    WiFiClient newClient = server.available();
    if (newClient) {
      client = newClient;
      Serial.println("✅ Cliente TCP conectado.");
    }
  }

  // Recibir matriz por serial
  if (!matrizLista && Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    if (line == "<START>") {
      Serial.println("📥 Recibiendo matriz...");
      rows = 0;
      matrizLista = false;

      while (rows < MAX_HEIGHT) {
        while (!Serial.available());
        String filaStr = Serial.readStringUntil('\n');
        filaStr.trim();

        if (filaStr == "<END>") break;

        int col = 0;
        char *token = strtok((char *)filaStr.c_str(), ",");
        while (token && col < MAX_WIDTH) {
          matriz[rows][col++] = atof(token);
          token = strtok(NULL, ",");
        }

        if (col == MAX_WIDTH) {
          rows++;
        } else {
          Serial.printf("❌ Fila %d con columnas incompletas (%d).\n", rows, col);
          return;
        }
      }

      cols = MAX_WIDTH;
      if (rows == MAX_HEIGHT) {
        matrizLista = true;
        Serial.println("✅ Matriz completa recibida.");
      }
    }
  }

  // Enviar matriz por TCP si está lista
  if (matrizLista) {
    if (client && client.connected()) {
      digitalWrite(LED_PIN, HIGH);

      const char* sync = "SYNC";
      client.write((const uint8_t*)sync, 4);
      client.write((uint8_t*)&rows, sizeof(rows));
      client.write((uint8_t*)&cols, sizeof(cols));
      client.write((uint8_t*)matriz, sizeof(float) * rows * cols);
      client.flush();

      digitalWrite(LED_PIN, LOW);
      Serial.println("📤 Matriz enviada por TCP.");
    } else {
      Serial.println("⚠️ Cliente no conectado. Matriz descartada.");
    }

    matrizLista = false;
  }
}
