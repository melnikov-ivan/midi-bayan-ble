"""
Класс для работы с регистром сдвига 74HC165N
Последовательная загрузка битов из параллельного входного регистра
"""
import digitalio
import board


class ShiftRegister74HC165:
    """
    Класс для работы с регистром сдвига 74HC165N
    
    Параметры:
    - load_pin: пин для PL (Parallel Load) - загрузка параллельных данных
    - clock_pin: пин для CP (Clock Pulse) - тактовый сигнал
    - data_pin: пин для Q7 (Serial Output) - последовательный выход данных
    """
    
    def __init__(self, load_pin, clock_pin, data_pin):
        # Настройка пина загрузки (PL)
        self.load = digitalio.DigitalInOut(load_pin)
        self.load.direction = digitalio.Direction.OUTPUT
        self.load.value = True  # По умолчанию HIGH
        
        # Настройка пина тактового сигнала (CP)
        self.clock = digitalio.DigitalInOut(clock_pin)
        self.clock.direction = digitalio.Direction.OUTPUT
        self.clock.value = False  # По умолчанию LOW
        
        # Настройка пина данных (Q7)
        self.data = digitalio.DigitalInOut(data_pin)
        self.data.direction = digitalio.Direction.INPUT
        
    def read(self):
        """
        Читает 8 битов из регистра сдвига
        
        Возвращает:
        - byte: байт с данными (8 битов)
        """
        # Шаг 1: Загрузить параллельные данные
        # Установить PL в LOW для загрузки
        self.load.value = False
        
        # Небольшая задержка для стабилизации
        # В CircuitPython можно использовать time.sleep(0.000001) если нужно
        
        # Шаг 2: Вернуть PL в HIGH для начала сдвига
        self.load.value = True
        
        # Шаг 3: Последовательно читать 8 битов
        byte_value = 0
        
        for i in range(8):
            # Прочитать бит из Q7
            bit = self.data.value
            
            # Добавить бит в байт (старший бит первым)
            byte_value |= (bit << (7 - i))
            
            # Подать тактовый импульс для сдвига следующего бита
            self.clock.value = True
            # Небольшая задержка для стабилизации
            self.clock.value = False
        
        return byte_value
    
    def read_multiple(self, count=1):
        """
        Читает данные из нескольких каскадно соединенных регистров
        
        Параметры:
        - count: количество регистров (по умолчанию 1)
        
        Возвращает:
        - list: список байтов, по одному на каждый регистр
        """
        # Загрузить параллельные данные во все регистры
        self.load.value = False
        self.load.value = True
        
        # Читать данные из всех регистров
        bytes_list = []
        
        for _ in range(count):
            byte_value = 0
            
            for i in range(8):
                bit = self.data.value
                byte_value |= (bit << (7 - i))
                
                self.clock.value = True
                self.clock.value = False
            
            bytes_list.append(byte_value)
        
        return bytes_list
    
    def deinit(self):
        """Освобождает ресурсы пинов"""
        self.load.deinit()
        self.clock.deinit()
        self.data.deinit()


# Пример использования:
if __name__ == "__main__":
    # Пример подключения (замените на ваши пины):
    # PL -> D2
    # CP -> D3
    # Q7 -> D4
    
    # Создать экземпляр регистра
    # shift_reg = ShiftRegister74HC165(
    #     load_pin=board.D2,
    #     clock_pin=board.D3,
    #     data_pin=board.D4
    # )
    
    # Читать данные в цикле
    # while True:
    #     data = shift_reg.read()
    #     print(f"Прочитано: {data:08b} ({data})")
    #     time.sleep(0.1)
