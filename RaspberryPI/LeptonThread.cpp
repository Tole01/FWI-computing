#include <iostream>
#include <vector>
#include <iomanip>
#include <fcntl.h>
#include <cerrno>
#include <string>
#include <sstream>
#include <algorithm>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <cstring>
#include "LeptonThread.h"
#include "Palettes.h"
#include "SPI.h"
#include "Lepton_I2C.h"

#define PACKET_SIZE 164
#define PACKET_SIZE_UINT16 (PACKET_SIZE/2)
#define PACKETS_PER_FRAME 60
#define FRAME_SIZE_UINT16 (PACKET_SIZE_UINT16*PACKETS_PER_FRAME)
#define FPS 27;

LeptonThread::LeptonThread() : QThread()
{
    // Configuración inicial
    loglevel = 0;

    // Mapa de colores (3: ironblack por defecto)
    typeColormap = 3;
    selectedColormap = colormap_ironblack;
    selectedColormapSize = get_size_colormap_ironblack();

    // Tipo de Lepton (3.x: 160x120 píxeles)
    typeLepton = 3;
    myImageWidth = 160;
    myImageHeight = 120;

    // Velocidad SPI (20 MHz)
    spiSpeed = 20 * 1000 * 1000;

    // Rango de temperatura automático
    autoRangeMin = true;
    autoRangeMax = true;
    rangeMin = 30000;
    rangeMax = 32000;

    // Inicializar matrices
    tempMatrix.resize(120, std::vector<float>(160, 0.0f));

}

LeptonThread::~LeptonThread() {
}

void LeptonThread::setLogLevel(uint16_t newLoglevel) {
    loglevel = newLoglevel;
}

void LeptonThread::useColormap(int newTypeColormap) {
    switch (newTypeColormap) {
        case 1:
            selectedColormap = colormap_rainbow;
            selectedColormapSize = get_size_colormap_rainbow();
            break;
        case 2:
            selectedColormap = colormap_grayscale;
            selectedColormapSize = get_size_colormap_grayscale();
            break;
        default:
            selectedColormap = colormap_ironblack;
            selectedColormapSize = get_size_colormap_ironblack();
            break;
    }
}

void LeptonThread::useLepton(int newTypeLepton) {
    typeLepton = newTypeLepton;
    if (typeLepton == 3) {
        myImageWidth = 160;
        myImageHeight = 120;
    } else {
        myImageWidth = 80;
        myImageHeight = 60;
    }
    tempMatrix.resize(myImageHeight, std::vector<float>(myImageWidth, 0.0f));
}

void LeptonThread::useSpiSpeedMhz(unsigned int newSpiSpeed) {
    spiSpeed = newSpiSpeed * 1000 * 1000;
}

void LeptonThread::setAutomaticScalingRange() {
    autoRangeMin = true;
    autoRangeMax = true;
}

void LeptonThread::useRangeMinValue(uint16_t newMinValue) {
    autoRangeMin = false;
    rangeMin = newMinValue;
}

void LeptonThread::useRangeMaxValue(uint16_t newMaxValue) {
    autoRangeMax = false;
    rangeMax = newMaxValue;
}

void LeptonThread::sendToESP32(const std::vector<std::vector<float>>& data) {
    const char* serialPort = "/dev/ttyUSB0";
    
    // Abrir puerto con flags no bloqueantes
    int fd = open(serialPort, O_WRONLY | O_NOCTTY | O_SYNC);
    if (fd == -1) {
        std::cerr << "[ERROR] No se pudo abrir" << serialPort << "\n";
        return;
    }

    // Configuración del puerto
    struct termios options;
    tcgetattr(fd, &options);
    cfsetispeed(&options, B115200);
    cfsetospeed(&options, B115200);
    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;
    options.c_cc[VMIN] = 0;
    options.c_cc[VTIME] = 5;
    tcsetattr(fd, TCSANOW, &options);
    tcflush(fd, TCIOFLUSH);

    const char* startMarker = "<START>\n";
    const char* endMarker = "<END>\n";

    write(fd, startMarker, strlen(startMarker));
    usleep(500);

    // Enviar todas las temperaturas por filas
    for (const auto& row : data) {
        std::ostringstream oss;
        for (size_t i = 0; i < row.size(); ++i) {
            // Enviar temperatura en °C con 1 decimal
            oss << std::fixed << std::setprecision(1) << (row[i] - 273.15f);
            if (i < row.size() - 1) oss << ",";
        }
        oss << "\n";
        std::string line = oss.str();

        write(fd, line.c_str(), line.size());
        tcdrain(fd);
        usleep(500); // CH340 friendly
    }

    write(fd, endMarker, strlen(endMarker));
    close(fd);
    std::cout << "[INFO] Matriz de temperaturas enviada correctamente.\n";
}

void LeptonThread::run() {
    // Crear imagen RGB
    myImage = QImage(myImageWidth, myImageHeight, QImage::Format_RGB888);

    const int *colormap = selectedColormap;
    const int colormapSize = selectedColormapSize;
    uint16_t minValue = rangeMin;
    uint16_t maxValue = rangeMax;
    float diff = maxValue - minValue;
    float scale = 255 / diff;
    uint16_t n_wrong_segment = 0;
    uint16_t n_zero_value_drop_frame = 0;

    // Rango de temperatura para uint8_t (20°C a 100°C)
    const float TEMP_MIN_C = -10.0f;
    const float TEMP_MAX_C = 140.0f;
    const float TEMP_RANGE = TEMP_MAX_C - TEMP_MIN_C;

    // Abrir puerto SPI
    SpiOpenPort(0, spiSpeed);

    while (true) {
        // Leer paquetes de la Lepton
        int resets = 0;
        int segmentNumber = -1;
        for (int j = 0; j < PACKETS_PER_FRAME; j++) {
            read(spi_cs0_fd, result + sizeof(uint8_t) * PACKET_SIZE * j, sizeof(uint8_t) * PACKET_SIZE);
            int packetNumber = result[j * PACKET_SIZE + 1];
            if (packetNumber != j) {
                j = -1;
                resets += 1;
                usleep(1000);
                if (resets == 750) {
                    SpiClosePort(0);
                    lepton_reboot();
                    n_wrong_segment = 0;
                    n_zero_value_drop_frame = 0;
                    usleep(750000);
                    SpiOpenPort(0, spiSpeed);
                }
                continue;
            }
            if ((typeLepton == 3) && (packetNumber == 20)) {
                segmentNumber = (result[j * PACKET_SIZE] >> 4) & 0x0f;
                if ((segmentNumber < 1) || (segmentNumber > 4)) {
                    log_message(10, "[ERROR] Wrong segment number " + std::to_string(segmentNumber));
                    break;
                }
            }
        }

        // Procesar segmentos
        int iSegmentStart = 1;
        int iSegmentStop = (typeLepton == 3) ? 4 : 1;

        if (typeLepton == 3 && ((segmentNumber < 1) || (segmentNumber > 4))) {
            n_wrong_segment++;
            continue;
        }

        // Copiar datos al buffer
        if (typeLepton == 3) {
            memcpy(shelf[segmentNumber - 1], result, sizeof(uint8_t) * PACKET_SIZE * PACKETS_PER_FRAME);
            if (segmentNumber != 4) continue;
        } else {
            memcpy(shelf[0], result, sizeof(uint8_t) * PACKET_SIZE * PACKETS_PER_FRAME);
        }

        // Escalado automático de rango
        if (autoRangeMin || autoRangeMax) {
            minValue = (autoRangeMin) ? 65535 : minValue;
            maxValue = (autoRangeMax) ? 0 : maxValue;
            for (int iSegment = iSegmentStart; iSegment <= iSegmentStop; iSegment++) {
                for (int i = 0; i < FRAME_SIZE_UINT16; i++) {
                    if (i % PACKET_SIZE_UINT16 < 2) continue;
                    uint16_t value = (shelf[iSegment - 1][i * 2] << 8) + shelf[iSegment - 1][i * 2 + 1];
                    if (value == 0) continue;
                    if (autoRangeMax && (value > maxValue)) maxValue = value;
                    if (autoRangeMin && (value < minValue)) minValue = value;
                }
            }
            diff = maxValue - minValue;
            scale = 255 / diff;
        }

// Procesar píxeles y guardar temperaturas
    for (int iSegment = iSegmentStart; iSegment <= iSegmentStop; iSegment++) {
        int ofsRow = (typeLepton == 3) ? 30 * (iSegment - 1) : 0;
        for (int i = 0; i < FRAME_SIZE_UINT16; i++) {
            if (i % PACKET_SIZE_UINT16 < 2) continue;

            uint16_t valueFrameBuffer = (shelf[iSegment - 1][i * 2] << 8) + shelf[iSegment - 1][i * 2 + 1];
            if (valueFrameBuffer == 0) {
                n_zero_value_drop_frame++;
                break;
            }

            // Convertir a temperatura en Kelvin (ajustar según Lepton 3.5)
            float tempKelvin = valueFrameBuffer * 0.01f;
            int row, column;
            if (typeLepton == 3) {
                column = (i % PACKET_SIZE_UINT16) - 2 + (myImageWidth / 2) * ((i % (PACKET_SIZE_UINT16 * 2)) / PACKET_SIZE_UINT16);
                row = i / PACKET_SIZE_UINT16 / 2 + ofsRow;
            } else {
                column = (i % PACKET_SIZE_UINT16) - 2;
                row = i / PACKET_SIZE_UINT16;
            }

            // Guardar temperatura en la matriz
            if (row < myImageHeight && column < myImageWidth) {
                tempMatrix[row][column] = tempKelvin;
            }
            
                // Colorear la imagen
                uint16_t value = (valueFrameBuffer - minValue) * scale;
                int ofs_r = 3 * value + 0; if (colormapSize <= ofs_r) ofs_r = colormapSize - 1;
                int ofs_g = 3 * value + 1; if (colormapSize <= ofs_g) ofs_g = colormapSize - 1;
                int ofs_b = 3 * value + 2; if (colormapSize <= ofs_b) ofs_b = colormapSize - 1;
                QRgb color = qRgb(colormap[ofs_r], colormap[ofs_g], colormap[ofs_b]);
                myImage.setPixel(column, row, color);
            }
        }

      

        // Emitir señales
        emit updateImage(myImage);
        emit updateTemperatures(tempMatrix);
        
        // Enviar datos por serial al ESP32
        sendToESP32(tempMatrix);
    }

    // Cerrar puerto SPI
    SpiClosePort(0);
}

void LeptonThread::performFFC() {
    lepton_perform_ffc();
}

void LeptonThread::log_message(uint16_t level, std::string msg) {
    if (level <= loglevel) {
        std::cerr << msg << std::endl;
    }
}
