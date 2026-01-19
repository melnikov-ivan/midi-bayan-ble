"""
Главный файл для CircuitPython.
Инициализирует BLE MIDI и USB MIDI, постоянно отправляет примеры и обрабатывает BLE сообщения.
"""

import time
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
print("Запуск системы: примеры MIDI + обработка BLE")
print("="*50)

# Список примеров для выполнения
examples = [
    ("Последовательность нот", controller.example_sequence),
    ("Control Change", controller.example_control_change),
    ("Pitch Bend", controller.example_pitch_bend),
    ("Аккорды", controller.example_chords),
]

# Основной цикл: постоянно запускаем примеры и обрабатываем BLE
while True:
    # Запускаем все примеры по очереди
    for example_name, example_func in examples:
        # Обрабатываем BLE сообщения перед каждым примером
        read.process_ble_messages()
        
        print(f"\n=== Запуск примера: {example_name} ===")
        try:
            example_func()
        except Exception as e:
            print(f"Ошибка в примере: {e}")
            import traceback
            traceback.print_exception(e, e, e.__traceback__)
        
        # Обрабатываем BLE сообщения после каждого примера
        read.process_ble_messages()
        
        # Небольшая пауза между примерами
        time.sleep(1.0)
    
    print("\n" + "="*50)
    print("Цикл примеров завершён, повторяем...")
    print("="*50)
    time.sleep(1.0)
