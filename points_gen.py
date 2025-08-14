import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import freud # для создания диаграммы Вороного
import networkx as nx # для создания матрицы смежности

def generate_points(N):
    points = np.vstack((np.random.uniform(0, 1, N, ), np.random.uniform(0, 1, N))).T # generate uniformly distributed points in [0,1]^2
    points = np.hstack((points, np.zeros((N, 1)))) # add z=0 component for freud
    box = freud.box.Box(Lx=1, Ly=1, is2D=True)
    points = box.wrap(points)
    return box, points

def normalization(coord): # нужно закодировать каждую вершину, желательно убирая эффекты арифметики с плавающей точкой
    x = coord[0]
    if x < -0.5:
        x += 1.
    elif x > 0.5:
        x -= 1.
    y = coord[1]
    if y < -0.5:
        y += 1.
    elif y > 0.5:
        y -= 1.
    return (str(round(x, 8)) + " " + str(round(y, 8))) # для этого я храню координаты как строки с заранее заданной точностью 
                                                       # (если есть ошибка, можно пропустить и не парить мозги)
    
def get_vertices(cells): # нужно получить список вершин, чтобы потом обращаться к нему и записывать ребра
    vertices = np.concatenate(cells)
    vertices2 = np.asarray([normalization(x) for x in vertices])
    return {x: i for i,x in enumerate(sorted(vertices2)[::3])} # здесь использую, что графы получаются 3-регулярными, если не получился, то undefined behaviour ИСПРАВИТЬ

def transform(cells): # функция сделана для удобства
    ans = []
    for cell in cells:
        ans.append([normalization(x) for x in cell])
    return ans

def get_edges(vertices, transformed_cells): # собираю список ребер, из которого потом получим граф
    edges = []
    for cell in transformed_cells:
        cell = cell.copy()
        l = len(cell)
        cell.append(cell[0])
        for i in range(l):
            edge = (vertices.get(cell[i]), vertices.get(cell[i+1]))
            edges.append(edge)
    return edges # не смотрели на повторы ребер, но потом матрица смежности их не учитывает

def voronoi_adjacency_matrix(N, return_nx_graph = False, draw = False): # засунул все в одну функцию
    box, points = generate_points(N)
    voro = freud.locality.Voronoi()

    cells = voro.compute((box, points)).polytopes

    vertices = get_vertices(cells)
    transformed_cells = transform(cells)
    
    edgelist = get_edges(vertices, transformed_cells)
    G = nx.Graph(edgelist)
    A = nx.adjacency_matrix(G)
    
    ans = A.toarray()
    
    if draw:
        nx.draw(G, with_labels=True) # нарисовать граф, скорее всего не нужно
    
    if np.all( ans.sum(axis = 0) == 3 ): # проверка, что граф 3-регулярный
        return (G if return_nx_graph else A.toarray()) # возвращает матрицу смежности, но можно возвращать и графы
    else: 
        return None