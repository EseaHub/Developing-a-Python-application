from solver import *

import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox

# Глобальные переменные
entries = []
selected_method = None

def validate_ranking():
    try:
        # Проверяем, что выбраны количество альтернатив и экспертов
        try:
            num_alternatives = int(alternatives_entry.get())
            num_experts = int(experts_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите количество альтернатив и экспертов!")
            return None
            
        # Проверяем, что метод выбран
        if selected_method is None:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите метод решения.")
            return None
            
        # Проверяем, что таблица создана
        if not entries:
            messagebox.showerror("Ошибка", "Сначала создайте таблицу с помощью кнопки 'Принять'!")
            return None
            
        # Проверяем все столбцы
        for j in range(num_experts):
            column_values = []
            for i in range(num_alternatives):
                value = entries[i][j].get()
                if not value:
                    messagebox.showerror("Ошибка", f"Пустое значение в строке {i+1}, столбец {j+1}!")
                    return None
                try:
                    num = int(value)
                    column_values.append(num)
                except ValueError:
                    messagebox.showerror("Ошибка", f"Некорректное значение в строке {i+1}, столбец {j+1}!")
                    return None
            
            # Проверяем, что все числа от 1 до "количества альтернатив"
            expected = set(range(1, num_alternatives + 1))
            actual = set(column_values)
            
            if len(column_values) != len(expected):
                messagebox.showerror("Ошибка", f"В столбце {j+1} недостаточно значений!")
                return None
                
            if actual != expected:
                messagebox.showerror("Ошибка", 
                    f"В столбце {j+1} должны быть все числа от 1 до {num_alternatives} без повторений!")
                return None
        
        # Если все проверки пройдены, возвращаем данные
        rvalues = []
        for i in range(num_alternatives):
            row_values = []
            for j in range(num_experts):
                row_values.append(int(entries[i][j].get()))
            rvalues.append(row_values)

        return np.array(rvalues, dtype=int), selected_method
        
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        return None, None

def create_table():
    try:
        num_alternatives = int(alternatives_entry.get())
        num_experts = int(experts_entry.get())
        
        if num_alternatives > 10 or num_alternatives < 3:
            messagebox.showerror("Ошибка", "Число альтернатив должно быть от 3 до 10!")
            return
        if num_experts > 9 or num_experts < 3:
            messagebox.showerror("Ошибка", "Число экспертов должно быть от 3 до 9!")
            return
            
        # Проверка на четное число экспертов
        if num_experts % 2 == 0:
            messagebox.showwarning("Предупреждение", 
                               "Рекомендуется использовать нечетное число экспертов для избежания ничьих в результатах!")
            return    
        # Очищаем старую таблицу
        for widget in table_frame.winfo_children():
            widget.destroy()
            
        # Создаем заголовки столбцов
        for j in range(num_experts):
            label = ttk.Label(table_frame, text=f"Эксперт {j+1}", font=('Helvetica', 10, 'italic'))
            label.grid(row=0, column=j+1, padx=5, pady=5)  # Сдвигаем на 1 колонку вправо
            
        # Создаем поле для ввода
        global entries
        entries = []
        for i in range(1, num_alternatives + 1):
            row_entries = []
            # Добавляем метку для строки
            if i == 1:
                label = ttk.Label(table_frame, text="Лучшая альтернатива", font=('Helvetica', 10))
                label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.E)
            elif i == num_alternatives:
                label = ttk.Label(table_frame, text="Худшая альтернатива", font=('Helvetica', 10))
                label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.E)
                
            # Добавляем поля ввода
            for j in range(num_experts):
                entry = ttk.Entry(table_frame, width=10)
                entry.grid(row=i, column=j+1, padx=5, pady=5)
                row_entries.append(entry)
            entries.append(row_entries)
            
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения!")

def select_method(method):
    global selected_method
    selected_method = method
    # Подсвечиваем выбранную кнопку
    for btn in method_buttons:
        btn.config(style='TButton')
    method_buttons[method-1].config(style='Selected.TButton')

# Создание основного окна
root = tk.Tk()
root.title("Ранжирование альтернатив")
root.geometry("800x600")

# Создаем стили для интерфейса
style = ttk.Style()
style.configure("Blue.TSeparator", background="blue")
style.configure("MethodFrame.TFrame", background="#0078D7", borderwidth=2, relief="solid")
style.configure("MethodLabel.TLabel", foreground="white", background="#0078D7", 
               font=('Arial', 10, 'bold'), padding=5)
style.configure("Method.TButton", width=25, padding=5)
style.configure("Selected.TButton", background="#0078D7", foreground="white")

# Главный заголовок с разделительной линией
header_frame = ttk.Frame(root)
header_frame.pack(fill=tk.X, padx=10, pady=10)

main_header = ttk.Label(header_frame, text="Ранжирование альтернатив", font=('Arial', 16, 'bold'))
main_header.pack()

# Голубая разделительная линия
separator = ttk.Separator(header_frame, orient=tk.HORIZONTAL)
separator.pack(fill=tk.X, pady=5)
separator.configure(style="Blue.TSeparator")

# Меню с вкладками (подзаголовки)
tabs_frame = ttk.Frame(root)
tabs_frame.pack(fill=tk.X, padx=10, pady=(5, 0))

# Создаем 3 равные колонки для заголовков
tabs_frame.columnconfigure(0, weight=1, uniform="group1")
tabs_frame.columnconfigure(1, weight=1, uniform="group1")
tabs_frame.columnconfigure(2, weight=1, uniform="group1")

# Функции для открытия PDF
def open_help():
    import webbrowser
    try:
        webbrowser.open('help.pdf')  # файл с помощью
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл справки: {str(e)}")

def open_theory():
    import webbrowser
    try:
        webbrowser.open('theory.pdf')  # файл с теорией
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл теории: {str(e)}")

# Заголовки вкладок (красные)
tab1 = ttk.Label(tabs_frame, text="Выбор альтернатив", font=('Arial', 10, 'bold'), foreground="red")
tab1.grid(row=0, column=0, sticky=tk.NSEW)
tab1.configure(anchor=tk.CENTER)

# Создаем "кнопки" для Помощи и Теории
help_button = ttk.Label(
    tabs_frame, 
    text="Помощь", 
    font=('Arial', 10, 'bold'), 
    foreground="red",
    cursor="hand2"  # Курсор в виде руки (пальца)
)
help_button.grid(row=0, column=1, sticky=tk.NSEW)
help_button.configure(anchor=tk.CENTER)
help_button.bind("<Button-1>", lambda e: open_help())

theory_button = ttk.Label(
    tabs_frame, 
    text="Теория", 
    font=('Arial', 10, 'bold'), 
    foreground="red",
    cursor="hand2"
)
theory_button.grid(row=0, column=2, sticky=tk.NSEW)
theory_button.configure(anchor=tk.CENTER)
theory_button.bind("<Button-1>", lambda e: open_theory())

# Основной контейнер для содержимого (под подзаголовками)
content_frame = ttk.Frame(root)
content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Настраиваем grid для равномерного распределения
content_frame.columnconfigure(0, weight=1)
content_frame.columnconfigure(1, weight=1)
content_frame.columnconfigure(2, weight=1)


input_frame = ttk.Frame(content_frame)
input_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

alternatives_label = ttk.Label(input_frame, text="Число альтернатив (3-10):")
alternatives_label.grid(row=0, column=0, padx=5, sticky=tk.W)
alternatives_entry = ttk.Entry(input_frame, width=5)
alternatives_entry.grid(row=0, column=1, padx=5)

experts_label = ttk.Label(input_frame, text="Число экспертов (3-9, нечетное):")
experts_label.grid(row=1, column=0, padx=5, sticky=tk.W)
experts_entry = ttk.Entry(input_frame, width=5)
experts_entry.grid(row=1, column=1, padx=5)

accept_button = ttk.Button(input_frame, text="Принять", command=create_table)
accept_button.grid(row=0, column=2, rowspan=2, padx=10)

# Средняя колонка (пустая)
middle_frame = ttk.Frame(content_frame)
middle_frame.grid(row=0, column=1, sticky=tk.NSEW)

# Правая колонка - методы
theory_frame = ttk.Frame(content_frame)
theory_frame.grid(row=0, column=2, sticky=tk.NSEW, padx=5)


methods_frame = ttk.Frame(theory_frame, style="MethodFrame.TFrame", padding=5)
methods_frame.pack(fill=tk.X, pady=5)

# Метка "Методы" в голубом прямоугольнике
methods_label = ttk.Label(methods_frame, text="Методы", style="MethodLabel.TLabel")
methods_label.pack(fill=tk.X)

# Кнопки методов
method_buttons = []
methods = [
    "Гамильтоновы пути",
    "Гамильтонов путь максимальной длины",
    "Индексирование вершин"
]

for i, method in enumerate(methods, 1):
    btn = ttk.Button(
        methods_frame, 
        text=method, 
        style="Method.TButton",
        command=lambda m=i: select_method(m)
    )
    btn.pack(fill=tk.X, pady=2)
    method_buttons.append(btn)

# Фрейм для таблицы
table_frame = ttk.Frame(root, padding="10")
table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Фрейм для кнопки "Пуск"
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

# Создаем холст для кнопки "Пуск"
canvas = tk.Canvas(button_frame, width=120, height=50, highlightthickness=0)
canvas.pack()


button_bg = canvas.create_oval(5, 5, 115, 45, fill="red", outline="darkred")
button_text = canvas.create_text(60, 25, text="Пуск", font=('Arial', 14, 'bold'), fill="white")

# Функция для обработки нажатия
def on_start_click(event):
    result = validate_ranking()
    if result[0] is not None:
        solve(values=result[0], method=result[1])

# Привязываем события
canvas.tag_bind(button_bg, "<Button-1>", on_start_click)
canvas.tag_bind(button_text, "<Button-1>", on_start_click)

# Эффект при наведении
def on_enter(event):
    canvas.itemconfig(button_bg, fill="dark red")
    
def on_leave(event):
    canvas.itemconfig(button_bg, fill="red")

canvas.bind("<Enter>", on_enter)
canvas.bind("<Leave>", on_leave)

root.mainloop()