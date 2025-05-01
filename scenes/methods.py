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
        name: Dot(pos[name], fill_color=BLUE).scale(1.2) for name in labels
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
                line = Line(pos[u], pos[v])  # Дуга между вершинами
                weight_label = Tex(str(w)).move_to(
                    (pos[u] + pos[v]) / 2 + 0.3 * UP
                )  # Текст для веса дуги
                edges.append(
                    (w, line, (u, v), weight_label)
                )  # Добавляем в список дугу с его весом
    return edges


# Функция для создания ориентированных рёбер (стрелок) на основе матрицы смежности
def create_edges(n, labels, adjacency_matrix, pos, ignore_arcs=False):
    # Подсчёт рёбер для определения двунаправленных соединений
    edge_count = defaultdict(int)
    if not ignore_arcs:
        for i in range(n):
            for j in range(n):
                if adjacency_matrix[i][j] != 0:
                    edge_count[(i, j)] += 1

    edges = []  # Список для хранения рёбер (стрелок)
    for i in range(n):
        for j in range(n):
            w = adjacency_matrix[i][j]  # Вес ребра между вершинами i и j
            if w:  # Если вес не ноль (существует ребро)
                u, v = labels[i], labels[j]  # Метки вершин
                p1, p2 = pos[u], pos[v]  # Позиции начальной и конечной вершины

                # Проверка: есть ли обратное ребро из j в i (двунаправленность)
                if (j, i) in edge_count:
                    # Смещение для дуги, чтобы рёбра не накладывались друг на друга
                    offset = 0.1 * normalize(np.cross(p2 - p1, OUT))
                    norm = 0.2 * normalize(p2 - p1)
                    p1_shifted = p1 + offset + norm
                    p2_shifted = p2 + offset - norm

                    # Построение дуги между смещёнными точками
                    arc = ArcBetweenPoints(
                        p1_shifted, p2_shifted, angle=0.75, color=WHITE
                    )

                    # Стрелка на конце дуги
                    tip = Triangle(
                        stroke_width=0, fill_color=WHITE, fill_opacity=1
                    ).scale(0.125)

                    # Определение направления касательной к дуге в конце (для ориентации стрелки)
                    end_point = arc.point_from_proportion(1)
                    prev_point = arc.point_from_proportion(1 - EPSILON)
                    tangent = normalize(end_point - prev_point)
                    angle = angle_of_vector(tangent)

                    # Размещение и поворот стрелки по направлению касательной
                    tip.move_to(end_point)
                    tip.rotate(angle - PI / 2)

                    arrow = VGroup(arc, tip)  # Объединение дуги и стрелки
                    label_pos = (
                        arc.point_from_proportion(0.5) + 0.2 * UP
                    )  # Позиция текста веса
                else:
                    # Если обратного ребра нет — обычная стрелка
                    arrow = Arrow(p1, p2, buff=0.15)
                    label_pos = (p1 + p2) / 2 + 0.3 * UP  # Позиция текста веса

                label = Tex(str(w)).scale(0.7).move_to(label_pos)  # Надпись веса
                edges.append((w, arrow, (u, v), label))  # Добавление ребра в список

    return edges
