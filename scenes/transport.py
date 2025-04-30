from manimlib import *
from collections import deque


class NorthwestCornerTransport(Scene):
    def __init__(self, matrix, **kwargs):
        super().__init__(**kwargs)

        matrix = np.array(matrix)

        self.supply = matrix[:, -1][:-1]
        self.demand = matrix[-1, 0:][:-1]

        cost_matrix = matrix[:-1, :-1]

        total_supply = sum(self.supply)
        total_demand = sum(self.demand)

        if total_supply > total_demand:
            self.demand = np.append(self.demand, total_supply - total_demand)

            extra = np.zeros((len(self.supply), 1), dtype=int)

            self.cost_matrix = np.hstack((cost_matrix, extra))

            self.has_extra_demand = True
            self.has_extra_supply = False
        elif total_supply < total_demand:
            self.supply = np.append(self.supply, total_demand - total_supply)

            extra = np.zeros((1, len(self.demand)), dtype=int)

            self.cost_matrix = np.vstack((cost_matrix, extra))

            self.has_extra_demand = False
            self.has_extra_supply = True
        else:
            self.cost_matrix = cost_matrix

            self.has_extra_demand = False
            self.has_extra_supply = False

    def show_total_cost(self, allocations, coords, cost_matrix, prev_label=None):
        total_cost = sum(
            int(label.tex_string) * cost_matrix[i][j]
            for (i, j), label in allocations.items()
        )
        cost_tex = (
            Tex(f"\\text{{Цена: }} {total_cost}").scale(0.7).to_corner(DOWN + RIGHT)
        )

        if prev_label:
            self.play(FadeOut(prev_label))
        self.play(Write(cost_tex))
        return cost_tex

    def construct(self):
        m, n = len(self.supply), len(self.demand)

        # === Сетка ===
        table = VGroup()
        labels = VGroup()
        cell_w, cell_h = 1.5, 1.2
        top_left = 3 * UP + 5 * LEFT
        coords = {}

        for i in range(m + 1):
            for j in range(n + 1):
                pos = top_left + j * cell_w * RIGHT + i * cell_h * DOWN
                rect = Rectangle(width=cell_w, height=cell_h, stroke_width=0.8).move_to(
                    pos
                )
                table.add(rect)
                coords[(i, j)] = pos

        self.play(FadeIn(table))
        self.wait(0.5)

        total = sum(self.demand)

        for i in range(m + 1):
            for j in range(n + 1):
                if i < m and j < n:
                    label = Tex(f"{self.cost_matrix[i][j]}").scale(0.7)
                elif i == m and j < n:
                    label = Tex(f"{self.demand[j]}")
                elif j == n and i < m:
                    label = Tex(f"{self.supply[i]}")
                else:
                    label = Tex(f"\\Sigma = {total}").scale(0.7)
                pos = top_left + j * cell_w * RIGHT + i * cell_h * DOWN
                label.move_to(pos)
                labels.add(label)
                coords[(i, j)] = pos

        self.play(Write(labels))
        self.wait(1)

        # === Северо-западный угол ===
        i, j = 0, 0
        allocations = {}
        curr_supply = self.supply.copy()
        curr_demand = self.demand.copy()

        while i < m and j < n:
            amount = min(curr_supply[i], curr_demand[j])
            pos = coords[(i, j)] + 0.4 * DOWN + 0.5 * RIGHT
            label = Tex(f"{amount}").set_color(GREEN).scale(0.7).move_to(pos)
            allocations[(i, j)] = label
            self.play(Write(label))
            self.wait(0.3)

            curr_supply[i] -= amount
            curr_demand[j] -= amount
            if curr_supply[i] == 0:
                i += 1
            elif curr_demand[j] == 0:
                j += 1

        self.wait(1)

        cost_label = self.show_total_cost(allocations, coords, self.cost_matrix)
        self.wait(1)

        while True:
            # === Потенциалы ===
            u, v = [None] * m, [None] * n
            u[0] = 0
            basis = list(allocations.keys())
            while any(x is None for x in u) or any(x is None for x in v):
                for i, j in basis:
                    if u[i] is not None and v[j] is None:
                        v[j] = self.cost_matrix[i][j] - u[i]
                    elif v[j] is not None and u[i] is None:
                        u[i] = self.cost_matrix[i][j] - v[j]

            # === Потенциалы строк и столбцов ===
            potentials = VGroup()

            for i in range(m):
                pos = top_left + n * cell_w * RIGHT + i * cell_h * DOWN

                text = Tex(f"{u[i]}").scale(0.5).move_to(pos + 0.4 * DOWN + 0.5 * RIGHT)
                text.set_color(BLUE)
                potentials.add(text)

            for j in range(n):
                pos = top_left + j * cell_w * RIGHT + m * cell_h * DOWN

                text = Tex(f"{v[j]}").scale(0.5).move_to(pos + 0.4 * DOWN + 0.5 * RIGHT)
                text.set_color(BLUE)
                potentials.add(text)

            self.play(Write(potentials))
            self.wait(1)

            # === Дельты ===
            delta_texts = VGroup()
            deltas = {}
            for i in range(m):
                for j in range(n):
                    if (i, j) not in allocations:
                        delta = self.cost_matrix[i][j] - u[i] - v[j]
                        deltas[(i, j)] = delta
                        text = (
                            Tex(f"\\phi={delta}")
                            .scale(0.5)
                            .move_to(coords[(i, j)] + 0.3 * UP + 0.3 * LEFT)
                        )
                        text.set_color(RED if delta < 0 else GREY)
                        delta_texts.add(text)
            self.play(Write(delta_texts))
            self.wait(1)

            # === Если нет отрицательных дельт — оптимум ===
            entering = next(
                (
                    (i, j)
                    for (i, j), d in sorted(deltas.items(), key=lambda x: x[1])
                    if d < 0
                ),
                None,
            )
            if not entering:
                break

            ei, ej = entering
            highlight = Square(side_length=1.2).move_to(coords[(ei, ej)]).set_color(RED)
            self.play(ShowCreation(highlight))
            self.wait(1)

            # === Автоматическое нахождение цикла ===
            def find_cycle(start, allocations):
                def get_neighbors(pos, visited, is_row):
                    i, j = pos
                    neighbors = []
                    visited_set = set(visited)

                    for ii, jj in allocations:
                        if (ii, jj) in visited_set or (ii, jj) == pos:
                            continue
                        if is_row and ii == i:
                            neighbors.append((ii, jj))
                        elif not is_row and jj == j:
                            neighbors.append((ii, jj))

                    if start and start != pos:
                        si, sj = start
                        if is_row and si == i:
                            neighbors.append(start)
                        elif not is_row and sj == j:
                            neighbors.append(start)

                    return neighbors

                queue = deque()
                queue.append((start, [start], True))

                while queue:
                    current, path, is_row = queue.popleft()

                    for neighbor in get_neighbors(current, set(path), is_row):
                        if neighbor == start and len(path) >= 4 and len(path) % 2 == 0:
                            return path
                        if neighbor not in path:
                            queue.append((neighbor, path + [neighbor], not is_row))

                return None

            cycle = find_cycle(entering, allocations)
            if not cycle:
                break

            # === Отрисовка цикла ===
            arrows = VGroup()
            for k in range(len(cycle)):
                a, b = coords[cycle[k]], coords[cycle[(k + 1) % len(cycle)]]
                arrows.add(Arrow(a, b, buff=0.1, stroke_color=YELLOW))
            self.play(ShowCreation(arrows))
            self.wait(1)

            # === Применение оптимизации ===
            signs = [1 if i % 2 == 0 else -1 for i in range(len(cycle))]
            minus_vals = [
                int(allocations[idx].tex_string)
                for idx, s in zip(cycle, signs)
                if s == -1
            ]
            theta = min(minus_vals)

            count = minus_vals.count(theta)

            for idx, sign in zip(cycle, signs):
                if idx in allocations:
                    label = allocations[idx]
                    old_val = int(label.tex_string)
                    new_val = old_val + sign * theta
                    self.play(FadeOut(label))
                    if new_val > 0 or count > 1:
                        new_label = (
                            Tex(f"{new_val}")
                            .set_color(GREEN)
                            .scale(0.7)
                            .move_to(label.get_center())
                        )
                        allocations[idx] = new_label
                        self.play(Write(new_label))

                        if new_val == 0:
                            count -= 1
                    else:
                        del allocations[idx]
                else:
                    pos = coords[idx] + 0.4 * DOWN + 0.5 * RIGHT
                    new_label = Tex(f"{theta}").set_color(GREEN).scale(0.7).move_to(pos)
                    allocations[idx] = new_label
                    self.play(Write(new_label))

            cost_label = self.show_total_cost(
                allocations, coords, self.cost_matrix, cost_label
            )
            self.wait(1)
            self.play(
                FadeOut(highlight),
                FadeOut(arrows),
                FadeOut(delta_texts),
                FadeOut(potentials),
            )

        line = Mobject()

        if self.has_extra_demand:
            line = Line(
                coords[(0, n - 1)] + 0.5 * UP,
                coords[(m, n - 1)] + 0.5 * DOWN,
            )
        if self.has_extra_supply:
            line = Line(
                coords[(m - 1, 0)] + 0.5 * LEFT,
                coords[(m - 1, n)] + 0.5 * RIGHT,
            )

        self.play(ShowCreation(line), cost_label.animate.set_color(GREEN))

        self.wait(3)
