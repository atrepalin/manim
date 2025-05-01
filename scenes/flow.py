from manimlib import *  # Импорт библиотеки Manim
from .methods import compute_positions, create_vertices, create_edges
from .scene import InteractiveScene


class FordFulkersonFromAdjacency(InteractiveScene):
    def __init__(self, adjacency_matrix, **kwargs):
        super().__init__(**kwargs)
        self.adjacency_matrix = adjacency_matrix
        self.n = len(adjacency_matrix)  # Количество вершин
        self.labels = [f"X_{{{i+1}}}" for i in range(self.n)]  # Метки для вершин

    def construct(self):
        # Вычисление позиций вершин и их отображение
        pos = compute_positions(self.n, self.labels)
        verts, v_labels = create_vertices(self.labels, pos)
        self.add(*verts.values(), *v_labels.values())  # Отображаем вершины

        # Создание рёбер на основе матрицы смежности
        edges = create_edges(self.n, self.labels, self.adjacency_matrix, pos)
        capacity = {}  # Словарь для хранения пропускных способностей рёбер
        original_edges = set()  # Множество для рёбер оригинального графа

        # Заполнение пропускных способностей рёбер и сохранение их
        for i in range(self.n):
            for j in range(self.n):
                w = self.adjacency_matrix[i][j]
                if w > 0:
                    u, v = self.labels[i], self.labels[j]
                    capacity[(u, v)] = w
                    original_edges.add((u, v))  # Добавляем ребра в оригинальные рёбра

        # Отображение всех рёбер на сцене
        for w, line, (_, _), label in edges:
            self.play(ShowCreation(line), Write(label), run_time=0.2)
        self.wait(1)

        source, sink = self.labels[0], self.labels[-1]  # Источник и сток
        flow = {}  # Словарь для потоков по рёбрам

        # Инициализация потоков на рёбрах как 0
        for u, v in capacity:
            flow[(u, v)] = 0
            if (v, u) not in flow:
                flow[(v, u)] = 0  # Добавляем обратный поток для рёбер

        max_flow = 0  # Общий максимальный поток
        max_flow_tracker = ValueTracker(
            0
        )  # Трекер для отслеживания максимального потока
        max_flow_label = always_redraw(
            lambda: Tex(
                f"\\text{{Максимальный поток: }} {int(max_flow_tracker.get_value())}"
            ).to_corner(
                UL
            )  # Отображение максимального потока
        )
        self.add(max_flow_label)

        # Функция для поиска пути с помощью BFS
        def bfs():
            parent = {}  # Словарь для восстановления пути
            visited = {source}  # Множество посещённых вершин
            queue = [source]  # Очередь для BFS
            while queue:
                u = queue.pop(0)  # Извлекаем вершину из очереди
                for v in self.labels:
                    # Если остаточная ёмкость рёбра положительная
                    residual = capacity.get((u, v), 0) - flow.get((u, v), 0)
                    if residual > 0 and v not in visited:
                        visited.add(v)
                        parent[v] = u
                        queue.append(v)
            return (
                parent if sink in parent else None
            )  # Возвращаем путь, если он существует

        # Основной цикл алгоритма Форда-Фалкерсона
        while True:
            parent = bfs()  # Находим путь в остаточной сети
            if not parent:  # Если путь не найден — выходим
                break

            # Вычисление минимального остатка на найденном пути
            path_flow = float("inf")
            s = sink
            while s != source:
                u = parent[s]
                residual = capacity.get((u, s), 0) - flow.get((u, s), 0)
                path_flow = min(path_flow, residual)
                s = u

            # Обновление потока вдоль пути
            s = sink
            while s != source:
                u = parent[s]
                flow[(u, s)] += path_flow
                if (s, u) not in flow:
                    flow[(s, u)] = 0
                flow[(s, u)] -= path_flow  # Обновляем обратный поток
                if (s, u) not in capacity:
                    capacity[(s, u)] = 0  # Для корректного расчёта остаточной ёмкости
                s = u

            # Обновляем общий поток
            max_flow += path_flow
            self.play(max_flow_tracker.animate.set_value(max_flow), run_time=0.4)

            # Обновление подписей рёбер с учётом потока
            for i in range(len(edges)):
                _, line, (u, v), label = edges[i]
                if (u, v) in original_edges:
                    current_flow = max(flow[(u, v)], 0)
                    cap = capacity[(u, v)]
                    new_text = (
                        Tex(f"{current_flow}/{cap}")
                        .scale(0.7)
                        .move_to(label.get_center())  # Новый текст с текущим потоком
                    )

                    # Цвет рёбер в зависимости от текущего потока
                    if current_flow == cap:
                        color = RED
                    elif current_flow > 0:
                        color = YELLOW
                    else:
                        color = GREY

                    self.play(FadeOut(label), run_time=0.1)
                    self.play(
                        Write(new_text), line.animate.set_color(color), run_time=0.2
                    )
                    edges[i] = (0, line, (u, v), new_text)

            self.pause()

        self.wait(1)

        # Построение минимального разреза
        visited = set()  # Множество для посещённых вершин
        queue = [source]  # Очередь для BFS
        while queue:
            u = queue.pop(0)
            visited.add(u)
            for v in self.labels:
                residual = capacity.get((u, v), 0) - flow.get((u, v), 0)
                if residual > 0 and v not in visited:
                    queue.append(v)

        # Выделение вершин с двух сторон разреза
        for v in visited:
            verts[v].set_fill(BLUE, opacity=0.5)
        for v in self.labels:
            if v not in visited:
                verts[v].set_fill(ORANGE, opacity=0.5)

        # Выделение рёбер, пересекающих разрез
        for _, line, (u, v), _ in edges:
            if u in visited and v not in visited:
                self.play(line.animate.set_color(RED), run_time=0.2)

        self.wait(3)
