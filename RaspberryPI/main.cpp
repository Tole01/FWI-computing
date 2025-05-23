#include <QApplication>
#include <QThread>
#include <QMutex>
#include <QMessageBox>
#include <QColor>
#include <QLabel>
#include <QtDebug>
#include <QString>
#include <QPushButton>
#include <QTableWidget>
#include <QHeaderView>
#include <QFile>
#include <QTextStream>

#include "LeptonThread.h"
#include "MyLabel.h"

void printUsage(char *cmd) {
    char *cmdname = basename(cmd);
    printf("Usage: %s [OPTION]...\n"
           " -h      display this help and exit\n"
           " -cm x   select colormap\n"
           "           1 : rainbow\n"
           "           2 : grayscale\n"
           "           3 : ironblack [default]\n"
           " -tl x   select type of Lepton\n"
           "           2 : Lepton 2.x [default]\n"
           "           3 : Lepton 3.x\n"
           " -ss x   SPI bus speed [MHz] (10 - 30)\n"
           "           20 : 20MHz [default]\n"
           " -min x  override minimum value for scaling (0 - 65535)\n"
           "           [default] automatic scaling range adjustment\n"
           "           e.g. -min 30000\n"
           " -max x  override maximum value for scaling (0 - 65535)\n"
           "           [default] automatic scaling range adjustment\n"
           "           e.g. -max 32000\n"
           " -d x    log level (0-255)\n"
           "", cmdname);
    return;
}

int main(int argc, char **argv) {
    // Configuración por defecto
    int typeColormap = 3;
    int typeLepton = 3;
    int spiSpeed = 20;
    int rangeMin = -1;
    int rangeMax = -1;
    int loglevel = 0;

    // Procesar argumentos de línea de comandos
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-h") == 0) {
            printUsage(argv[0]);
            exit(0);
        } else if (strcmp(argv[i], "-d") == 0) {
            if ((i + 1 != argc) && (strncmp(argv[i + 1], "-", 1) != 0)) {
                loglevel = std::atoi(argv[i + 1]) & 0xFF;
                i++;
            }
        } else if ((strcmp(argv[i], "-cm") == 0) && (i + 1 != argc)) {
            int val = std::atoi(argv[i + 1]);
            if (val == 1 || val == 2) {
                typeColormap = val;
                i++;
            }
        } else if ((strcmp(argv[i], "-tl") == 0) && (i + 1 != argc)) {
            int val = std::atoi(argv[i + 1]);
            if (val == 3) {
                typeLepton = val;
                i++;
            }
        } else if ((strcmp(argv[i], "-ss") == 0) && (i + 1 != argc)) {
            int val = std::atoi(argv[i + 1]);
            if (val >= 10 && val <= 30) {
                spiSpeed = val;
                i++;
            }
        } else if ((strcmp(argv[i], "-min") == 0) && (i + 1 != argc)) {
            int val = std::atoi(argv[i + 1]);
            if (val >= 0 && val <= 65535) {
                rangeMin = val;
                i++;
            }
        } else if ((strcmp(argv[i], "-max") == 0) && (i + 1 != argc)) {
            int val = std::atoi(argv[i + 1]);
            if (val >= 0 && val <= 65535) {
                rangeMax = val;
                i++;
            }
        }
    }

    QApplication a(argc, argv);

    // Configuración de la ventana principal
    QWidget *mainWindow = new QWidget;
    mainWindow->setWindowTitle("FLIR Lepton Thermal Camera");
    mainWindow->setGeometry(400, 300, 800, 600);

    // Configuración de la imagen térmica
    MyLabel thermalImageLabel(mainWindow);
    thermalImageLabel.setGeometry(10, 10, 320, 240);

    // Botón para FFC (Flat Field Correction)
    QPushButton *ffcButton = new QPushButton("Perform FFC", mainWindow);
    ffcButton->setGeometry(320/2 - 50, 260, 100, 30);

    // Configuración de la tabla de temperaturas
    QTableWidget *tempTable = new QTableWidget(120, 160, mainWindow);
    tempTable->setGeometry(340, 10, 450, 280);
    tempTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    tempTable->verticalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    tempTable->setEditTriggers(QAbstractItemView::NoEditTriggers);

    // Configuración del hilo de la cámara térmica
    LeptonThread *leptonThread = new LeptonThread();
    leptonThread->setLogLevel(loglevel);
    leptonThread->useColormap(typeColormap);
    leptonThread->useLepton(typeLepton);
    leptonThread->useSpiSpeedMhz(spiSpeed);
    
    if (rangeMin >= 0) leptonThread->useRangeMinValue(rangeMin);
    if (rangeMax >= 0) leptonThread->useRangeMaxValue(rangeMax);

    // Conexiones de señales
    QObject::connect(leptonThread, &LeptonThread::updateImage, 
                    &thermalImageLabel, &MyLabel::setImage);
    
    QObject::connect(ffcButton, &QPushButton::clicked, 
                    leptonThread, &LeptonThread::performFFC);

    // Conexión para actualizar la tabla de temperaturas (opcional)
    QObject::connect(leptonThread, &LeptonThread::updateTemperatures,
        [tempTable](const std::vector<std::vector<float>>& temps) {
            // Mostrar solo una parte de la matriz en la tabla (opcional)
            const int displayRows = std::min(120, (int)temps.size());
            const int displayCols = std::min(160, temps.empty() ? 0 : (int)temps[0].size());
            
            tempTable->setRowCount(displayRows);
            tempTable->setColumnCount(displayCols);
            
            for (int y = 0; y < displayRows; ++y) {
                for (int x = 0; x < displayCols; ++x) {
                    float tempCelsius = temps[y][x] - 273.15f;
                    
                    QTableWidgetItem *item = tempTable->item(y, x);
                    if (!item) {
                        item = new QTableWidgetItem();
                        tempTable->setItem(y, x, item);
                    }
                    item->setText(QString::number(tempCelsius, 'f', 1) + " °C");
                    
                    // Opcional: colorear celdas según temperatura
                    if (tempCelsius < 30) item->setBackground(Qt::blue);
                    else if (tempCelsius > 70) item->setBackground(Qt::red);
                    else item->setBackground(Qt::green);
                }
            }
        });
        
    // Iniciar el hilo y mostrar la ventana
    leptonThread->start();
    mainWindow->show();

    return a.exec();
}
