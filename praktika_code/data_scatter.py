"""Задание № 2: система первичной визуализации данных."""
from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import dataset

# Цифровой корень ID 70227772 равен 7; индивидуальный маркер — «v».
MARKER = "v"


class ScatterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Первичная визуализация данных")
        self.root.minsize(900, 600)

        self.df = dataset.df
        self.columns = dataset.numeric_columns(self.df)
        if len(self.columns) < 2:
            messagebox.showerror("Ошибка", "Необходимо минимум две счётные колонки.")
            root.destroy()
            return

        self.x_column = self.columns[0]
        self.y_column = self.columns[1]

        left = tk.LabelFrame(root, text="Ось Y")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)
        for column in self.columns:
            tk.Button(left, text=column, command=lambda c=column: self.select_y(c)).pack(
                fill=tk.X, padx=3, pady=2
            )

        center = tk.Frame(root)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=center)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        bottom = tk.LabelFrame(center, text="Ось X")
        bottom.pack(fill=tk.X, padx=6, pady=6)
        for column in self.columns:
            tk.Button(bottom, text=column, command=lambda c=column: self.select_x(c)).pack(
                side=tk.LEFT, padx=2, pady=2
            )
        tk.Button(bottom, text="Сохранить", command=self.save_graph).pack(side=tk.RIGHT, padx=5)

        self.draw_graph()

    def select_x(self, column: str) -> None:
        self.x_column = column
        self.draw_graph()

    def select_y(self, column: str) -> None:
        self.y_column = column
        self.draw_graph()

    def draw_graph(self) -> None:
        self.axes.clear()
        data = self.df[[self.x_column, self.y_column]].dropna()
        self.axes.scatter(data[self.x_column], data[self.y_column], marker=MARKER)
        self.axes.set_xlabel(self.x_column)
        self.axes.set_ylabel(self.y_column)
        self.axes.set_title(f"{self.y_column} от {self.x_column}")
        self.axes.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()

    def save_graph(self) -> None:
        filename = datetime.now().strftime("graph%H_%M_%S.png")
        self.figure.savefig(filename, dpi=150, bbox_inches="tight")
        messagebox.showinfo("Сохранение", f"График сохранён в файл {filename}")


def main() -> None:
    root = tk.Tk()
    ScatterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
