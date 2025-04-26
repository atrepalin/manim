import os
import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
from tkinterdnd2 import DND_FILES, TkinterDnD
import ast
from scenes import scenes
from runner import run
from examples import examples
from functools import partial


class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Алгоритмы на графах")
        self.geometry("1300x800")
        self.configure(bg="#f0f0f0")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 10), padding=6)
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 12))

        self.selected_row = 0
        self.selected_col = 0
        self.selected_task = None

        self.setup_ui()

        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.on_drop)
        self.bind_all("<Control-KeyPress>", self.on_ctrl_key)

    def setup_ui(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.left_frame = ttk.Frame(container, width=220)
        self.left_frame.pack(side="left", fill="y")

        label = ttk.Label(
            self.left_frame, text="Выберите задачу:", font=("Segoe UI", 14, "bold")
        )
        label.pack(pady=(0, 20))

        options = [
            ("Максимальный поток", lambda: self.show_table("flow")),
            ("Транспортная задача", lambda: self.show_table("transport")),
            ("Мин. остовное дерево - Прим", lambda: self.show_table("mst_prim")),
            ("Мин. остовное дерево - Краскал", lambda: self.show_table("mst_kruskal")),
        ]

        for text, command in options:
            button = ttk.Button(self.left_frame, text=text, command=command)
            button.pack(pady=5, fill="x")

        separator = ttk.Separator(container, orient="vertical")
        separator.pack(side="left", fill="y", padx=10)

        self.center_frame = ttk.Frame(container)
        self.center_frame.pack(side="left", fill="both", expand=True)

        self.entries = []

        # Статус
        self.status_label = ttk.Label(self, text="", anchor="e", font=("Segoe UI", 10))
        self.status_label.pack(side="bottom", anchor="e", padx=10, pady=5)

    def show_status(self, message, color="green", duration=3000):
        self.status_label.config(text=message, foreground=color)
        if duration:
            self.after(duration, lambda: self.status_label.config(text=""))

    def show_table(self, task_type):
        self.selected_task = task_type

        for widget in self.center_frame.winfo_children():
            widget.destroy()

        title = ttk.Label(
            self.center_frame, text="Введите матрицу:", font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=10)

        controls = ttk.Frame(self.center_frame)
        controls.pack(pady=10)

        ttk.Button(controls, text="Добавить строку", command=self.add_row_near).pack(
            side="left", padx=5
        )
        ttk.Button(controls, text="Удалить строку", command=self.delete_row).pack(
            side="left", padx=5
        )
        ttk.Button(
            controls, text="Добавить столбец", command=self.add_column_near
        ).pack(side="left", padx=5)
        ttk.Button(controls, text="Удалить столбец", command=self.delete_column).pack(
            side="left", padx=5
        )
        ttk.Button(controls, text="Очистить таблицу", command=self.clear_table).pack(
            side="left", padx=5
        )

        load_controls = ttk.Frame(self.center_frame)
        load_controls.pack(pady=10)

        ttk.Button(
            load_controls, text="Загрузить пример", command=self.load_example
        ).pack(side="left", padx=5)
        ttk.Button(
            load_controls, text="Загрузить из буфера", command=self.load_from_clipboard
        ).pack(side="left", padx=5)
        ttk.Button(
            load_controls, text="Загрузить из TXT", command=self.load_from_txt
        ).pack(side="left", padx=5)
        ttk.Button(
            load_controls, text="Загрузить из Excel", command=self.load_from_excel
        ).pack(side="left", padx=5)

        self.table_frame = ttk.Frame(self.center_frame)
        self.table_frame.pack(fill="both", expand=True, pady=10)

        self.runner_frame = ttk.Frame(self.center_frame)
        self.runner_frame.pack(pady=10)

        ttk.Button(
            self.runner_frame,
            text="Запустить алгоритм",
            command=partial(self.run_algorithm, False, False),
        ).pack(side="left", padx=5)
        ttk.Button(
            self.runner_frame,
            text="Запустить с пропуском анимации",
            command=partial(self.run_algorithm, True, False),
        ).pack(side="left", padx=5)
        ttk.Button(
            self.runner_frame,
            text="Сохранить в файл",
            command=partial(self.run_algorithm, False, True),
        ).pack(side="left", padx=5)

        self.rows = 3
        self.cols = 3
        self.entries = []

        self.build_table()

    def run_algorithm(self, skip_animations, render_to_file):
        matrix = self.get_matrix()

        if not render_to_file:
            self.withdraw()

        run(
            scenes[self.selected_task],
            matrix,
            skip_animations=skip_animations,
            render_to_file=render_to_file,
        )

        if not render_to_file:
            self.deiconify()

    def save_data(self):
        data = []
        for row in self.entries:
            data_row = []
            for entry in row:
                data_row.append(entry.get() if entry else "")
            data.append(data_row)
        return data

    def get_matrix(self):
        data = self.save_data()

        def parse_int(x):
            try:
                return int(x)
            except ValueError:
                return 0

        return [[parse_int(x) for x in row] for row in data]

    def build_table(self, saved_data=None):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        empty = ttk.Label(self.table_frame, text="", width=4)
        empty.grid(row=0, column=0, padx=2, pady=2)

        for c in range(self.cols):
            label = ttk.Label(
                self.table_frame,
                text=str(c + 1),
                width=6,
                anchor="center",
                background="#dddddd",
            )
            label.grid(row=0, column=c + 1, padx=2, pady=2)

        for r in range(self.rows):
            row_entries = []
            label = ttk.Label(
                self.table_frame,
                text=str(r + 1),
                width=4,
                anchor="center",
                background="#dddddd",
            )
            label.grid(row=r + 1, column=0, padx=2, pady=2)

            for c in range(self.cols):
                entry = ttk.Entry(self.table_frame, width=10, justify="center")
                entry.grid(row=r + 1, column=c + 1, padx=2, pady=2)
                entry.bind(
                    "<FocusIn>", lambda e, row=r, col=c: self.set_selected(row, col)
                )
                entry.bind(
                    "<FocusOut>", lambda e, row=r, col=c: self.validate_cell(row, col)
                )

                if saved_data and r < len(saved_data) and c < len(saved_data[r]):
                    entry.insert(0, saved_data[r][c])
                row_entries.append(entry)
            self.entries.append(row_entries)

        self.validate_full_matrix()

    def set_selected(self, row, col):
        self.selected_row = row
        self.selected_col = col

    def add_row_near(self):
        data = self.save_data()
        data.insert(self.selected_row + 1, ["" for _ in range(self.cols)])
        self.rows += 1
        self.build_table(data)

    def add_column_near(self):
        data = self.save_data()
        for row in data:
            row.insert(self.selected_col + 1, "")
        self.cols += 1
        self.build_table(data)

    def delete_row(self):
        if self.rows > 1:
            data = self.save_data()
            data.pop(self.selected_row)
            self.rows -= 1
            self.selected_row = max(0, self.selected_row - 1)
            self.build_table(data)

    def delete_column(self):
        if self.cols > 1:
            data = self.save_data()
            for row in data:
                row.pop(self.selected_col)
            self.cols -= 1
            self.selected_col = max(0, self.selected_col - 1)
            self.build_table(data)

    def clear_table(self):
        for row in self.entries:
            for entry in row:
                entry.delete(0, tk.END)
        self.validate_full_matrix()

    def parse_clipboard_text(self, text):
        text = text.strip()

        # Попробуем сначала парсить как целиком один Python-объект
        if text.startswith("[") and text.endswith("]"):
            try:
                matrix = ast.literal_eval(text)
                if isinstance(matrix, list):
                    if all(isinstance(x, list) for x in matrix):
                        return [[str(cell) for cell in row] for row in matrix]
                    else:
                        return [[str(cell) for cell in matrix]]
            except Exception:
                pass  # если не получилось, идём дальше

        # Иначе: разбиваем построчно
        rows = [row.strip() for row in text.split("\n") if row.strip()]
        matrix = []

        is_all_rows_like_lists = True
        parsed_rows = []

        for row in rows:
            # Если строка похожа на отдельный список [1,2,3]
            if row.startswith("[") and (row.endswith("]") or row.endswith("],")):
                try:
                    if row.endswith(","):
                        row = row[:-1]

                    parsed_row = ast.literal_eval(row)
                    if isinstance(parsed_row, list):
                        parsed_rows.append([str(cell) for cell in parsed_row])
                    else:
                        is_all_rows_like_lists = False
                        break
                except Exception:
                    is_all_rows_like_lists = False
                    break
            else:
                is_all_rows_like_lists = False
                break

        if is_all_rows_like_lists and parsed_rows:
            return parsed_rows

        # Иначе: обычный разбор по пробелам/запятым
        for row in rows:
            parts = []
            for part in row.replace(",", " ").split():
                if part:
                    parts.append(part)
            if parts:
                matrix.append(parts)

        return matrix

    def load_example(self):
        try:
            matrix = examples[self.selected_task]

            self.validate_matrix(matrix)
            self.rows = len(matrix)
            self.cols = max(len(r) for r in matrix)
            self.build_table(matrix)
            self.show_status("Пример загружен")
        except Exception as e:
            self.show_status(f"Ошибка загрузки: {e}", color="red")

    def load_from_clipboard(self):
        try:
            text = self.clipboard_get()
            matrix = self.parse_clipboard_text(text)

            self.validate_matrix(matrix)
            self.rows = len(matrix)
            self.cols = max(len(r) for r in matrix)
            self.build_table(matrix)
            self.show_status("Данные загружены из буфера")
        except Exception as e:
            self.show_status(f"Ошибка загрузки: {e}", color="red")

    def load_from_txt(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.load_file(path, from_excel=False)

    def load_from_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if path:
            self.load_file(path, from_excel=True)

    def load_file(self, path, from_excel=False):
        try:
            if from_excel:
                df = pd.read_excel(path, header=None)
                matrix = df.fillna("").astype(str).values.tolist()
            else:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                rows = [r.strip() for r in text.strip().split("\n") if r.strip()]
                matrix = [r.split() for r in rows]

            self.validate_matrix(matrix)
            self.rows = len(matrix)
            self.cols = max(len(r) for r in matrix)
            self.build_table(matrix)
            self.show_status("Файл успешно загружен")
        except Exception as e:
            self.show_status(f"Ошибка загрузки файла: {e}", color="red")

    def validate_matrix(self, matrix):
        for row in matrix:
            for value in row:
                if value.strip() == "":
                    continue
                try:
                    int(value)
                except ValueError:
                    raise ValueError(
                        f"Недопустимое значение '{value}', должно быть числом!"
                    )

        if self.selected_task in ("flow", "mst_prim", "mst_kruskal"):
            if len(matrix) != len(matrix[0]):
                raise ValueError("Матрица должна быть квадратной!")
        elif self.selected_task == "transport":
            if len(matrix) < 2 or len(matrix[0]) < 2:
                raise ValueError("Матрица для транспортной задачи слишком мала!")
            for row in matrix[:-1]:
                if len(row) != len(matrix[0]):
                    raise ValueError("Матрица должна быть прямоугольной!")

    def validate_cell(self, row, col):
        entry = self.entries[row][col]
        value = entry.get().strip()

        if value == "":
            entry.config(foreground="black")
            return

        try:
            int(value)
            entry.config(foreground="black")
        except ValueError:
            entry.config(foreground="red")

    def validate_full_matrix(self):
        for r, row in enumerate(self.entries):
            for c, entry in enumerate(row):
                self.validate_cell(r, c)

    def on_drop(self, event):
        path = event.data.strip("{}")
        if os.path.isdir(path):
            self.load_from_txt()
        else:
            ext = os.path.splitext(path)[1].lower()
            if ext in [".txt"]:
                self.load_file(path, from_excel=False)
            elif ext in [".xls", ".xlsx"]:
                self.load_file(path, from_excel=True)
            else:
                self.show_status("Неподдерживаемый формат файла!", color="red")

    def on_ctrl_key(self, event):
        if event.state & 0x4:
            if event.keycode == 86:
                self.handle_paste()

    def handle_paste(self, event=None):
        if self.selected_task is None:
            self.show_status("Сначала выберите задачу!", color="orange")
            return

        try:
            clipboard = self.clipboard_get()
            if os.path.isfile(clipboard):
                path = os.path.abspath(clipboard)
                if os.path.isfile(path):
                    ext = os.path.splitext(path)[1].lower()
                    if ext in [".txt"]:
                        self.load_file(path, from_excel=False)
                    elif ext in [".xls", ".xlsx"]:
                        self.load_file(path, from_excel=True)
                    else:
                        self.show_status("Неподдерживаемый формат файла!", color="red")
                    return
            self.load_from_clipboard()
        except Exception as e:
            self.show_status(f"Ошибка вставки: {e}", color="red")


if __name__ == "__main__":
    app = App()
    app.mainloop()
