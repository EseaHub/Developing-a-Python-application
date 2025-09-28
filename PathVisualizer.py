import networkx as nx

# Для PyInstaller
import sys
import os
if getattr(sys, 'frozen', False):
    # Если программа 'заморожена' (скомпилирована в exe)
    os.environ['MATPLOTLIBDATA'] = os.path.join(sys._MEIPASS, 'mpl-data')
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
import sympy as sp
import numpy as np

class PathVisualizer:
    def __init__(self, R, C, hamilton_paths):
        self.R = R
        self.C = C
        self.hamilton_paths = hamilton_paths
        self.current_path = 0
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        
        # Увеличиваем отступ снизу для кнопок и текста
        plt.subplots_adjust(bottom=0.25)
        
        # Создаем кнопки по центру
        button_width = 0.15
        button_height = 0.06
        total_buttons_width = 3 * button_width + 0.2  # 0.1 - расстояние между кнопками
        left_start = (1 - total_buttons_width) / 2  # Центрируем
        
        ax_prev = plt.axes([left_start, 0.05, button_width, button_height])
        ax_next = plt.axes([left_start + button_width + 0.1, 0.05, button_width, button_height])
        ax_rebuild = plt.axes([left_start + 2*(button_width + 0.1), 0.05, button_width, button_height])
        
        self.btn_prev = Button(ax_prev, '<- Пред.')
        self.btn_next = Button(ax_next, 'След. ->')
        self.btn_rebuild = Button(ax_rebuild, 'Перестроить')
        self.btn_prev.on_clicked(self.prev_path)
        self.btn_next.on_clicked(self.next_path)
        self.btn_rebuild.on_clicked(self.rebuild_graph)
        
        # Инициализируем позиции вершин как None (будут вычислены при первом построении)
        self.pos = None
        self.seed = 42  # Начальное значение seed для воспроизводимости
        
        # Подготовка данных для путей
        self.prepare_paths_data()
        self.draw_graph()
    
    def prepare_paths_data(self):
        self.paths_info = []
        #создадим палитру цветов
        colors = plt.cm.tab10.colors
        
        for idx, path_expr in enumerate(self.hamilton_paths):
            if isinstance(path_expr, sp.Mul):
                path_symbols = path_expr.args
            else:
                path_symbols = [path_expr]
            
            vertex_indices = [ord(str(s)) - ord('a') for s in path_symbols]
            path_names = [f'a{i+1}' for i in vertex_indices]
            
            path_edges = [(path_names[i], path_names[i+1]) for i in range(len(path_names)-1)]
            
            total_weight = sum(self.C[vertex_indices[i], vertex_indices[i+1]] 
                          for i in range(len(vertex_indices)-1))
            
            self.paths_info.append({
                'names': path_names,
                'edges': path_edges,
                'weight': int(total_weight),
                'color': colors[idx % len(colors)],
                'path_str': '-'.join(path_names)
            })
    
    def draw_graph(self):
        self.ax.clear()
        
        G = nx.DiGraph()
        vertices = [f'a{i+1}' for i in range(self.R.shape[0])]
        G.add_nodes_from(vertices)
        
        # Добавляем дуги
        edge_labels = {}
        for i in range(self.R.shape[0]):
            for j in range(self.R.shape[1]):
                if self.R[i,j] == 1:
                    from_vertex = f'a{i+1}'
                    to_vertex = f'a{j+1}'
                    weight = int(self.C[i,j])
                    G.add_edge(from_vertex, to_vertex, weight=weight)
                    edge_labels[(from_vertex, to_vertex)] = weight
        
        # Если позиции еще не вычислены, вычисляем и сохраняем их
        if self.pos is None:
            self.pos = nx.spring_layout(G, seed=self.seed)  # Фиксируем seed для воспроизводимости
        
        # Цвета и толщина ребер
        edge_colors = []
        edge_widths = []
        for edge in G.edges():
            if edge in self.paths_info[self.current_path]['edges']:
                edge_colors.append(self.paths_info[self.current_path]['color'])
                edge_widths.append(3)
            else:
                edge_colors.append('gray')
                edge_widths.append(1)
        
        # Рисуем граф с фиксированными позициями
        nx.draw_networkx_nodes(G, self.pos, node_color='lightblue', node_size=1200, ax=self.ax)
        nx.draw_networkx_edges(G, self.pos, edge_color=edge_colors, width=edge_widths, 
                             arrows=True, arrowsize=25, ax=self.ax)
        nx.draw_networkx_labels(G, self.pos, font_size=14, font_weight='bold', ax=self.ax)
        nx.draw_networkx_edge_labels(G, self.pos, edge_labels=edge_labels, 
                                   font_size=12, font_color='black', ax=self.ax)
        
        # Отображаем информацию о текущем пути (переносим текст выше)
        path_info = self.paths_info[self.current_path]
        self.ax.set_title(f"Гамильтонов путь {self.current_path+1}/{len(self.paths_info)}", 
                         pad=20, fontsize=14)
        self.ax.text(0.5, 0.02,
                    f"Путь: {path_info['path_str']}\nВес: {path_info['weight']}",
                    ha='center', va='center', transform=self.fig.transFigure,
                    bbox=dict(facecolor='white', alpha=0.8), fontsize=12)
        
        self.ax.axis('off')
        plt.draw()

    def next_path(self, event):
        self.current_path = (self.current_path + 1) % len(self.paths_info)
        self.draw_graph()
    
    def prev_path(self, event):
        self.current_path = (self.current_path - 1) % len(self.paths_info)
        self.draw_graph()
    
    def rebuild_graph(self, event):
        # Изменяем seed для получения новой конфигурации
        self.seed = np.random.randint(0, 10000)
        self.pos = None
        self.draw_graph()


def visualize_ham_paths_interactive(R, C, hamilton_paths):
    visualizer = PathVisualizer(R, C, hamilton_paths)
    plt.show()




def visualize_ham_path(R, C, best_path_symbols):
        # Конвертируем символьный путь в индексы и названия вершин
        vertex_indices = [ord(str(s)) - ord('a') for s in best_path_symbols.args]
        best_path_names = [f'a{i+1}' for i in vertex_indices]
        
        # Создаем список ребер пути для подсветки
        best_path_edges = []
        for i in range(len(best_path_names)-1):
            best_path_edges.append((best_path_names[i], best_path_names[i+1]))
        
        # Вычисляем суммарный вес пути
        total_weight = 0
        for i in range(len(vertex_indices)-1):
            from_idx = vertex_indices[i]
            to_idx = vertex_indices[i+1]
            total_weight += C[from_idx, to_idx]
        
        # Создаем граф
        G = nx.DiGraph()
        vertices = [f'a{i+1}' for i in range(R.shape[0])]
        G.add_nodes_from(vertices)
        
        # Добавляем дуги с весами
        edge_colors = []
        edge_labels = {}
        for i in range(R.shape[0]):
            for j in range(R.shape[1]):
                if R[i,j] == 1:
                    from_vertex = f'a{i+1}'
                    to_vertex = f'a{j+1}'
                    weight = int(C[i,j])  # Преобразуем вес в целое число
                    G.add_edge(from_vertex, to_vertex, weight=weight)
                    edge_labels[(from_vertex, to_vertex)] = weight  # Используем целое число
                    
                    # Определяем цвет дуги
                    if (from_vertex, to_vertex) in best_path_edges:
                        edge_colors.append('#1f77b4')
                    else:
                        edge_colors.append('gray')
        
        # Визуализация
        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(G)
        
        # Рисуем элементы графа с увеличенными размерами
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=1200)
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True, arrowsize=25, width=2)
        nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold') 
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=16, font_color='black') 
        
        # Формируем строку пути для вывода
        path_str = '-'.join(best_path_names)
        
        # Выводим информацию о пути
        plt.text(0.5, -0.1, 
                f"Полученное ранжирование: {path_str}\nСуммарный вес: {int(total_weight)}", 
                ha='center', va='center', transform=plt.gca().transAxes,
                bbox=dict(facecolor='white', alpha=0.8), fontsize=12)
        
        plt.title("Орграф с Гамильтоновым путём максимальной длины", pad=20, fontsize=14)
        plt.axis('off')
        plt.tight_layout()
        plt.show()




def visualize_vertex_index_graph(R_sp, C_np, Vindx, link):
    # Конвертируем sympy.Matrix в numpy.array
    R = np.array(R_sp.tolist(), dtype=int)
    
    # Создаем граф
    G = nx.DiGraph()
    vertices = [f'a{i+1}' for i in range(R.shape[0])]
    G.add_nodes_from(vertices)
    
    # Добавляем дуги с весами
    edge_labels = {}
    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            if R[i,j] == 1:
                from_vertex = f'a{i+1}'
                to_vertex = f'a{j+1}'
                weight = int(C_np[i,j])
                G.add_edge(from_vertex, to_vertex, weight=weight)
                edge_labels[(from_vertex, to_vertex)] = weight
    
    # Визуализация
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    
    nx.draw_networkx_nodes(G, pos, node_size=1000, node_color='lightblue')
    nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold')
    nx.draw_networkx_edges(G, pos,  edge_color='gray', arrows=True, arrowsize=20, width=1.5)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=16)
    
    # Формируем ранжирование
    ranking = []
    current_group = [f'a{link[0]+1}']
    current_val = Vindx[link[0]]
    
    for i in range(1, len(link)):
        if np.isclose(Vindx[link[i]], current_val):
            current_group.append(f'a{link[i]+1}')
        else:
            ranking.append(', '.join(current_group))
            current_group = [f'a{link[i]+1}']
            current_val = Vindx[link[i]]
    
    ranking.append(', '.join(current_group))
    ranking_str = ' - '.join(ranking)
    
    plt.text(0.5, -0.1, 
             f"Порядок ранжирования:\n{ranking_str}",
             ha='center', transform=plt.gca().transAxes,
             bbox=dict(facecolor='white', alpha=0.8), fontsize=12)
    
    plt.title("Орграф с нестрогим ранжированием вершин", pad=20)
    plt.axis('off')
    plt.tight_layout()
    plt.show()