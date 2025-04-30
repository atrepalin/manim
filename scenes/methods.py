from manimlib import *
import numpy as np
from collections import defaultdict


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


# Функция для создания дуг на основе матрицы смежности
def create_arcs(n, labels, adjacency_matrix, pos):
    edges = []  # Список для хранения дуг
    for i in range(n):
        for j in range(
            i + 1, n
        ):  # Проходим только по верхней треугольной части матрицы (дуги между разными вершинами)
            w = adjacency_matrix[i][j]  # Вес дуги между вершинами i и j
            if w:  # Если вес больше нуля (существует дуга)
                u, v = labels[i], labels[j]  # Извлекаем метки вершин
                line = Line(pos[u], pos[v], color=GREY)  # Дуга между вершинами
                weight_label = Tex(str(w)).move_to(
                    (pos[u] + pos[v]) / 2 + 0.3 * UP
                )  # Текст для веса дуги
                edges.append(
                    (w, line, (u, v), weight_label)
                )  # Добавляем в список дугу с его весом
    return edges


def create_edges(n, labels, adjacency_matrix, pos):
    # Подсчёт рёбер для определения двунаправленности
    edge_count = defaultdict(int)
    for i in range(n):
        for j in range(n):
            if adjacency_matrix[i][j] != 0:
                edge_count[(i, j)] += 1

    # Построение рёбер
    edges = []
    for i in range(n):
        for j in range(n):
            w = adjacency_matrix[i][j]
            if w:
                u, v = labels[i], labels[j]
                p1, p2 = pos[u], pos[v]

                # Проверка на наличие обратного ребра
                if (j, i) in edge_count:
                    offset = 0.1 * normalize(np.cross(p2 - p1, OUT))
                    p1_shifted = p1 + offset
                    p2_shifted = p2 + offset
                    arc = ArcBetweenPoints(
                        p1_shifted, p2_shifted, angle=0.75, color=WHITE
                    )
                    tip = Triangle(
                        stroke_width=0, fill_color=WHITE, fill_opacity=1
                    ).scale(0.125)

                    # Приближение касательной через разность точек
                    end_point = arc.point_from_proportion(1)
                    prev_point = arc.point_from_proportion(1 - EPSILON)
                    tangent = normalize(end_point - prev_point)
                    angle = angle_of_vector(tangent)

                    tip.move_to(end_point)
                    tip.rotate(angle - PI / 2)

                    arrow = VGroup(arc, tip)
                    label_pos = arc.point_from_proportion(0.5) + 0.2 * UP
                else:
                    arrow = Arrow(p1, p2, buff=0.15)
                    label_pos = (p1 + p2) / 2 + 0.3 * UP

                label = Tex(str(w)).scale(0.7).move_to(label_pos)
                edges.append((w, arrow, (u, v), label))

    return edges
