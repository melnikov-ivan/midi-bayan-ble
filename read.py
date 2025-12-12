"""
Пример создания BLE сервиса с характеристикой и прослушиванием новых значений.
"""

import time
import adafruit_ble
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services import Service
from adafruit_ble.uuid import VendorUUID
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics.int import Uint8Characteristic


# Определяем кастомный сервис с уникальным UUID
class MyCustomService(Service):
    """Кастомный BLE сервис."""

    # UUID сервиса (сгенерируйте свой уникальный UUID)
    uuid = VendorUUID("12345678-1234-5678-1234-56789abcdef0")

    # Характеристика для записи (клиент может отправлять значения)
    # WRITE - клиент может записывать значения
    # WRITE_NO_RESPONSE - запись без подтверждения (быстрее)
    writable_value = Uint8Characteristic(
        uuid=VendorUUID("12345678-1234-5678-1234-56789abcdef1"),
        properties=Characteristic.WRITE | Characteristic.WRITE_NO_RESPONSE,
        initial_value=0,
    )

    # Характеристика для чтения и уведомлений
    # READ - клиент может читать значение
    # NOTIFY - сервер может отправлять уведомления клиенту
    readable_value = Uint8Characteristic(
        uuid=VendorUUID("12345678-1234-5678-1234-56789abcdef2"),
        properties=Characteristic.READ | Characteristic.NOTIFY,
        initial_value=0,
    )


# Создаём экземпляр сервиса
my_service = MyCustomService()

# Настраиваем BLE радио
ble = adafruit_ble.BLERadio()
ble.name = "MyDevice"  # Имя устройства

# Отключаем существующие соединения
if ble.connected:
    for connection in ble.connections:
        connection.disconnect()

# Создаём рекламное объявление с нашим сервисом
advertisement = ProvideServicesAdvertisement(my_service)

print("Запуск BLE рекламы...")
ble.start_advertising(advertisement)

# Переменная для отслеживания предыдущего значения
last_received_value = my_service.writable_value

while True:
    print("Ожидание подключения...")
    
    while not ble.connected:
        pass
    
    print("Клиент подключился!")
    
    while ble.connected:
        # Проверяем, изменилось ли записанное значение
        current_value = my_service.writable_value
        
        if current_value != last_received_value:
            print(f"Получено новое значение: {current_value}")
            last_received_value = current_value
            
            # Обрабатываем полученное значение
            # Например, отправляем ответ обратно через readable_value
            response = (current_value * 2) % 256  # Просто пример обработки
            my_service.readable_value = response
            print(f"Отправлен ответ: {response}")
        
        time.sleep(0.1)  # Небольшая задержка для экономии энергии
    
    print("Клиент отключился")
    print("Перезапуск рекламы...")
    ble.start_advertising(advertisement)