"""Задание № 4: модификация визуализаций средствами ручного рисования."""
from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import colorchooser, messagebox, ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

import dataset

MARKER = "v"
DEFAULT_CMAP = "PuBuGn"
# Цифровой корень 70227772: 7; 7 // 2 + 5 = 8.
DEFAULT_WIDTH = 8
# Последние 6 цифр 227772: R=22, G=77, B=72.
DEFAULT_COLOR = "#164D48"
CMAPS = [
    "viridis", "plasma", "inferno", "magma", "cividis", "Greys", "Purples",
    "Blues", "Greens", "Oranges", "Reds", "YlOrBr", "YlOrRd", "OrRd",
    "PuRd", "RdPu", "BuPu", "GnBu", "PuBu", "YlGnBu", "PuBuGn", "BuGn",
    "YlGn", "binary", "gist_yarg", "spring", "summer", "autumn", "winter",
]


class DrawApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Визуализация с ручным рисованием")
        self.root.minsize(1050, 680)

        self.df = dataset.df
        self.numeric = dataset.numeric_columns(self.df)
        self.categorical = dataset.categorical_columns(self.df)
        self.columns = list(self.df.columns)
        if len(self.numeric) < 2:
            messagebox.showerror("Ошибка", "Необходимо минимум две счётные колонки.")
            root.destroy()
            return

        self.x_column = self.numeric[0]
        self.y_column = self.numeric[1]
        self.cmap_name = tk.StringVar(value=DEFAULT_CMAP)
        self.line_width = tk.IntVar(value=DEFAULT_WIDTH)
        self.line_color = DEFAULT_COLOR

        self.drawing_enabled = False
        self.mouse_pressed = False
        self.current_line = None
        self.last_completed_line = None

        top = tk.Frame(root)
        top.pack(fill=tk.X, padx=6, pady=6)

        tk.Label(top, text="Цветовая схема:").pack(side=tk.LEFT)
        cmap_box = ttk.Combobox(
            top, textvariable=self.cmap_name, values=CMAPS, state="readonly", width=13
        )
        cmap_box.pack(side=tk.LEFT, padx=4)
        cmap_box.bind("<<ComboboxSelected>>", self.on_cmap_change)

        self.draw_button = tk.Button(top, text="Режим рисования", command=self.toggle_drawing)
        self.draw_button.pack(side=tk.LEFT, padx=5)

        tk.Label(top, text="Толщина:").pack(side=tk.LEFT)
        tk.Spinbox(top, from_=1, to=30, textvariable=self.line_width, width=4).pack(
            side=tk.LEFT, padx=3
        )

        self.color_button = tk.Button(
            top, text="   ", bg=self.line_color, command=self.choose_color, relief=tk.RAISED
        )
        self.color_button.pack(side=tk.LEFT, padx=5)

        tk.Button(top, text="Сохранить", command=self.save_graph).pack(side=tk.RIGHT)

        left = tk.LabelFrame(root, text="Ось Y")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)
        for column in self.columns:
            tk.Button(left, text=column, command=lambda c=column: self.select_y(c)).pack(
                fill=tk.X, padx=3, pady=1
            )

        center = tk.Frame(root)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=center)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        bottom = tk.LabelFrame(center, text="Ось X")
        bottom.pack(fill=tk.X, padx=6, pady=6)
        for column in self.columns:
            tk.Button(bottom, text=column, command=lambda c=column: self.select_x(c)).pack(
                side=tk.LEFT, padx=1, pady=2
            )

        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)
        self.root.bind_all("<Control-z>", self.undo_last_line)
        self.root.bind_all("<Control-Z>", self.undo_last_line)

        self.draw_graph()

    def is_numeric(self, column: str) -> bool:
        return column in self.numeric

    def is_categorical(self, column: str) -> bool:
        return column in self.categorical

    def palette(self, count: int) -> np.ndarray:
        """Возвращает насыщенные оттенки выбранной цветовой схемы."""
        cmap = matplotlib.colormaps[self.cmap_name.get()]
        if count <= 1:
            return np.asarray([cmap(0.72)])
        return cmap(np.linspace(0.28, 0.92, count))

    def select_x(self, column: str) -> None:
        self.disable_drawing()
        self.x_column = column
        self.draw_graph()

    def select_y(self, column: str) -> None:
        self.disable_drawing()
        self.y_column = column
        self.draw_graph()

    def on_cmap_change(self, _event=None) -> None:
        self.disable_drawing()
        self.draw_graph()

    def draw_graph(self) -> None:
        self.axes.clear()
        x, y = self.x_column, self.y_column
        x_num, y_num = self.is_numeric(x), self.is_numeric(y)
        x_cat, y_cat = self.is_categorical(x), self.is_categorical(y)

        if x == y and x_num:
            values = self.df[x].dropna()
            _counts, _bins, patches = self.axes.hist(
                values, bins=10, edgecolor="black", linewidth=1.0
            )
            for patch, color in zip(patches, self.palette(len(patches))):
                patch.set_facecolor(color)
            self.axes.set_xlabel(x)
            self.axes.set_ylabel("Количество")
            self.axes.set_title(f"Гистограмма распределения: {x}")
        elif x == y and x_cat:
            counts = self.df[x].fillna("Нет данных").astype(str).value_counts()
            self.axes.pie(
                counts.values, labels=counts.index, colors=self.palette(len(counts)), autopct="%1.1f%%"
            )
            self.axes.set_title(f"Круговая диаграмма: {x}")
        elif x_cat and y_num:
            counts = self.df[x].fillna("Нет данных").astype(str).value_counts()
            self.axes.bar(
                counts.index, counts.values, color=self.palette(len(counts)),
                edgecolor="black", linewidth=0.8
            )
            self.axes.set_xlabel(x)
            self.axes.set_ylabel("Количество записей")
            self.axes.set_title(f"Столбчатая диаграмма по категориям: {x}")
            self.axes.tick_params(axis="x", labelrotation=45)
        elif x_num and y_cat:
            prepared = self.df[[x, y]].dropna()
            groups = list(prepared.groupby(y, sort=False)[x])
            labels = [str(name) for name, _values in groups]
            values = [group.to_numpy() for _name, group in groups]
            boxes = self.axes.boxplot(values, tick_labels=labels, patch_artist=True)
            for patch, color in zip(boxes["boxes"], self.palette(len(boxes["boxes"]))):
                patch.set_facecolor(color)
            self.axes.set_xlabel(y)
            self.axes.set_ylabel(x)
            self.axes.set_title(f"Коробочная диаграмма: {x} по {y}")
            self.axes.tick_params(axis="x", labelrotation=45)
        elif x_num and y_num:
            data = self.df[[x, y]].dropna()
            self.axes.scatter(
                data[x], data[y], marker=MARKER, color=self.palette(1)[0],
                edgecolors="black", linewidths=0.45, alpha=0.9
            )
            self.axes.set_xlabel(x)
            self.axes.set_ylabel(y)
            self.axes.set_title(f"Точечная диаграмма: {y} от {x}")
        else:
            counts = self.df[x].fillna("Нет данных").astype(str).value_counts()
            self.axes.bar(
                counts.index, counts.values, color=self.palette(len(counts)),
                edgecolor="black", linewidth=0.8
            )
            self.axes.set_xlabel(x)
            self.axes.set_ylabel("Количество записей")
            self.axes.set_title(f"Распределение категорий: {x}")
            self.axes.tick_params(axis="x", labelrotation=45)

        self.axes.grid(True, alpha=0.25)
        self.figure.tight_layout()
        self.last_completed_line = None
        self.canvas.draw()

    def toggle_drawing(self) -> None:
        if self.drawing_enabled:
            self.disable_drawing()
        else:
            self.drawing_enabled = True
            self.draw_button.config(relief=tk.SUNKEN)
            self.canvas_widget.config(cursor="pencil")

    def disable_drawing(self) -> None:
        self.drawing_enabled = False
        self.mouse_pressed = False
        self.current_line = None
        self.draw_button.config(relief=tk.RAISED)
        self.canvas_widget.config(cursor="")

    def choose_color(self) -> None:
        selected = colorchooser.askcolor(color=self.line_color, title="Выбор цвета кисти")[1]
        if selected:
            self.line_color = selected
            self.color_button.config(bg=selected)

    def on_mouse_press(self, event) -> None:
        # Правая кнопка — альтернативный выход из режима рисования.
        if event.button == 3 and self.drawing_enabled:
            self.disable_drawing()
            return
        if (
            not self.drawing_enabled
            or event.button != 1
            or event.inaxes is not self.axes
            or event.xdata is None
            or event.ydata is None
        ):
            return

        self.mouse_pressed = True
        self.current_line, = self.axes.plot(
            [event.xdata],
            [event.ydata],
            color=self.line_color,
            linewidth=self.line_width.get(),
            solid_capstyle="projecting",
            zorder=100,
        )
        self.canvas.draw_idle()

    def on_mouse_move(self, event) -> None:
        if not self.drawing_enabled or not self.mouse_pressed or self.current_line is None:
            return
        if event.inaxes is not self.axes or event.xdata is None or event.ydata is None:
            return

        x_values = list(self.current_line.get_xdata())
        y_values = list(self.current_line.get_ydata())
        x_values.append(event.xdata)
        y_values.append(event.ydata)
        self.current_line.set_data(x_values, y_values)
        self.canvas.draw_idle()

    def on_mouse_release(self, _event) -> None:
        if self.current_line is not None:
            self.last_completed_line = self.current_line
        self.current_line = None
        self.mouse_pressed = False

    def undo_last_line(self, _event=None) -> None:
        # Во время удержания кнопки мыши отмена не выполняется.
        if self.mouse_pressed or self.last_completed_line is None:
            return
        try:
            self.last_completed_line.remove()
        except ValueError:
            pass
        self.last_completed_line = None
        self.canvas.draw_idle()

    def save_graph(self) -> None:
        filename = datetime.now().strftime("graph%H_%M_%S.png")
        self.figure.savefig(filename, dpi=150, bbox_inches="tight")
        messagebox.showinfo("Сохранение", f"График вместе с рисунками сохранён в файл {filename}")


def main() -> None:
    root = tk.Tk()
    DrawApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
