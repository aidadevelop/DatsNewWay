from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class GameResult:
    """Результат одной игры"""
    round_id: str
    score: int
    max_length: int
    foods_eaten: int
    deaths: int
    timestamp: str

@dataclass
class SnakeStats:
    """Статистика змейки"""
    total_games: int = 0
    total_score: int = 0
    best_score: int = 0
    total_foods: int = 0
    best_length: int = 0
    successful_moves: Dict[str, int] = None  # хэш состояния -> количество успешных ходов
    failed_moves: Dict[str, int] = None  # хэш состояния -> количество неудачных ходов
    
    def __post_init__(self):
        if self.successful_moves is None:
            self.successful_moves = defaultdict(int)
        if self.failed_moves is None:
            self.failed_moves = defaultdict(int)

class StatsManager:
    def __init__(self):
        """Инициализация менеджера статистики"""
        self.stats_file = "snake_stats.json"
        self.current_stats = {
            "points": 0,
            "length": 0,
            "deaths": 0,
            "games_played": 0,
            "max_points": 0,
            "max_length": 0
        }
        self.load_stats()
        
    def load_stats(self):
        """Загрузка статистики из файла"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    self.current_stats = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")
            
    def save_stats(self):
        """Сохранение статистики в файл"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.current_stats, f, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения статистики: {e}")
            
    def update(self, points: int = 0, length: int = 0, deaths: int = 0):
        """
        Обновление текущей статистики
        
        Args:
            points: Текущие очки
            length: Текущая длина змейки
            deaths: Количество смертей
        """
        # Обновляем текущие значения
        self.current_stats["points"] = points
        self.current_stats["length"] = length
        self.current_stats["deaths"] = deaths
        
        # Обновляем максимальные значения
        if points > self.current_stats["max_points"]:
            self.current_stats["max_points"] = points
        if length > self.current_stats["max_length"]:
            self.current_stats["max_length"] = length
            
        # Сохраняем статистику
        self.save_stats()
        
    def get_summary(self) -> Dict:
        """
        Получение сводки статистики
        
        Returns:
            Dict: Статистика игры
        """
        return {
            "Текущие очки": self.current_stats["points"],
            "Максимум очков": self.current_stats["max_points"],
            "Текущая длина": self.current_stats["length"],
            "Максимальная длина": self.current_stats["max_length"],
            "Смертей": self.current_stats["deaths"],
            "Игр сыграно": self.current_stats["games_played"]
        }
