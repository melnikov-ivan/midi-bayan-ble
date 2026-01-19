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
import controller


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
        try:
            current = bytes(self._midi_io)
            if current != self._last_value and len(current) > 0:
                self._last_value = current
                return current
        except Exception as e:
            # Игнорируем ошибки чтения (характеристика может быть пустой)
            pass
        return None

    def write_value(self, data):
        """Записывает значение в характеристику (для уведомлений клиента)."""
        self._midi_io = data


def _process_midi_message(midi_data):
    """
    Обрабатывает MIDI сообщение и отправляет его в USB MIDI через controller.
    
    Параметры:
    - midi_data: байты MIDI данных (без timestamp заголовка)
    """
    if len(midi_data) < 1:
        return
    
    status_byte = midi_data[0]
    message_type = status_byte & 0xF0
    channel = status_byte & 0x0F
    
    # Note Off (0x80-0x8F)
    if message_type == 0x80 and len(midi_data) >= 3:
        note = midi_data[1]
        velocity = midi_data[2]
        print(f"  Note Off: канал={channel}, нота={note}, velocity={velocity}")
        controller.send_note_off(note, velocity, channel)
    
    # Note On (0x90-0x9F)
    elif message_type == 0x90 and len(midi_data) >= 3:
        note = midi_data[1]
        velocity = midi_data[2]
        # Note On с velocity=0 эквивалентен Note Off
        if velocity == 0:
            print(f"  Note Off (via Note On): канал={channel}, нота={note}")
            controller.send_note_off(note, 0, channel)
        else:
            print(f"  Note On: канал={channel}, нота={note}, velocity={velocity}")
            controller.send_note_on(note, velocity, channel)
    
    # Control Change (0xB0-0xBF)
    elif message_type == 0xB0 and len(midi_data) >= 3:
        control = midi_data[1]
        value = midi_data[2]
        print(f"  Control Change: канал={channel}, контроллер={control}, значение={value}")
        controller.send_control_change(control, value, channel)
    
    # Program Change (0xC0-0xCF)
    elif message_type == 0xC0 and len(midi_data) >= 2:
        program = midi_data[1]
        print(f"  Program Change: канал={channel}, программа={program}")
        controller.send_program_change(program, channel)
    
    # Pitch Bend (0xE0-0xEF)
    elif message_type == 0xE0 and len(midi_data) >= 3:
        # Pitch bend: 14-bit value, LSB first
        lsb = midi_data[1]
        msb = midi_data[2]
        value = (msb << 7) | lsb
        print(f"  Pitch Bend: канал={channel}, значение={value}")
        controller.send_pitch_bend(value, channel)
    
    # Polyphonic Key Pressure / Aftertouch (0xA0-0xAF)
    elif message_type == 0xA0 and len(midi_data) >= 3:
        note = midi_data[1]
        pressure = midi_data[2]
        print(f"  Aftertouch: канал={channel}, нота={note}, давление={pressure}")
        # Послекасание обычно отправляется как Control Change или игнорируется
    
    # Channel Pressure / Aftertouch (0xD0-0xDF)
    elif message_type == 0xD0 and len(midi_data) >= 2:
        pressure = midi_data[1]
        print(f"  Channel Aftertouch: канал={channel}, давление={pressure}")
        # Послекасание обычно отправляется как Control Change или игнорируется
    
    else:
        # Неизвестный или необработанный тип сообщения
        print(f"  Необработанное MIDI сообщение: тип=0x{message_type:02X}, канал={channel}, данные={[hex(b) for b in midi_data]}")


# Глобальные переменные для BLE
midi_service = None
ble = None
advertisement = None


def init_ble():
    """Инициализирует BLE MIDI сервис и начинает рекламу."""
    global midi_service, ble, advertisement
    
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
    return True


def process_ble_messages():
    """
    Обрабатывает входящие BLE MIDI сообщения.
    Должна вызываться периодически в основном цикле.
    """
    global midi_service, ble, advertisement
    
    if midi_service is None or ble is None:
        return
    
    # Если не подключен, просто возвращаемся
    if not ble.connected:
        return
    
    try:
        # Читаем новое значение из характеристики
        received = midi_service.read_value()
        
        if received is not None and len(received) > 0:
            # Выводим полученные байты в hex формате
            hex_str = " ".join(f"{b:02X}" for b in received)
            print(f"Получено BLE: [{hex_str}]")
            
            # Парсим BLE MIDI пакет
            # Формат BLE MIDI: timestamp_header (1 byte) + timestamp (1 byte) + midi_data
            # Но данные могут приходить и без заголовка, просто как MIDI данные
            midi_data = None
            
            if len(received) >= 3:
                # Проверяем, есть ли timestamp заголовок
                # BLE MIDI заголовок обычно начинается с 0x80
                if received[0] & 0x80 == 0x80:
                    # Есть timestamp заголовок
                    timestamp_header = received[0]
                    timestamp = received[1]
                    midi_data = received[2:]
                else:
                    # Нет заголовка, это просто MIDI данные
                    midi_data = received
            elif len(received) >= 1:
                # Короткий пакет, возможно просто MIDI данные
                midi_data = received
            
            if midi_data is not None and len(midi_data) > 0:
                midi_hex = " ".join(f"{b:02X}" for b in midi_data)
                print(f"MIDI данные: [{midi_hex}]")
                
                # Обрабатываем MIDI сообщения и отправляем в USB MIDI
                _process_midi_message(midi_data)
    except Exception as e:
        print(f"Ошибка при обработке BLE сообщения: {e}")


def run_ble_loop():
    """
    Запускает основной цикл обработки BLE подключений.
    Для использования в отдельном потоке или как основной цикл.
    """
    global ble, advertisement
    
    if ble is None:
        print("Ошибка: BLE не инициализирован. Вызовите init_ble() сначала.")
        return
    
    while True:
        print("Ожидание подключения...")
        
        while not ble.connected:
            time.sleep(0.1)
        
        print("Клиент подключился!")
        
        while ble.connected:
            process_ble_messages()
            time.sleep(0.01)  # Небольшая задержка
        
        print("Клиент отключился")
        print("Перезапуск рекламы...")
        ble.start_advertising(advertisement)
