import numpy as np
from typing import List, Tuple, Dict, Set
import heapq

class PathFinder:
    def __init__(self, grid_size=200, cell_size=1, sector_size=30):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.sector_size = sector_size
        self.obstacles: Set[Tuple[int, int, int]] = set()
        self.map_bounds = (-self.grid_size//2, self.grid_size//2)
        
    def clear_obstacles(self):
        self.obstacles.clear()
        
    def add_obstacle(self, pos: List[float]):
        """Добавляет препятствие в сетку"""
        x, y, z = [int(p / self.cell_size) for p in pos]
        self.obstacles.add((x, y, z))
        
    def add_snake_as_obstacles(self, geometry: List[List[float]], exclude_head=True):
        """Добавляет змейку как препятствие, исключая голову если нужно"""
        start = 1 if exclude_head else 0
        for pos in geometry[start:]:
            self.add_obstacle(pos)
            
    def is_position_safe(self, pos: List[float]) -> bool:
        """Проверяет безопасность позиции"""
        x, y, z = [int(p / self.cell_size) for p in pos]
        
        # Проверка границ карты (с отступом для безопасности)
        safety_margin = 2
        min_bound = self.map_bounds[0] + safety_margin
        max_bound = self.map_bounds[1] - safety_margin
        
        if not (min_bound <= x <= max_bound and 
                min_bound <= y <= max_bound and 
                min_bound <= z <= max_bound):
            return False
            
        # Проверка препятствий (с запасом)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    check_pos = (x + dx, y + dy, z + dz)
                    if check_pos in self.obstacles:
                        return False
                        
        return True
        
    def get_sector(self, pos: List[float]) -> Tuple[int, int, int]:
        """Получает координаты сектора для позиции"""
        return tuple(int(p // self.sector_size) for p in pos)
        
    def is_visible(self, from_pos: List[float], to_pos: List[float]) -> bool:
        """Проверяет видимость точки из текущей позиции"""
        from_sector = self.get_sector(from_pos)
        to_sector = self.get_sector(to_pos)
        
        # Проверяем, находится ли целевая точка в видимом секторе (включая диагональные)
        return all(abs(to_sector[i] - from_sector[i]) <= 1 for i in range(3))
        
    def get_visible_area(self, pos: List[float]) -> List[Tuple[int, int, int]]:
        """Получает список секторов в области видимости"""
        current_sector = self.get_sector(pos)
        visible_sectors = []
        
        # Собираем все прилегающие сектора (включая диагональные)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    sector = (
                        current_sector[0] + dx,
                        current_sector[1] + dy,
                        current_sector[2] + dz
                    )
                    visible_sectors.append(sector)
                    
        return visible_sectors
        
    def normalize_direction(self, direction: List[float]) -> List[float]:
        """Нормализует вектор направления"""
        # Проверяем на нулевой вектор
        if all(d == 0 for d in direction):
            return [1, 0, 0]  # Безопасное направление по умолчанию
            
        # Вычисляем длину вектора
        length = sum(d*d for d in direction) ** 0.5
        
        # Нормализуем и округляем до 6 знаков после запятой
        if length > 0:
            normalized = [round(d/length, 6) for d in direction]
            
            # Проверяем на допустимые значения
            if any(abs(d) > 1.0 for d in normalized):
                print(f"Внимание: недопустимые значения после нормализации: {normalized}")
                # Повторная нормализация
                length = sum(d*d for d in normalized) ** 0.5
                normalized = [round(d/length, 6) for d in normalized]
            
            return normalized
            
        return [1, 0, 0]  # Безопасное направление по умолчанию
        
    def get_safe_direction(self, current_pos: List[float], current_dir: List[float]) -> List[float]:
        """Находит безопасное направление движения"""
        # Нормализуем текущее направление
        current_dir = self.normalize_direction(current_dir)
            
        # Проверяем текущее направление
        next_pos = [current_pos[i] + current_dir[i] * 2 for i in range(3)]
        if self.is_position_safe(next_pos):
            return current_dir
            
        # Пробуем альтернативные направления
        base_directions = [
            [1, 0, 0], [-1, 0, 0],
            [0, 1, 0], [0, -1, 0],
            [0, 0, 1], [0, 0, -1]
        ]
        
        # Сортируем направления по близости к текущему
        base_directions.sort(key=lambda d: sum((d[i] - current_dir[i])**2 for i in range(3)))
        
        for direction in base_directions:
            next_pos = [current_pos[i] + direction[i] * 2 for i in range(3)]
            if self.is_position_safe(next_pos):
                return self.normalize_direction(direction)
                
        # Если все направления опасны, пытаемся уйти от препятствий
        escape_dir = [0, 0, 0]
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    pos = (int(current_pos[0]/self.cell_size) + dx,
                          int(current_pos[1]/self.cell_size) + dy,
                          int(current_pos[2]/self.cell_size) + dz)
                    if pos in self.obstacles:
                        escape_dir[0] -= dx
                        escape_dir[1] -= dy
                        escape_dir[2] -= dz
                        
        normalized_escape = self.normalize_direction(escape_dir)
        print(f"Направление ухода от препятствий: {normalized_escape}")
        return normalized_escape
        
    def get_neighbors(self, pos: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Получает соседние точки, исключая препятствия"""
        x, y, z = pos
        neighbors = []
        
        # 6 основных направлений движения
        for dx, dy, dz in [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]:
            new_pos = (x + dx, y + dy, z + dz)
            
            # Проверяем границы и препятствия
            if (self.map_bounds[0] <= new_pos[0] <= self.map_bounds[1] and 
                self.map_bounds[1] <= new_pos[1] <= self.map_bounds[1] and 
                self.map_bounds[2] <= new_pos[2] <= self.map_bounds[1] and 
                new_pos not in self.obstacles):
                neighbors.append(new_pos)
                
        return neighbors
        
    def heuristic(self, a: Tuple[int, int, int], b: Tuple[int, int, int]) -> float:
        """Манхэттенское расстояние в 3D"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
        
    def find_path(self, start: List[float], goal: List[float]) -> List[List[float]]:
        """Находит путь от start до goal, используя A*"""
        # Конвертируем координаты в индексы сетки
        start_grid = tuple(int(p / self.cell_size) for p in start)
        goal_grid = tuple(int(p / self.cell_size) for p in goal)
        
        # Если цель или старт в препятствии, возвращаем None
        if start_grid in self.obstacles or goal_grid in self.obstacles:
            print(f"Путь невозможен: {'старт' if start_grid in self.obstacles else 'цель'} в препятствии")
            return None
            
        print(f"Ищем путь от {start_grid} до {goal_grid}")
        
        frontier = []
        heapq.heappush(frontier, (0, start_grid))
        came_from = {start_grid: None}
        cost_so_far = {start_grid: 0}
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == goal_grid:
                break
                
            for next_pos in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(next_pos, goal_grid)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
                    
        # Восстанавливаем путь
        if goal_grid not in came_from:
            print(f"Путь не найден от {start_grid} до {goal_grid}")
            return None
            
        path = []
        current = goal_grid
        while current is not None:
            # Конвертируем обратно в мировые координаты
            world_pos = [p * self.cell_size for p in current]
            # Проверяем безопасность каждой точки пути
            if not self.is_position_safe(world_pos):
                print(f"Точка пути {world_pos} небезопасна, ищем другой путь")
                return None
            path.append(world_pos)
            current = came_from[current]
            
        path.reverse()
        print(f"Найден безопасный путь длиной {len(path)} шагов")
        return path
        
    def find_best_path_to_food(self, snake_pos: List[float], foods: List[Dict], 
                              other_snakes: List[List[List[float]]] = None) -> Tuple[List[List[float]], Dict]:
        """Находит лучший путь к еде, учитывая препятствия от других змей"""
        self.clear_obstacles()
        
        # Добавляем другие змейки как препятствия
        if other_snakes:
            for snake in other_snakes:
                self.add_snake_as_obstacles(snake)
                
        best_path = None
        best_food = None
        best_score = float('inf')
        
        print(f"\nИщем путь для змейки на позиции {snake_pos}")
        visible_food = []
        
        # Фильтруем еду по видимости
        for food in foods:
            food_pos = food.get('position', food.get('c', [0, 0, 0]))
            if self.is_visible(snake_pos, food_pos):
                visible_food.append(food)
                
        print(f"Доступно еды в области видимости: {len(visible_food)}")
        
        for food in visible_food:
            food_pos = food.get('position', food.get('c', [0, 0, 0]))
            is_golden = food.get('golden', False)
            print(f"\nПробуем {'золотую' if is_golden else 'обычную'} еду на позиции {food_pos}")
            
            path = self.find_path(snake_pos, food_pos)
            
            if path:
                # Оцениваем путь (длина пути и стоимость еды)
                path_length = len(path)
                food_value = 5 if is_golden else 1
                score = path_length / food_value
                
                print(f"Длина пути: {path_length}, ценность: {food_value}, счет: {score}")
                
                if score < best_score:
                    best_score = score
                    best_path = path
                    best_food = food
                    print("Это лучший путь на данный момент!")
                    
        if best_path:
            print(f"\nВыбран {'золотой' if best_food.get('golden', False) else 'обычный'} путь длиной {len(best_path)}")
        else:
            print("\nНе удалось найти безопасный путь к еде!")
            
        return best_path, best_food
