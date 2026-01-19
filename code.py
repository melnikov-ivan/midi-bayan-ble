"""
Главный файл для CircuitPython.
Читает MIDI команды по BLE и отправляет их в USB MIDI.
"""

import controller
import read

# Инициализация USB MIDI (автоматически при импорте controller)
print("Инициализация USB MIDI...")
if controller.midi is None:
    print("Ошибка: USB MIDI не инициализирован")
else:
    print("USB MIDI готов")

# Инициализация BLE MIDI
print("\nИнициализация BLE MIDI...")
if not read.init_ble():
    print("Ошибка: BLE MIDI не инициализирован")
else:
    print("BLE MIDI готов")

print("\n" + "="*50)
print("Система готова: чтение BLE MIDI -> отправка в USB MIDI")
print("="*50)

# Запускаем основной цикл обработки BLE подключений
read.run_ble_loop()
