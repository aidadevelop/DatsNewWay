import time
from typing import Dict, List, Optional
import math

class SnakeGame:
    def __init__(self, api, round_info: Dict):
        self.api = api
        self.round_info = round_info
        self.snake_ids = []
        # Статистика для каждой змейки
        self.snake_stats = {}
        # Словарь для хранения текущих целей и направлений змеек
        self.snake_targets = {}  # {snake_id: {"target": food_pos, "direction": [x,y,z]}}
        
    def update_snake_stats(self, snake: Dict):
        """
        Обновляет статистику змейки
        """
        snake_id = snake['id']
        if snake_id not in self.snake_stats:
            self.snake_stats[snake_id] = {
                'normal_food': 0,
                'golden_food': 0,
                'kills': 0,
                'deaths': 0,
                'points': 0,
                'length': 0
            }
            
        # Обновляем статистику
        current_stats = self.snake_stats[snake_id]
        new_stats = {
            'normal_food': snake.get('normalFoodEaten', 0),
            'golden_food': snake.get('goldenFoodEaten', 0),
            'kills': snake.get('kills', 0),
            'deaths': snake.get('deaths', 0),
            'points': snake.get('points', 0),
            'length': len(snake.get('geometry', []))
        }
        
        # Выводим изменения в статистике
        for key, new_value in new_stats.items():
            old_value = current_stats[key]
            if new_value != old_value:
                if key in ['normal_food', 'golden_food']:
                    print(f"Змейка {snake_id} съела {'золотую' if key == 'golden_food' else 'обычную'} мандаринку!")
                elif key == 'kills':
                    print(f"Змейка {snake_id} уничтожила противника!")
                elif key == 'deaths':
                    print(f"Змейка {snake_id} погибла!")
                elif key == 'points' and new_value > old_value:
                    print(f"Змейка {snake_id} заработала {new_value - old_value} очков!")
                    
        # Сохраняем новую статистику
        self.snake_stats[snake_id] = new_stats
        
    def print_stats(self, game_state: Dict):
        """
        Выводит подробную статистику игры
        """
        print("\n=== Статистика игры ===")
        print(f"Ход: {game_state.get('tick', 0)}")
        print(f"Змей на поле: {len(game_state.get('snakes', []))}")
        print(f"Еды на поле: {len(game_state.get('food', []))}")
        
        total_stats = {
            'normal_food': 0,
            'golden_food': 0,
            'kills': 0,
            'deaths': 0,
            'points': 0
        }
        
        print("\n--- Статистика по змейкам ---")
        for snake_id, stats in self.snake_stats.items():
            print(f"\nЗмейка {snake_id}:")
            print(f"  Обычных мандаринок: {stats['normal_food']}")
            print(f"  Золотых мандаринок: {stats['golden_food']}")
            print(f"  Убийств: {stats['kills']}")
            print(f"  Смертей: {stats['deaths']}")
            print(f"  Очков: {stats['points']}")
            print(f"  Длина: {stats['length']}")
            
            # Суммируем статистику
            for key in total_stats:
                total_stats[key] += stats[key]
                
        print("\n--- Общая статистика ---")
        print(f"Всего собрано обычных мандаринок: {total_stats['normal_food']}")
        print(f"Всего собрано золотых мандаринок: {total_stats['golden_food']}")
        print(f"Всего убийств: {total_stats['kills']}")
        print(f"Всего смертей: {total_stats['deaths']}")
        print(f"Всего очков: {total_stats['points']}")
        print("=====================")
        
    def find_nearest_golden_food(self, snake_pos: List[int], foods: List[Dict]) -> Optional[Dict]:
        """
        Находит ближайшую золотую мандаринку
        """
        nearest_food = None
        min_distance = float('inf')
        
        for food in foods:
            if food.get('type') == 'golden':  # Ищем только золотые мандаринки
                food_pos = food['position']
                distance = math.sqrt(
                    (snake_pos[0] - food_pos[0]) ** 2 +
                    (snake_pos[1] - food_pos[1]) ** 2 +
                    (snake_pos[2] - food_pos[2]) ** 2
                )
                if distance < min_distance:
                    min_distance = distance
                    nearest_food = food
                    
        return nearest_food
        
    def calculate_direction(self, snake_pos: List[int], target_pos: List[int]) -> List[int]:
        """
        Вычисляет направление к цели
        """
        direction = [0, 0, 0]
        max_diff = 0
        max_index = 0
        
        # Находим ось с максимальной разницей
        for i in range(3):
            diff = abs(target_pos[i] - snake_pos[i])
            if diff > max_diff:
                max_diff = diff
                max_index = i
                
        # Устанавливаем направление по этой оси
        if target_pos[max_index] > snake_pos[max_index]:
            direction[max_index] = 1
        elif target_pos[max_index] < snake_pos[max_index]:
            direction[max_index] = -1
            
        return direction
        
    def run(self) -> bool:
        """
        Основной игровой цикл
        """
        # Подключаемся к игре
        self.snake_ids = self.api.join_round(self.round_info)
        if not self.snake_ids:
            print("Не удалось подключиться к игре")
            return False
            
        print(f"Подключились к игре! ID змеек: {self.snake_ids}")
        
        # Инициализируем визуализатор и поиск пути
        from snake_visualizer import SnakeVisualizer
        from pathfinder import PathFinder
        
        visualizer = SnakeVisualizer()
        pathfinder = PathFinder()
        
        # Передаем ID наших змеек в визуализатор
        visualizer.set_our_snake_ids(self.snake_ids)
        
        # Начальное направление для каждой змейки
        for snake_id in self.snake_ids:
            self.snake_targets[snake_id] = {
                "target": None,
                "direction": [1, 0, 0]  # Начальное направление вправо
            }
            
        try:
            while True:
                # Получаем состояние игры
                game_state = self.api.get_game_state(self.round_info)
                if not game_state:
                    print("Не удалось получить состояние игры")
                    break
                    
                # Обновляем и выводим статистику
                for snake in game_state.get('snakes', []):
                    self.update_snake_stats(snake)
                self.print_stats(game_state)
                
                # Готовим ходы для всех змеек
                moves = []
                
                for snake_id in self.snake_ids:
                    # Ищем нашу змейку
                    snake = next((s for s in game_state['snakes'] if s['id'] == snake_id), None)
                    if not snake or snake['status'] != 'alive':
                        continue
                        
                    # Получаем позицию головы змейки
                    head_pos = snake['geometry'][0]
                    
                    # Проверяем, нужно ли искать новую цель
                    current_target = self.snake_targets[snake_id]["target"]
                    current_direction = self.snake_targets[snake_id]["direction"]
                    need_new_target = True
                    
                    if current_target:
                        # Проверяем, существует ли еще текущая цель
                        target_exists = any(
                            food.get('position', food.get('c', [0, 0, 0])) == current_target
                            for food in game_state.get('food', [])
                        )
                        if target_exists:
                            need_new_target = False
                            
                    # Получаем список других змей для избегания столкновений
                    other_snakes = [s['geometry'] for s in game_state['snakes'] 
                                  if s['id'] != snake_id and s['status'] == 'alive']
                                  
                    # Проверяем безопасность текущего направления
                    safe_direction = pathfinder.get_safe_direction(head_pos, current_direction)
                    
                    # Если текущее направление опасно, сразу меняем его
                    if [round(x, 6) for x in safe_direction] != [round(x, 6) for x in current_direction]:
                        print(f"Обнаружена опасность! Меняем направление для змейки {snake_id}")
                        print(f"Старое направление: {current_direction}")
                        print(f"Новое направление: {safe_direction}")
                        self.snake_targets[snake_id]["direction"] = safe_direction
                        need_new_target = True
                            
                    if need_new_target:
                        print(f"\nИщем новую цель для змейки {snake_id}")
                        
                        # Ищем лучший путь к еде
                        best_path, target_food = pathfinder.find_best_path_to_food(
                            head_pos,
                            game_state.get('food', []),
                            other_snakes
                        )
                        
                        if best_path and len(best_path) > 1:
                            # Обновляем цель и направление
                            next_point = best_path[1]
                            direction = [
                                next_point[0] - head_pos[0],
                                next_point[1] - head_pos[1],
                                next_point[2] - head_pos[2]
                            ]
                            
                            # Нормализуем вектор направления
                            direction = pathfinder.normalize_direction(direction)
                            
                            target_pos = target_food.get('position', target_food.get('c', [0, 0, 0]))
                            self.snake_targets[snake_id] = {
                                "target": target_pos,
                                "direction": direction
                            }
                            print(f"Новая цель: {target_pos}, направление: {direction}")
                        else:
                            print(f"Не удалось найти путь, используем безопасное направление")
                            self.snake_targets[snake_id]["direction"] = safe_direction
                            self.snake_targets[snake_id]["target"] = None
                    
                    # Проверяем и корректируем направление перед отправкой
                    direction = self.snake_targets[snake_id]["direction"]
                    
                    # Убеждаемся, что направление нормализовано
                    length = sum(d*d for d in direction) ** 0.5
                    if abs(length - 1.0) > 0.0001:  # Проверяем с погрешностью
                        print(f"Внимание: направление не нормализовано! Длина = {length}")
                        if length > 0:
                            direction = [d/length for d in direction]
                        else:
                            direction = [1, 0, 0]  # Безопасное направление по умолчанию
                            
                    # Округляем компоненты до 6 знаков после запятой для стабильности
                    direction = [round(d, 6) for d in direction]
                    
                    # Проверяем каждую компоненту на допустимые значения
                    if any(abs(d) > 1.0 for d in direction):
                        print(f"Внимание: недопустимые значения в направлении: {direction}")
                        # Нормализуем еще раз
                        length = sum(d*d for d in direction) ** 0.5
                        direction = [d/length for d in direction]
                        direction = [round(d, 6) for d in direction]
                    
                    print(f"Финальное направление для змейки {snake_id}: {direction}")
                    
                    # Преобразуем список в словарь с координатами
                    direction_dict = {
                        "x": direction[0],
                        "y": direction[1],
                        "z": direction[2]
                    }
                    
                    # Сохраняем исправленное направление
                    self.snake_targets[snake_id]["direction"] = direction
                    
                    # Добавляем ход с направлением в формате словаря
                    moves.append({
                        "id": snake_id,
                        "direction": direction_dict
                    })
                
                # Обновляем визуализацию
                if not visualizer.process_events(game_state):
                    break
                visualizer.render(game_state)
                
                # Отправляем ходы
                if moves and not self.api.make_move(self.round_info, moves):
                    print("Не удалось сделать ход")
                    break
                    
                time.sleep(1)  # Пауза между ходами
                
        except KeyboardInterrupt:
            print("\nИгра остановлена пользователем")
            return True
            
        return True