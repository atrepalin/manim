from manimlib import *  # Импорт библиотеки Manim для создания анимаций
from .methods import compute_positions, create_vertices, create_arcs


# Класс для анимации алгоритма Краскала
class KruskalFromAdjacency(Scene):
    def __init__(self, adjacency_matrix, **kwargs):
        super().__init__(**kwargs)

        self.adjacency_matrix = adjacency_matrix

        self.n = len(adjacency_matrix)  # Количество вершин в графе
        self.labels = [f"X_{{{i+1}}}" for i in range(self.n)]

    def construct(self):
        pos = compute_positions(self.n, self.labels)  # Вычисляем позиции вершин
        verts, v_labels = create_vertices(self.labels, pos)  # Создаём вершины и подписи
        self.add(
            *verts.values(), *v_labels.values()
        )  # Добавляем вершины и подписи на сцену

        edges = create_arcs(
            self.n, self.labels, self.adjacency_matrix, pos
        )  # Создаём рёбра
        # Показ всех рёбер и весов
        for w, line, (_, _), weight_label in edges:
            self.play(
                ShowCreation(line), Write(weight_label), run_time=0.2
            )  # Показываем рёбра и их веса
        self.wait(1)

        # Подготовка для алгоритма union-find
        edges.sort(
            key=lambda x: x[0]
        )  # Сортируем рёбра по весу (от минимального к максимальному)
        parent = {v: v for v in self.labels}  # Множество для хранения родителей вершин

        # Функция поиска родителя вершины
        def find(v):
            while parent[v] != v:
                parent[v] = parent[parent[v]]  # Сжатие пути
                v = parent[v]
            return v

        # Функция объединения двух компонент
        def union(u, v):
            parent[find(u)] = find(v)

        weight_tracker = ValueTracker(0)  # Трекер веса

        def get_label():
            return Tex(f"\\text{{Вес: }} {int(weight_tracker.get_value())}").to_corner(
                UP + LEFT
            )  # Обновляем метку веса

        weight_label = always_redraw(get_label)
        self.add(weight_label)

        # Основной цикл алгоритма Краскала
        for w, line, (u, v), _ in edges:
            ru, rv = find(u), find(
                v
            )  # Находим компоненты, к которым принадлежат вершины u и v
            find_u = Tex(f"find({u})={ru}").to_corner(UR)  # Подсказка для анимации find
            find_v = Tex(f"find({v})={rv}").next_to(
                find_u, DOWN
            )  # Подсказка для анимации find
            self.play(
                Write(find_u), Write(find_v), run_time=0.5
            )  # Показываем find для u и v
            self.play(FadeOut(find_u), FadeOut(find_v))  # Убираем подсказки

            if ru != rv:  # Если вершины принадлежат разным компонентам
                union_txt = Tex(f"union({u},{v})").to_corner(
                    UR
                )  # Подсказка для анимации union
                self.play(Write(union_txt), run_time=0.5)  # Показываем union
                self.play(FadeOut(union_txt))  # Убираем подсказку
                union(u, v)  # Объединяем компоненты
                self.play(
                    line.animate.set_color(GREEN),
                    weight_tracker.animate.set_value(weight_tracker.get_value() + w),
                    run_time=0.5,
                )
            else:  # Если вершины уже в одной компоненте
                self.play(
                    line.animate.set_color(RED), run_time=0.3
                )  # Окрашиваем ребро в красный (не включаем в остов)

        final = get_label()

        self.play(FadeTransform(weight_label, final), final.animate.set_color(GREEN))
        self.wait(2)


# Класс для анимации алгоритма Прима
class PrimFromAdjacency(Scene):
    def __init__(self, adjacency_matrix, **kwargs):
        super().__init__(**kwargs)

        self.adjacency_matrix = adjacency_matrix

        self.n = len(adjacency_matrix)  # Количество вершин в графе
        self.labels = [f"X_{{{i+1}}}" for i in range(self.n)]

    def construct(self):
        pos = compute_positions(self.n, self.labels)  # Вычисляем позиции вершин
        verts, v_labels = create_vertices(self.labels, pos)  # Создаём вершины и подписи
        self.add(
            *verts.values(), *v_labels.values()
        )  # Добавляем вершины и подписи на сцену

        edges = create_arcs(
            self.n, self.labels, self.adjacency_matrix, pos
        )  # Создаём рёбра
        # Показ всех рёбер и весов
        for w, line, (_, _), weight_label in edges:
            self.play(
                ShowCreation(line), Write(weight_label), run_time=0.2
            )  # Показываем рёбра и их веса
        self.wait(1)

        # Инициализация алгоритма Прима
        start = self.labels[0]  # Начинаем с вершины A
        visited = {start}  # Множество посещённых вершин
        verts[start].set_fill(YELLOW, opacity=0.5)  # Окрасим вершину в жёлтый

        weight_tracker = ValueTracker(0)  # Трекер веса

        def get_label():
            return Tex(f"\\text{{Вес: }} {int(weight_tracker.get_value())}").to_corner(
                UP + LEFT
            )  # Обновляем метку веса

        weight_label = always_redraw(get_label)
        self.add(weight_label)

        # Формирование начального фронтира (рёбер, выходящих из вершины A)
        frontier = [e for e in edges if e[2][0] == start or e[2][1] == start]
        frontier.sort(key=lambda x: x[0])  # Сортируем рёбра по весу

        # Основной цикл алгоритма Прима
        while len(visited) < self.n:
            w, line, (u, v), _ = frontier.pop(
                0
            )  # Берём рёбра из фронтира (по наименьшему весу)
            new = v if u in visited else u  # Определяем новую вершину
            if new in visited:  # Если вершина уже посещена, пропускаем её
                continue
            sel = Tex(f"add({u},{v})").to_corner(
                UR
            )  # Подсказка для добавления ребра в остов
            self.play(Write(sel), run_time=0.5)  # Показываем подсказку
            self.play(FadeOut(sel))  # Убираем подсказку
            # Добавляем ребро в остов
            self.play(
                line.animate.set_color(GREEN),
                weight_tracker.animate.set_value(weight_tracker.get_value() + w),
                run_time=0.5,
            )
            # Обновляем посещённость и фронтир
            visited.add(new)
            verts[new].set_fill(YELLOW, opacity=0.5)
            for e in edges:
                w2, l2, (uu, vv), _ = e
                if (uu in visited) ^ (vv in visited) and e not in frontier:
                    frontier.append(
                        e
                    )  # Добавляем рёбра, которые соединяют посещённые и непосещённые вершины
            frontier.sort(key=lambda x: x[0])  # Сортируем фронтир по весу рёбер

        final = get_label()

        self.play(FadeTransform(weight_label, final), final.animate.set_color(GREEN))
        self.wait(2)
