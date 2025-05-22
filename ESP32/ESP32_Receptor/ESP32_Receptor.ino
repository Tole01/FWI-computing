#include <WiFi.h>

#define MAX_HEIGHT 120
#define MAX_WIDTH 160
#define LED_PIN 2
#define SERVER_IP "192.168.4.1"
#define SERVER_PORT 3333

float matriz[MAX_HEIGHT][MAX_WIDTH];
int rows = 0;
int cols = 0;

WiFiClient client;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  WiFi.begin("ESP32_AP", "esp32pass");
  Serial.print("Conectando al Access Point");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Conectado al AP. IP local: " + WiFi.localIP().toString());

  if (!client.connect(SERVER_IP, SERVER_PORT)) {
    Serial.println("❌ No se pudo conectar al servidor TCP.");
    return;
  }
  Serial.println("✅ Conectado al servidor TCP.");
}

void loop() {
  if (client.connected()) {
    while (client.available() > 0) client.read();

    while (client.available() < 4) delay(1);
    char syncCheck[5] = {0};
    client.readBytes((uint8_t*)syncCheck, 4);
    if (strncmp(syncCheck, "SYNC", 4) != 0) {
      Serial.println("❌ SYNC no detectado. Abortando.");
      return;
    }
    Serial.println("🔗 SYNC recibido. Recibiendo dimensiones...");

    while (client.available() < sizeof(int) * 2) delay(1);
    client.readBytes((uint8_t*)&rows, sizeof(rows));
    client.readBytes((uint8_t*)&cols, sizeof(cols));

    Serial.print("📦 Recibido rows: "); Serial.println(rows);
    Serial.print("📦 Recibido cols: "); Serial.println(cols);

    if (rows < 10 || rows > MAX_HEIGHT || cols < 10 || cols > MAX_WIDTH) {
      Serial.println("❌ Dimensiones fuera de rango. Limpiando datos...");
      while (client.available()) client.read();
      return;
    }

    int totalBytes = sizeof(float) * rows * cols;
    int bytesRead = 0;
    uint8_t* ptr = (uint8_t*)matriz;
    unsigned long startRead = millis();

    while (bytesRead < totalBytes && millis() - startRead < 15000) {
      if (client.available()) {
        int n = client.read(ptr + bytesRead, totalBytes - bytesRead);
        if (n > 0) bytesRead += n;
      } else {
        delay(1);
      }
    }

    if (bytesRead < totalBytes) {
      Serial.printf("⚠️ Solo se recibieron %d de %d bytes. Rellenando con -999.0\n", bytesRead, totalBytes);
      int missingFloats = (totalBytes - bytesRead) / sizeof(float);
      float* mtxPtr = (float*)matriz;
      for (int i = (bytesRead / sizeof(float)); i < rows * cols; i++) {
        mtxPtr[i] = -999.0f;
      }
    }

    digitalWrite(LED_PIN, HIGH);

    Serial.println("<START>");
    //Serial.print("DIM:"); Serial.print(rows); Serial.print(","); Serial.println(cols);

    for (int i = 0; i < rows; i++) {
      for (int j = 0; j < cols; j++) {
        Serial.print(matriz[i][j], 1);
        Serial.print(j < cols - 1 ? "," : "\n");
      }
    }

    Serial.println("<END>");
    digitalWrite(LED_PIN, LOW);
  }
}
