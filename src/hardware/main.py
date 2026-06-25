# src/hardware/main.py
# ────────────────────────────────────────────────────────────
# Sistema RFID + Deep Learning — Raspberry Pi Pico (RP2040)
# Foco Exclusivo: MFRC522 e Classificação Serial
#
# Hardware:
#   RC522 → SPI0
#   MISO  → GP16
#   CS    → GP17
#   SCK   → GP18
#   MOSI  → GP19
#   RST   → GP20
#
# Upload:
#   mpremote cp src/hardware/main.py       :main.py
#   mpremote cp src/hardware/rfid_rc522.py :rfid_rc522.py
#   mpremote cp src/model/model.py         :model.py
# ────────────────────────────────────────────────────────────

from machine import Pin, SPI
import time
import json
import gc

gc.collect()

from rfid_rc522 import MFRC522
import model

gc.collect()

# ── Configuração SPI para a Pico (RP2040) ────────────────────
# Utilizando o bloco SPI0 padrão com os pinos designados
spi = SPI(0, baudrate=1_000_000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(19), miso=Pin(16))

# Inicializa o driver MFRC522
rfid = MFRC522(spi=spi, gpioRst=Pin(20), gpioCs=Pin(17))

# ── Banco de UIDs ─────────────────────────────────────────────
DB_FILE = "rfid_db.json"

def db_load():
    try:
        with open(DB_FILE) as f:
            return json.load(f)
    except:
        return {}

def db_save(database):
    with open(DB_FILE, "w") as f:
        json.dump(database, f)

db = db_load()
history = {}
WINDOW = 8

# ── Controle Temporal ─────────────────────────────────────────
def update_history(uid_hex, uid_hash):
    now   = time.localtime()
    hora  = (now[3] * 3600 + now[4] * 60 + now[5])
    dia   = now[6]

    if uid_hex not in history:
        history[uid_hex] = []

    hist = history[uid_hex]
    if hist:
        last_t = hist[-1][2] * 86400
        delta  = max(0, hora - last_t) / 86400
    else:
        delta  = 0.5 

    feat = [hora / 86400, dia / 7, delta, uid_hash / 255]
    hist.append(feat)
    
    if len(hist) > WINDOW:
        hist.pop(0)

    while len(hist) < WINDOW:
        hist.insert(0, feat)

    return hist[-WINDOW:]

def uid_to_hex(uid_bytes):
    return "".join(f"{b:02X}" for b in uid_bytes)

# ── Loop Principal ────────────────────────────────────────────
print("="*45)
print("  RFID + Deep Learning (RP2040 / Pico)")
print("  Status: Aguardando leitura de tag...")
print("="*45)

while True:
    stat, tag_type = rfid.request(rfid.REQIDL)
    if stat != rfid.OK:
        time.sleep_ms(50)
        continue

    stat, raw_uid = rfid.anticoll()
    if stat != rfid.OK:
        continue

    uid_hex  = uid_to_hex(raw_uid)
    uid_hash = sum(raw_uid) % 256
    t_start  = time.ticks_ms()

    # Log temporal
    lt = time.localtime()
    ts = f"{lt[3]:02d}:{lt[4]:02d}:{lt[5]:02d}"

    # Auto-Cadastro para UIDs Desconhecidos (Já que removemos o botão)
    if uid_hex not in db:
        print(f"[{ts}] NOVO CARTÃO: UID={uid_hex}")
        db[uid_hex] = {"nome": f"User_{uid_hex[:4]}", "hash": uid_hash}
        db_save(db)
        print(f" -> Auto-cadastrado como {db[uid_hex]['nome']}. Leia novamente.")
        time.sleep(1.5)
        continue

    # Inferência com a LSTM Importada
    features = update_history(uid_hex, uid_hash)
    label, conf = model.classify(features)
    t_ms = time.ticks_diff(time.ticks_ms(), t_start)
    
    # Formatação de saída Serial
    print(f"[{ts}] UID: {uid_hex} | Status: {label:<10} | Conf: {conf}% | {t_ms}ms")

    # Pausa para evitar múltiplas leituras consecutivas do mesmo toque
    time.sleep(1.5)