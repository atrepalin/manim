from manimlib import *  # Импорт библиотеки Manim для создания анимаций
import numpy as np  # Импорт библиотеки NumPy для работы с векторами и массивами


# Функция для вычисления позиций вершин по кругу
def compute_positions(n, labels, radius=3):
    angle_step = TAU / n  # Угол между соседними вершинами на окружности
    return {
        labels[i]: radius
        * np.array(
            [np.cos(i * angle_step), np.sin(i * angle_step), 0]
        )  # Позиция вершины в 3D-пространстве (X, Y, Z)
        for i in range(n)
    }


# Функция для создания объектов-вершин и подписей к ним
def create_vertices(labels, pos):
    # Создание точек (вершин) на основе вычисленных позиций
    verts = {
        name: Dot(pos[name], color=BLUE).scale(1.2) for name in labels
    }  # Синие точки для вершин
    # Подписи для каждой вершины
    lbls = {name: Tex(name).next_to(pos[name] * 1.15, ORIGIN) for name in labels}
    return verts, lbls


# === Основной класс сцены с анимацией алгоритма Форда-Фалкерсона ===
class FordFulkersonFromAdjacency(Scene):
    def __init__(self, adjacency_matrix, **kwargs):
        super().__init__(**kwargs)

        self.adjacency_matrix = adjacency_matrix

        self.n = len(adjacency_matrix)  # Количество вершин в графе
        self.labels = [f"X_{{{i+1}}}" for i in range(self.n)]

    def construct(self):
        pos = compute_positions(self.n, self.labels)  # Позиции вершин
        verts, v_labels = create_vertices(self.labels, pos)  # Вершины и подписи
        self.add(*verts.values(), *v_labels.values())  # Отображение на сцене

        edges = []  # Список рёбер
        capacity = {}  # Словарь: (u, v) -> пропускная способность

        # Обработка матрицы смежности для создания рёбер
        for i in range(self.n):
            for j in range(self.n):
                w = self.adjacency_matrix[i][j]
                if w > 0:
                    u, v = self.labels[i], self.labels[j]
                    line = Arrow(pos[u], pos[v], buff=0.15, fill_color=GREY)
                    label = (
                        Tex(f"0/{w}")
                        .scale(0.7)
                        .move_to((pos[u] + pos[v]) / 2 + 0.3 * UP)
                    )
                    edges.append((line, (u, v), label))
                    capacity[(u, v)] = w  # Сохраняем пропускную способность

        # Отображение всех рёбер
        for line, (_, _), label in edges:
            self.play(ShowCreation(line), Write(label), run_time=0.2)
        self.wait(1)

        # Источник и сток
        source, sink = self.labels[0], self.labels[-1]

        flow = {key: 0 for key in capacity}  # Начальный поток на всех рёбрах — 0
        max_flow = 0  # Общий поток через сеть

        # Трекер для отображения текущего значения потока
        max_flow_tracker = ValueTracker(0)
        max_flow_label = always_redraw(
            lambda: Tex(
                f"\\text{{Максимальный поток: }} {int(max_flow_tracker.get_value())}"
            ).to_corner(UL)
        )
        self.add(max_flow_label)

        # === Поиск пути с помощью BFS (по остаточной сети) ===
        def bfs():
            parent = {}  # Для восстановления пути
            visited = {source}
            queue = [source]
            while queue:
                u = queue.pop(0)
                for v in self.labels:
                    # Условие: есть положительная остаточная ёмкость
                    if (
                        (u, v) in capacity
                        and v not in visited
                        and capacity[(u, v)] - flow[(u, v)] > 0
                    ):
                        visited.add(v)
                        parent[v] = u
                        queue.append(v)
            return parent if sink in parent else None

        # === Основной цикл алгоритма Форда-Фалкерсона ===
        while True:
            parent = bfs()
            if not parent:  # Если путь не найден — выходим
                break

            # Вычисление минимального остатка на найденном пути
            path_flow = float("inf")
            s = sink
            while s != source:
                u = parent[s]
                path_flow = min(path_flow, capacity[(u, s)] - flow[(u, s)])
                s = u

            # Обновление потоков вдоль пути
            s = sink
            while s != source:
                u = parent[s]
                flow[(u, s)] += path_flow
                # Обратный поток (для остаточной сети)
                flow[(s, u)] = flow.get((s, u), 0) - path_flow
                s = u

            # Обновляем общее значение потока
            max_flow += path_flow
            self.play(max_flow_tracker.animate.set_value(max_flow), run_time=0.4)

            # Обновление подписей и цвета рёбер
            for i in range(len(edges)):
                line, (u, v), label = edges[i]
                if (u, v) in flow:
                    current_flow = flow[(u, v)]
                    cap = capacity[(u, v)]
                    new_text = (
                        Tex(f"{current_flow}/{cap}")
                        .scale(0.7)
                        .move_to(label.get_center())
                    )

                    # Цвет по степени заполненности
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
                    edges[i] = (line, (u, v), new_text)

        self.wait(1)

        # === Построение минимального разреза ===
        # Повторный BFS для определения достижимых вершин из источника
        visited = set()
        queue = [source]
        while queue:
            u = queue.pop(0)
            visited.add(u)
            for v in self.labels:
                if (
                    (u, v) in capacity
                    and v not in visited
                    and capacity[(u, v)] - flow[(u, v)] > 0
                ):
                    queue.append(v)

        # Вершины по разные стороны разреза выделяются цветом
        for v in visited:
            verts[v].set_fill(BLUE, opacity=0.5)
        for v in self.labels:
            if v not in visited:
                verts[v].set_fill(ORANGE, opacity=0.5)

        # Рёбра, пересекающие разрез, выделяются красным
        for line, (u, v), _ in edges:
            if u in visited and v not in visited:
                self.play(line.animate.set_color(RED), run_time=0.2)

        self.wait(3)
