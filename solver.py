from algorithms import *
from PathVisualizer import *

import numpy as np
from tkinter import  messagebox

def solve(values, method):

    def Experts_matrix(values):
        experts_list = np.zeros((n_experts, n_alternatives, n_alternatives))  #(количество_матриц, строки, столбцы)
        for ExpertS in range(n_experts):
            ranking = values[:, ExpertS]
            for i in range(len(ranking)-1):
                stroka = ranking[i] - 1                     # номер строки м-цы. смеж. эксперта, которую будем заполнять щас
                for j in range(i+1, len(ranking)):
                    stolbec = ranking[j]-1                  # номер столбца м-цы. смеж. эксперта, которую будем заполнять щас
                    experts_list[ExpertS, stroka, stolbec] = 1  
        return experts_list


    def PRCmatrix(experts_list):
        P = np.sum(experts_list, axis=0)
        R = np.zeros((n_alternatives, n_alternatives))
        C = np.zeros((n_alternatives, n_alternatives))
        #тут будем находить R
        alfa = n_experts / 2
        for i in range(n_alternatives):
            for j in range(n_alternatives):
                if P[i][j] >= alfa:
                    R[i][j] = 1
        #далее находим матрицу весов
        for i in range(n_alternatives):
            for j in range(i, n_alternatives):
                if i==j:
                    C[i][j]=np.inf
                elif P[i][j] < P[j][i]:
                    C[j][i] = np.abs(P[i][j]-P[j][i])
                    C[i][j] = np.inf
                elif P[i][j] > P[j][i]:
                    C[i][j] = np.abs(P[i][j]-P[j][i])
                    C[j][i] = np.inf
                else:
                    C[i][j] = C[j][i] = np.inf
        return P, R, C


    def Hamilton_paths(R_):     #находит все Гам-новы пути в орграфе
        n = R_.rows
        H = create_H_matrix(R_)
        Rpred = R_
        for i in range(2, n):
            R_shtrih = H*Rpred
            Rbud = filter_matrix(R_shtrih)
            Rpred = Rbud

        row_symbols = [sp.symbols(chr(ord('a') + k), commutative = False) for k in range(n)]
        col_symbols = row_symbols
        paths = []

        for i in range(n):
            for j in range(n):
                elem = Rbud[i, j]
                
                # Пропускаем нулевые элементы
                if elem == 0:
                    continue
                    
                # Получаем символы строки и столбца
                row_sym = row_symbols[i]
                col_sym = col_symbols[j]
                
                if isinstance(elem, sp.Add):
                    for term in elem.args:
                        path = [row_sym] + list(term.args) + [col_sym]
                        paths.append(sp.Mul(*path))
                elif isinstance(elem, sp.Mul):
                    path = [row_sym] + list(elem.args) + [col_sym]
                    paths.append(sp.Mul(*path))
                else:
                    path = [row_sym] + [elem] + [col_sym]
                    paths.append(sp.Mul(*path))
        return paths



    def find_max_weight_path(paths, C):
        max_weight = 0
        best_path = None
        best_dist_Ham = 0

        for path in paths:      #paths = [d*c*b*a]
            # Преобразуем символьный путь в индексы вершин
            vertex_indices = [ord(str(symbol)) - ord('a') for symbol in path.args]  #[3,2,1,0]

            # Вычисляем суммарный вес пути
            total_weight = 0
            for i in range(len(vertex_indices)-1):
                from_vertex = vertex_indices[i]
                to_vertex = vertex_indices[i+1]
                total_weight += C[from_vertex, to_vertex]
        
            # Сравниваем с текущим максимумом
            if total_weight > max_weight:
                max_weight = total_weight
                best_path = path

                rankM = list_to_spMatrix(vertex_indices)
                best_dist_Ham = sum_dist_Hamming(experts_list, rankM)

            elif total_weight == max_weight:
                rankM = list_to_spMatrix(vertex_indices)
                act_dist_Ham = sum_dist_Hamming(experts_list, rankM)
                if act_dist_Ham < best_dist_Ham:
                    best_path = path
                    best_dist_Ham = act_dist_Ham

        return best_path
    

    def index_vertex(P):
        Vindx = np.array([])
        row_sums = np.sum(P, axis=1)
        col_sums = np.sum(P, axis=0)
        Vindx = row_sums - col_sums
        Link = np.argsort(-Vindx)   #индексы элементов массива в п. убывания

        ll = len(Link)
        Rindx = sp.zeros(ll)
        for i in range(ll):
            for j in range(i+1, ll):
                if Vindx[Link[i]] > Vindx[Link[j]]:
                    Rindx[Link[i], Link[j]] = 1
                elif Vindx[Link[i]] == Vindx[Link[j]]:
                    Rindx[Link[i], Link[j]] = 1
                    Rindx[Link[j], Link[i]] = 1

        return Vindx, Link, Rindx



 #=============================================================================#

    n_experts = values.shape[1] #5
    n_alternatives = values.shape[0] #4

    if method==1:                                #Гамильтоновы пути
        experts_list = Experts_matrix(values)
        P, R, C = PRCmatrix(experts_list)
        R_sp = sp.Matrix([[sp.Integer(val) for val in row] for row in R])
        hamilton_paths = Hamilton_paths(R_sp)

        if hamilton_paths == []:
            messagebox.showwarning("Предупреждение", "При таких данных не существует Гамильтоновых путей!\n Для данной задачи рекомендуется применить метод Индексированных вершин.")
        else:
            visualize_ham_paths_interactive(R,C, hamilton_paths)

    elif method==2:                              #Гамильтонов путь максимальной длины
        experts_list = Experts_matrix(values)
        P, R, C = PRCmatrix(experts_list)

        R_sp = sp.Matrix([[sp.Integer(val) for val in row] for row in R])
        hamilton_paths = Hamilton_paths(R_sp)
        best_path = find_max_weight_path(hamilton_paths, C)

        if hamilton_paths == []:
            messagebox.showwarning("Предупреждение", "При таких данных не существует Гамильтоновых путей!\n Для данной задачи рекомендуется применить метод Индексированных вершин.")
        else:
            visualize_ham_path(R,C, best_path)
        
    else:                                       #Индексирование вершин
        experts_list = Experts_matrix(values)
        P, R, C = PRCmatrix(experts_list)
        Vindx, Link, Rindx = index_vertex(P)    #[-3, -5, -3, 11] [3, 0, 2, 1] и м-ца смежности

        R_sp = sp.Matrix([[sp.Integer(val) for val in row] for row in R])
        hamilton_paths = Hamilton_paths(R_sp)
        best_path = find_max_weight_path(hamilton_paths, C)
        vertex_indices = [ord(str(symbol)) - ord('a') for symbol in best_path.args]
        R_bham = list_to_spMatrix(vertex_indices)

        if sum_dist_Hamming(experts_list, Rindx) > sum_dist_Hamming(experts_list, R_bham): 
            messagebox.showwarning("Предупреждение", "При использовании метода Индексирования вершин суммарное расстояние до экспертных предпочтений получается больше, чем у метода Гамильтонового пути максимальной длины.\n Для данной задачи рекомендуется применить метод Гамильтоного пути максимальной длины!")

        visualize_vertex_index_graph(Rindx, P, Vindx, Link)
            