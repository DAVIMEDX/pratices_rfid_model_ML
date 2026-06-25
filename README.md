rfid-deeplearning-pico2w/
├── src/
│   ├── hardware/
│   │   ├── main.py          # Código principal de execução
│   │   └── rfid_rc522.py    # Driver do módulo
│   └── model/
│       └── model.mpy        # Modelo treinado
├── README.md                # O guia que preparamos
└── requirements.txt         # (Opcional) Ferramentas para PC (mpremote, etc.)

# RFID Deep Learning - Raspberry Pi Pico

Este projeto implementa um sistema de autenticação e análise de tags RFID utilizando **Inteligência Artificial (LSTM)** rodando localmente em uma **Raspberry Pi Pico (RP2040)**. 
O sistema foi projetado para ser minimalista, eficiente e de baixo consumo, eliminando componentes periféricos desnecessários para focar no processamento de dados na borda.

## 🚀 Funcionalidades
- **Leitura SPI:** Driver otimizado para o leitor MFRC522.
- **Edge AI:** Inferência de rede neural (LSTM) para processamento temporal de sequências RFID.
- **Autonomia:** Implementação via *Frozen Modules* no MicroPython para inicialização instantânea e estabilidade.

## 📌 Esquema de Conexão (SPI)

| Pino RC522 | Pino Pico (GPIO) | Função |
| :--- | :--- | :--- |
| SDA (CS) | GP17 | Chip Select |
| SCK | GP18 | Clock |
| MOSI | GP19 | Master Out Slave In |
| MISO | GP16 | Master In Slave Out |
| RST | GP20 | Reset |
| 3.3V | 3V3 (OUT) | Alimentação |
| GND | GND | Terra |

> ⚠️ **Atenção:** Nunca alimente o RC522 com 5V, pois isso pode danificar permanentemente os pinos da Raspberry Pi Pico. Utilize sempre o pino 3V3.

## 🚀 Instalação via mpremote

Caso prefira não compilar o firmware, você pode enviar os arquivos diretamente para a placa:

1. **Conectar e enviar:**
   ```bash
   mpremote cp src/hardware/rfid_rc522.py :rfid_rc522.py
   mpremote cp src/model/model.mpy :model.mpy
   mpremote cp src/hardware/main.py :main.py
