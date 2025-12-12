"""
Пример создания BLE MIDI сервиса с характеристикой для чтения и записи.
Клиент может подключиться и записать значение в характеристику.
"""

import time
import adafruit_ble
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services import Service
from adafruit_ble.uuid import VendorUUID
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics.stream import StreamIn


# Определяем кастомный MIDI сервис
class MIDIService(Service):
    """BLE MIDI сервис."""

    # UUID стандартного BLE MIDI сервиса
    uuid = VendorUUID("03b80e5a-ede8-4b33-a751-6ce34ec4c700")

    # MIDI I/O характеристика
    # Поддерживает: чтение, запись без ответа, уведомления
    _midi_io = Characteristic(
        uuid=VendorUUID("7772e5db-3868-4112-a1a9-f2669d106bf3"),
        properties=(
            Characteristic.READ |
            Characteristic.WRITE_NO_RESPONSE |
            Characteristic.NOTIFY
        ),
        max_length=20,
        fixed_length=False,
    )

    def __init__(self):
        super().__init__()
        self._last_value = None

    @property
    def value(self):
        """Получить текущее значение характеристики."""
        return self._midi_io

    def read_value(self):
        """Читает значение из характеристики, если оно изменилось."""
        current = bytes(self._midi_io)
        if current != self._last_value and len(current) > 0:
            self._last_value = current
            return current
        return None

    def write_value(self, data):
        """Записывает значение в характеристику (для уведомлений клиента)."""
        self._midi_io = data


# Создаём экземпляр сервиса
midi_service = MIDIService()

# Настраиваем BLE радио
ble = adafruit_ble.BLERadio()
ble.name = "MIDI Bayan"  # Имя устройства

# Отключаем существующие соединения
if ble.connected:
    for connection in ble.connections:
        connection.disconnect()

# Создаём рекламное объявление с нашим сервисом
advertisement = ProvideServicesAdvertisement(midi_service)

print("Запуск BLE рекламы...")
print(f"Имя устройства: {ble.name}")
ble.start_advertising(advertisement)

while True:
    print("Ожидание подключения...")

    while not ble.connected:
        pass

    print("Клиент подключился!")

    while ble.connected:
        # Читаем новое значение из характеристики
        received = midi_service.read_value()

        if received is not None:
            # Выводим полученные байты в hex формате
            hex_str = " ".join(f"{b:02X}" for b in received)
            print(f"Получено: [{hex_str}]")

            # Парсим BLE MIDI пакет
            # Формат: timestamp_header (1 byte) + timestamp (1 byte) + midi_data
            if len(received) >= 3:
                timestamp_header = received[0]
                timestamp = received[1]
                midi_data = received[2:]

                midi_hex = " ".join(f"{b:02X}" for b in midi_data)
                print(f"MIDI данные: [{midi_hex}]")

                # Пример: если это Note On (0x9n)
                if len(midi_data) >= 3 and (midi_data[0] & 0xF0) == 0x90:
                    channel = midi_data[0] & 0x0F
                    note = midi_data[1]
                    velocity = midi_data[2]
                    print(f"  Note On: канал={channel}, нота={note}, velocity={velocity}")

                # Пример: если это Note Off (0x8n)
                elif len(midi_data) >= 3 and (midi_data[0] & 0xF0) == 0x80:
                    channel = midi_data[0] & 0x0F
                    note = midi_data[1]
                    velocity = midi_data[2]
                    print(f"  Note Off: канал={channel}, нота={note}, velocity={velocity}")

        time.sleep(0.01)  # Небольшая задержка

    print("Клиент отключился")
    print("Перезапуск рекламы...")
    ble.start_advertising(advertisement)
