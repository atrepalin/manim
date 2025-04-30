from manimlib import *
from .methods import compute_positions, create_vertices, create_edges


class DijkstraFromAdjacency(Scene):
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

        for w, line, _, label in edges:
            self.play(ShowCreation(line), Write(label), run_time=0.2)

        self.wait(1)

        start = self.labels[0]
        dist = {v: float("inf") for v in self.labels}
        dist[start] = 0
        visited = set()

        distance_labels = {}
        for v in self.labels:
            text = r"\infty" if dist[v] == float("inf") else str(int(dist[v]))
            label = Tex(text).scale(0.7).next_to(pos[v] * 1.45, ORIGIN)
            distance_labels[v] = label
        self.add(*distance_labels.values())

        info_box = Tex("").to_corner(UL)
        self.add(info_box)

        while len(visited) < self.n:
            u = min((v for v in self.labels if v not in visited), key=lambda x: dist[x])
            visited.add(u)

            self.play(
                Transform(
                    info_box,
                    Tex(f"\\text{{Текущая вершина: }} {u}").scale(0.8).to_corner(UL),
                ),
                verts[u].animate.set_fill(YELLOW, opacity=0.5),
                *[line[1].animate.set_color(WHITE) for line in edges],
                run_time=0.5,
            )

            for w, line, (a, b), _ in edges:
                if a == u and b not in visited:
                    self.play(line.animate.set_color(GREEN), run_time=0.4)

                    if dist[u] + w < dist[b]:
                        old_val = (
                            r"\infty" if dist[b] == float("inf") else str(int(dist[b]))
                        )

                        dist[b] = dist[u] + w

                        update_text = Tex(
                            f"{b}: {old_val} \\rightarrow {dist[b]}"
                        ).to_corner(UR)

                        self.play(Write(update_text), run_time=0.6)

                        self.play(FadeOut(distance_labels[b]), run_time=0.2)

                        new_label = (
                            Tex(str(int(dist[b])))
                            .scale(0.7)
                            .next_to(pos[b] * 1.45, ORIGIN)
                        )

                        distance_labels[b] = new_label
                        self.add(new_label)

                        self.play(FadeOut(update_text), run_time=0.2)
                else:
                    self.play(line.animate.set_color(GREY), run_time=0.2)

            self.wait(1)

        self.play(
            FadeOut(info_box),
            *[label.animate.set_color(GREEN) for label in distance_labels.values()],
        )

        self.wait(3)
