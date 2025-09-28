import sympy as sp


def create_H_matrix(R__):
    n = R__.rows
    # Создаем список символов для вершин: [a, b, c, ...]
    vertex_symbols = [sp.symbols(chr(ord('a') + i), commutative = False) for i in range(n)]  # commutative = False
    
    H = sp.zeros(n)  # Создаем нулевую матрицу n x n
    
    for i in range(n):
        for j in range(n):
            if int(R__[i, j]) == 1:
                H[i, j] = vertex_symbols[j]  # Заменяем 1 на букву, соответствующую столбцу
            else:
                H[i, j] = 0
    
    return H

def filter_matrix(M):
    n = M.rows
    filtered_M = M.copy()
    
    for i in range(n):
        current_row_sym = sp.symbols(chr(ord('a') + i), commutative=False)  # Символ текущей строки
        
        for j in range(n):
            # 1. Обнуляем диагональные элементы
            if i == j:
                filtered_M[i, j] = 0
                continue
            
            elem = filtered_M[i, j]
            
            # Пропускаем нулевые элементы
            if elem == 0:
                continue
            else:
                elem = sp.expand(elem)
            
            # 2. Обрабатываем элементы в зависимости от их типа
            if isinstance(elem, sp.Add):
                valid_terms = []
                for term in elem.args:
                    # Проверяем, содержится ли символ строки в слагаемом
                    if current_row_sym not in term.free_symbols:
                        valid_terms.append(term)
                
                # Обновляем элемент
                if valid_terms:
                    filtered_M[i, j] = sp.Add(*valid_terms)
                else:
                    filtered_M[i, j] = 0
            else:
                if current_row_sym in elem.free_symbols:
                    filtered_M[i, j] = 0
    
    return filtered_M




def dist_Hamming(M1, M2):   # принимает и sp матрицы и np матрицы
    dist = 0
    for i in range(M1.shape[0]):
        for j in range(M1.shape[0]):
            dist += abs(M1[i, j] - M2[i, j])
    return dist


def sum_dist_Hamming(list, matrix):
    ans = 0
    for exMatrix in list:  
        ans += dist_Hamming(exMatrix, matrix)
    return ans





def list_to_spMatrix(list):     #принимает [3, 2, 1, 0]
    n = len(list)
    matrix = sp.zeros(n)
    
    for i in range(n):
        current_element = list[i]
        # Все элементы после current_element в ранжировании хуже него
        for j in range(i + 1, n):
            worse_element = list[j]
            matrix[current_element, worse_element] = 1  # worse_element хуже current_element
            
    return matrix
