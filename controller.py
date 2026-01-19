"""
Пример отправки MIDI команд по USB.
Использует встроенный USB MIDI интерфейс CircuitPython.
"""

import time
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange
from adafruit_midi.pitch_bend import PitchBend
from adafruit_midi.program_change import ProgramChange

# Инициализация USB MIDI
midi = None

def init_midi():
    """Инициализирует USB MIDI интерфейс."""
    global midi
    try:
        # Проверяем доступность USB MIDI портов
        if len(usb_midi.ports) < 2:
            print("Ошибка: USB MIDI порты недоступны")
            return False
        
        # usb_midi.ports[1] - это выходной порт (MIDI OUT)
        midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)
        print("USB MIDI Controller готов")
        print("Канал MIDI: 0")
        return True
    except Exception as e:
        print(f"Ошибка инициализации USB MIDI: {e}")
        return False

# Автоматическая инициализация при импорте
if not init_midi():
    print("Предупреждение: USB MIDI не инициализирован")


def send_note_on(note, velocity=127, channel=0):
    """
    Отправляет MIDI Note On сообщение.
    
    Параметры:
    - note: номер ноты (0-127) или строка (например, "C4", "A#3")
    - velocity: скорость нажатия (0-127)
    - channel: MIDI канал (0-15)
    """
    if midi is None:
        print("Ошибка: MIDI не инициализирован")
        return
    midi.send(NoteOn(note, velocity), channel=channel)
    print(f"Note On: нота={note}, velocity={velocity}, канал={channel}")


def send_note_off(note, velocity=0, channel=0):
    """
    Отправляет MIDI Note Off сообщение.
    
    Параметры:
    - note: номер ноты (0-127) или строка
    - velocity: скорость отпускания (0-127)
    - channel: MIDI канал (0-15)
    """
    if midi is None:
        print("Ошибка: MIDI не инициализирован")
        return
    midi.send(NoteOff(note, velocity), channel=channel)
    print(f"Note Off: нота={note}, velocity={velocity}, канал={channel}")


def send_control_change(control, value, channel=0):
    """
    Отправляет MIDI Control Change сообщение.
    
    Параметры:
    - control: номер контроллера (0-127)
    - value: значение контроллера (0-127)
    - channel: MIDI канал (0-15)
    """
    if midi is None:
        print("Ошибка: MIDI не инициализирован")
        return
    midi.send(ControlChange(control, value), channel=channel)
    print(f"Control Change: контроллер={control}, значение={value}, канал={channel}")


def send_pitch_bend(value, channel=0):
    """
    Отправляет MIDI Pitch Bend сообщение.
    
    Параметры:
    - value: значение pitch bend (0-16383, где 8192 - центр)
    - channel: MIDI канал (0-15)
    """
    if midi is None:
        print("Ошибка: MIDI не инициализирован")
        return
    midi.send(PitchBend(value), channel=channel)
    print(f"Pitch Bend: значение={value}, канал={channel}")


def send_program_change(program, channel=0):
    """
    Отправляет MIDI Program Change сообщение.
    
    Параметры:
    - program: номер программы/инструмента (0-127)
    - channel: MIDI канал (0-15)
    """
    if midi is None:
        print("Ошибка: MIDI не инициализирован")
        return
    midi.send(ProgramChange(program), channel=channel)
    print(f"Program Change: программа={program}, канал={channel}")


# Пример 1: Простая последовательность нот
def example_sequence():
    """Проигрывает простую последовательность нот."""
    print("\n=== Пример 1: Последовательность нот ===")
    
    notes = [60, 64, 67, 72]  # C, E, G, C (аккорд C мажор)
    
    for note in notes:
        send_note_on(note, velocity=100)
        time.sleep(0.3)
    
    time.sleep(0.5)
    
    for note in notes:
        send_note_off(note)
        time.sleep(0.1)


# Пример 2: Использование Control Change
def example_control_change():
    """Демонстрирует использование Control Change."""
    print("\n=== Пример 2: Control Change ===")
    
    # Volume (CC 7)
    send_control_change(7, 100)
    time.sleep(0.1)
    
    # Modulation (CC 1)
    send_control_change(1, 64)
    time.sleep(0.1)
    
    # Expression (CC 11)
    send_control_change(11, 127)
    time.sleep(0.1)


# Пример 3: Pitch Bend
def example_pitch_bend():
    """Демонстрирует использование Pitch Bend."""
    print("\n=== Пример 3: Pitch Bend ===")
    
    # Играем ноту
    send_note_on(60, velocity=100)
    time.sleep(0.1)
    
    # Плавный pitch bend вверх
    for i in range(8192, 16383, 100):
        send_pitch_bend(i)
        time.sleep(0.01)
    
    # Возврат в центр
    send_pitch_bend(8192)
    time.sleep(0.1)
    
    # Плавный pitch bend вниз
    for i in range(8192, 0, -100):
        send_pitch_bend(i)
        time.sleep(0.01)
    
    # Возврат в центр
    send_pitch_bend(8192)
    time.sleep(0.1)
    
    send_note_off(60)


# Пример 4: Смена программы
def example_program_change():
    """Демонстрирует смену программы/инструмента."""
    print("\n=== Пример 4: Program Change ===")
    
    # Меняем программу на фортепиано (1)
    send_program_change(1)
    time.sleep(0.1)
    send_note_on(60, velocity=100)
    time.sleep(0.3)
    send_note_off(60)
    time.sleep(0.2)
    
    # Меняем программу на орган (20)
    send_program_change(20)
    time.sleep(0.1)
    send_note_on(60, velocity=100)
    time.sleep(0.3)
    send_note_off(60)


# Пример 5: Аккорды
def example_chords():
    """Играет аккорды."""
    print("\n=== Пример 5: Аккорды ===")
    
    # C мажор
    chord_c = [60, 64, 67]  # C, E, G
    for note in chord_c:
        send_note_on(note, velocity=100)
    time.sleep(0.5)
    for note in chord_c:
        send_note_off(note)
    time.sleep(0.2)
    
    # F мажор
    chord_f = [65, 69, 72]  # F, A, C
    for note in chord_f:
        send_note_on(note, velocity=100)
    time.sleep(0.5)
    for note in chord_f:
        send_note_off(note)
    time.sleep(0.2)
    
    # G мажор
    chord_g = [67, 71, 74]  # G, B, D
    for note in chord_g:
        send_note_on(note, velocity=100)
    time.sleep(0.5)
    for note in chord_g:
        send_note_off(note)


def run_examples():
    """Запускает все примеры использования MIDI в бесконечном цикле."""
    if midi is None:
        print("Ошибка: MIDI не инициализирован. Запустите init_midi() сначала.")
        return
    
    print("\n" + "="*50)
    print("USB MIDI Controller - Примеры использования")
    print("="*50)
    
    try:
        while True:
            # Запускаем примеры по очереди
            example_sequence()
            time.sleep(1)
            
            example_control_change()
            time.sleep(1)
            
            example_pitch_bend()
            time.sleep(1)
            
            # example_program_change()
            # time.sleep(1)
            
            example_chords()
            time.sleep(1)
            
            print("\n" + "="*50)
            print("Цикл завершён, повторяем...")
            print("="*50)
            time.sleep(1)
        
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exception(e, e, e.__traceback__)
