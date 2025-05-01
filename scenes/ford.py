from manimlib import *
from .methods import compute_positions, create_vertices, create_edges
from .scene import InteractiveScene


class BellmanFordFromAdjacency(InteractiveScene):
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

        distance_labels = {}
        for v in self.labels:
            text = r"\infty" if dist[v] == float("inf") else str(int(dist[v]))
            label = Tex(text).scale(0.7).next_to(pos[v] * 1.45, ORIGIN)
            distance_labels[v] = label
        self.add(*distance_labels.values())

        info_box = Tex("").to_corner(UL)
        self.add(info_box)

        for step in range(self.n - 1):
            self.play(
                Transform(
                    info_box,
                    Tex(f"\\text{{Итерация }} {step+1}").scale(0.8).to_corner(UL),
                ),
                *[line.animate.set_color(WHITE) for w, line, (a, b), _ in edges],
                run_time=0.5,
            )
            updated = False
            for w, line, (u, v), _ in edges:
                if dist[u] != float("inf") and dist[u] + w < dist[v]:
                    self.play(line.animate.set_color(GREEN), run_time=0.4)

                    old_val = (
                        r"\infty" if dist[v] == float("inf") else str(int(dist[v]))
                    )

                    dist[v] = dist[u] + w

                    update_text = Tex(
                        f"{v}: {old_val} \\rightarrow {dist[v]}"
                    ).to_corner(UR)

                    self.play(Write(update_text), run_time=0.6)

                    self.play(FadeOut(distance_labels[v]), run_time=0.2)

                    new_label = (
                        Tex(str(int(dist[v]))).scale(0.7).next_to(pos[v] * 1.45, ORIGIN)
                    )

                    distance_labels[v] = new_label
                    self.add(new_label)

                    self.play(FadeOut(update_text), run_time=0.2)
                    updated = True
                else:
                    self.play(line.animate.set_color(GREY), run_time=0.2)
            if not updated:
                break

            self.wait(1)
            self.pause()

        self.play(
            FadeOut(info_box),
            *[label.animate.set_color(GREEN) for label in distance_labels.values()],
        )

        self.wait(3)
