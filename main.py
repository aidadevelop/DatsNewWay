import sys
import time
from snake_api import SnakeAPI
from snake_game import SnakeGame

def main():
    # Инициализация API клиента
    AUTH_TOKEN = "c2290c4c-45f4-4a3b-bbe7-6f1bcf1b0603"  # Замените на свой токен
    api = SnakeAPI(AUTH_TOKEN)
    
    try:
        while True:
            print("\nОжидаем раунд...")
            
            # Получаем список активных раундов
            rounds = api.get_active_rounds()
            if not rounds:
                print("Не удалось получить список раундов")
                time.sleep(1)  # Ждем немного перед следующей попыткой
                continue
                
            # Выбираем первый доступный раунд
            current_round = rounds[0]
            print(f"Подключаемся к раунду: {current_round['name']}")
            
            # Создаем и запускаем игру
            game = SnakeGame(api, current_round)
            if not game.run():
                print("Игра завершена с ошибкой")
                break
                
    except KeyboardInterrupt:
        print("\nИгра остановлена пользователем")
        sys.exit(0)
        
if __name__ == "__main__":
    main()