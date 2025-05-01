from manimlib import *
from .methods import compute_positions, create_vertices, create_edges
from .scene import InteractiveScene


def remove_back_edges(adjacency_list):
    visited = set()
    on_stack = set()
    cycle_edges = []

    def dfs(v):
        visited.add(v)
        on_stack.add(v)
        for u, _ in adjacency_list[v]:
            if u not in visited:
                dfs(u)
            elif u in on_stack:
                # Обратное ребро (v → u), цикл найден
                cycle_edges.append((v, u))
        on_stack.remove(v)

    for v in adjacency_list:
        if v not in visited:
            dfs(v)

    return cycle_edges  # Список всех обратных рёбер


class DPShortestPathFromAdjacency(InteractiveScene):
    def __init__(self, adjacency_matrix, **kwargs):
        super().__init__(**kwargs)
        self.adjacency_matrix = adjacency_matrix
        self.n = len(adjacency_matrix)
        self.labels = [f"X_{{{i+1}}}" for i in range(self.n)]

    def construct(self):
        pos = compute_positions(self.n, self.labels, radius=2.5)
        verts, v_labels = create_vertices(self.labels, pos)
        self.add(*verts.values(), *v_labels.values())

        edges = create_edges(self.n, self.labels, self.adjacency_matrix, pos)
        adjacency_list = {v: [] for v in self.labels}

        for w, line, (a, b), label in edges:
            adjacency_list[a].append((b, w))
            self.play(ShowCreation(line), Write(label), run_time=0.2)

        self.wait(1)

        cycle_edges = remove_back_edges(adjacency_list)

        for u, v in cycle_edges:
            # Удалить из логики
            adjacency_list[u] = [(w, wgt) for w, wgt in adjacency_list[u] if w != v]

            # Найти визуальное ребро и удалить с анимацией
            for i, (w, line, (a, b), label) in enumerate(edges):
                if a == u and b == v:
                    self.play(line.animate.set_color(RED), label.animate.set_color(RED))
                    self.play(FadeOut(line), FadeOut(label))
                    edges.pop(i)
                    break

        # === Топологическая сортировка с наглядной анимацией ===
        visited = set()
        stack = []

        # Создаём визуальное представление стека
        stack_title = Tex(r"\text{Стек}").scale(0.8).to_edge(UR)
        stack_box = VGroup().arrange(DOWN, aligned_edge=LEFT).next_to(stack_title, DOWN)
        self.add(stack_title, stack_box)

        info_box = Tex("").to_corner(UL)
        self.add(info_box)

        def dfs(v):
            self.play(
                Transform(
                    info_box, Tex(f"\\text{{Посещаем: }} {v}").scale(0.8).to_corner(UL)
                ),
                verts[v].animate.set_fill(YELLOW, opacity=0.6),
                run_time=0.5,
            )
            visited.add(v)
            for neighbor, _ in adjacency_list[v]:
                if neighbor not in visited:
                    dfs(neighbor)
            stack.append(v)
            # Добавляем вершину в стек (визуально)
            stack_entry = Tex(v).scale(0.6).set_fill(GREEN).next_to(stack_box, DOWN)
            stack_box.add(stack_entry)
            self.play(
                Transform(
                    info_box,
                    Tex(f"\\text{{Добавляем в стек: }} {v}").scale(0.8).to_corner(UL),
                ),
                FadeIn(stack_entry),
                verts[v].animate.set_fill(GREEN, opacity=0.7),
                run_time=0.5,
            )

            self.pause()

        for v in self.labels:
            if v not in visited:
                dfs(v)

        self.wait(1)

        # Убираем инфо-бокс
        self.play(FadeOut(info_box), run_time=0.5)

        # === Выталкивание из стека и выстраивание в линию ===
        topo_order = stack[::-1]  # топологический порядок

        # Порядок с текстом сверху
        order_title = Tex(r"\text{Топологический порядок}").scale(0.8).to_corner(UP)
        self.play(FadeIn(order_title), run_time=0.5)

        # Создаём горизонтальную линию позиций
        spacing = 1.5
        topo_positions = {
            v: LEFT * ((len(topo_order) / 2 - 0.5) * spacing)
            + RIGHT * i * spacing
            + DOWN * 2
            for i, v in enumerate(topo_order)
        }

        # Анимируем выталкивание из стека и перестановку
        animations = []
        for i, v in enumerate(topo_order):
            index = topo_order.index(self.labels[i])
            stack_entry = stack_box[len(stack_box) - index - 1]

            animations.append(
                stack_entry.animate.move_to(topo_positions[v] + DOWN * 0.5)
            )
            animations.append(verts[v].animate.move_to(topo_positions[v] + DOWN))
            animations.append(
                v_labels[v].animate.move_to(topo_positions[v] + DOWN * 1.5)
            )
        self.play(*animations, run_time=2)

        self.pause()

        # Убираем стек
        self.play(
            FadeOut(stack_box), FadeOut(stack_title), FadeOut(order_title), run_time=0.5
        )

        self.wait(1)

        # Пересчитать позиции
        new_pos = compute_positions(len(topo_order), topo_order, radius=2.5)

        # Анимированное перемещение вершин
        self.play(
            *[
                verts[v].animate.move_to(new_pos[v]).set_color(BLUE)
                for v in self.labels
            ],
            *[v_labels[v].animate.move_to(new_pos[v] * 1.15) for v in v_labels.keys()],
        )

        # Удалить старые рёбра и перерисовать
        for _, line, _, label in edges:
            self.remove(line, label)

        edges = create_edges(self.n, self.labels, self.adjacency_matrix, new_pos, True)

        for u, v in cycle_edges:
            for i, (w, line, (a, b), label) in enumerate(edges):
                if a == u and b == v:
                    edges.pop(i)
                    break

        for w, line, _, label in edges:
            self.play(ShowCreation(line), Write(label), run_time=0.2)

        self.wait(1)
        self.pause()

        # === Расчет кратчайших путей через ДП ===
        start = self.labels[0]
        dist = {v: float("inf") for v in self.labels}
        dist[start] = 0

        distance_labels = {}
        for v in self.labels:
            text = r"\infty" if dist[v] == float("inf") else str(int(dist[v]))
            label = Tex(text).scale(0.7).next_to(new_pos[v] * 1.45, ORIGIN)
            distance_labels[v] = label
        self.add(*distance_labels.values())

        info_box = Tex("").to_corner(UL)
        self.add(info_box)

        while stack:
            u = stack.pop()
            self.play(
                Transform(
                    info_box,
                    Tex(f"\\text{{Обрабатываем: }} {u}").scale(0.8).to_corner(UL),
                ),
                verts[u].animate.set_fill(YELLOW, opacity=0.6),
                run_time=0.5,
            )

            if dist[u] != float("inf"):
                for v, w in adjacency_list[u]:
                    edge = next(e for e in edges if e[2] == (u, v))
                    line = edge[1]
                    self.play(line.animate.set_color(GREEN), run_time=0.3)

                    if dist[v] > dist[u] + w:
                        old_val = (
                            r"\infty" if dist[v] == float("inf") else str(int(dist[v]))
                        )
                        dist[v] = dist[u] + w

                        update_text = Tex(
                            f"{v}: {old_val} \\rightarrow {dist[v]}"
                        ).to_corner(UR)
                        self.play(Write(update_text), run_time=0.5)

                        self.play(FadeOut(distance_labels[v]), run_time=0.2)
                        new_label = (
                            Tex(str(int(dist[v])))
                            .scale(0.7)
                            .next_to(new_pos[v] * 1.45, ORIGIN)
                        )
                        distance_labels[v] = new_label
                        self.add(new_label)

                        self.play(FadeOut(update_text), run_time=0.2)
                    self.play(line.animate.set_color(GREY), run_time=0.2)

            self.wait(0.5)
            self.pause()

        self.play(
            FadeOut(info_box),
            *[label.animate.set_color(GREEN) for label in distance_labels.values()],
        )
        self.wait(3)
