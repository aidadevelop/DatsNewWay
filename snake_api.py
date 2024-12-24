import requests
from typing import Dict, Optional, List
import time

class SnakeAPI:
    def __init__(self, auth_token: str):
        """
        Инициализация API клиента
        
        Args:
            auth_token: Токен авторизации
        """
        self.base_url = "https://games-test.datsteam.dev"
        self.headers = {
            "X-Auth-Token": auth_token,
            "Content-Type": "application/json"
        }
        
    def get_active_rounds(self) -> Optional[List[Dict]]:
        """
        Получение списка активных раундов
        
        Returns:
            Optional[List[Dict]]: Список активных раундов или None
        """
        try:
            response = requests.get(
                f"{self.base_url}/rounds/snake3d",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get('rounds', [])
        except Exception as e:
            print(f"Ошибка получения списка раундов: {e}")
            return None
            
    def join_round(self, round_info: Dict) -> List[str]:
        """
        Подключение к раунду через начальный ход
        
        Args:
            round_info: Информация о раунде
            
        Returns:
            List[str]: Список ID змеек
        """
        try:
            # Отправляем начальный ход для подключения
            data = {
                "snakes": [
                    {"id": "", "direction": [1, 0, 0]}  # Начальное направление вправо
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/play/snake3d/player/move",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            
            # Получаем состояние игры и ищем наши змейки
            game_state = response.json()
            snake_ids = []
            
            for snake in game_state.get('snakes', []):
                if snake['status'] == 'alive':
                    snake_ids.append(snake['id'])
                    
            if snake_ids:
                print(f"Успешное подключение! ID змеек: {snake_ids}")
            return snake_ids
            
        except Exception as e:
            print(f"Ошибка подключения к раунду: {e}")
            return []
            
    def make_move(self, round_info: Dict, moves: List[Dict]) -> bool:
        """
        Сделать ход
        
        Args:
            round_info: Информация о раунде
            moves: Список ходов для каждой змейки
                [{"id": "snake_id", "direction": [x, y, z]}, ...]
            
        Returns:
            bool: True если ход успешен
        """
        try:
            data = {"snakes": moves}
            
            response = requests.post(
                f"{self.base_url}/play/snake3d/player/move",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Ошибка выполнения хода: {e}")
            return False
            
    def get_game_state(self, round_info: Dict) -> Optional[Dict]:
        """
        Получение состояния игры через пустой ход
        
        Args:
            round_info: Информация о раунде
            
        Returns:
            Optional[Dict]: Состояние игры или None
        """
        try:
            # Отправляем пустой ход для получения состояния
            data = {"snakes": []}
            
            response = requests.post(
                f"{self.base_url}/play/snake3d/player/move",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка получения состояния игры: {e}")
            return None
