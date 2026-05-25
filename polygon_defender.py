from dataclasses import dataclass
from typing import List
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MatplotPolygon

@dataclass
class Point:
    x: float =0.0
    y: float = 0.0

@dataclass
class Edge:
    p1: Point
    p2: Point

@dataclass
class Triangle:
    a: Point
    b: Point
    c: Point

@dataclass
class Polygon:
    vertices: List[Point]

def load_polygon() -> Polygon:
    pass

def is_simple(p: Polygon) -> bool:
    pass


def triangulate(p: Polygon) -> List[Triangle]:
    pass


def place_guards(triangles: List[Triangle]) -> List[Point]:
    pass


def is_visible(guard: Point, intruder: Point, p: Polygon) -> bool:
    pass





#--------------------PRZECINANIE ODCINKÓW------------------------
def point_placement(A:Point, B:Point, C:Point) -> bool:
    return (C.y - A.y)* (B.x -A.x) > (B.y -A.y)*(C.x -A.x)

#zwraca true, jak odcinki się przecinają
def intersect(A:Point, B:Point, C:Point, D:Point) ->bool:
    return point_placement(A, C, D) !=point_placement(B, C, D) and point_placement(A,B,C) != point_placement(A, B,D)

#widoczność
def is_visible(guard: Point, intruder: Point, p:Polygon)->bool:
    n= len(p.vertices)

    for i in range(n):
        p1 = p.vertices[i]
        p2=p.vertices[(i+1)% n] #% n pozwala nam połączyć ostatni punkt z pierwszym

        if intersect(guard, intruder, p1, p2):
            return False # nie widać intruza
        
    return True # nic nie zablokowalo wzroku wiec untruz jest widoczny

#-------------WIZUALIZACJA------------------
def draw_gallery(polygon_data: Polygon, guard:Point):
    fig, ax = plt.subplots(figsize=(8, 6))
    plt.subplots_adjust(bottom=0.2)

    points = [[pt.x, pt.y] for pt in polygon_data.vertices]

    poly_patch = MatplotPolygon(points, closed=True, fill=True, color='lightgray', ec='black')
    ax.add_patch(poly_patch)

    ax.plot(guard.x, guard.y, 'bo', markersize=8, label="Strażnik")
    intruder_plot, = ax.plot([], [], 'ro', markersize=8, label="Intruz")
    los_line, = ax.plot([], [], 'g-', lw=2, alpha=0.7) # Line of Sight
    status_text = ax.text(0.5, -0.15, '', transform=ax.transAxes, ha='center', fontsize=12, fontweight='bold')
    
    # Ustawienia osi
    all_x = [p.x for p in polygon_data.vertices] + [guard.x]
    all_y = [p.y for p in polygon_data.vertices] + [guard.y]
    ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
    ax.set_ylim(min(all_y) - 1, max(all_y) + 1)
    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    ax.set_title("Polygon Defender: Test Widoczności", fontsize=14)
   
   
    def on_click(event):
        if event.xdata is None or event.ydata is None: return # Kliknięcie poza osiami

        intruder = Point(event.xdata, event.ydata)
        intruder_plot.set_data([intruder.x], [intruder.y])
        # Sprawdzanie widoczności
        visible = is_visible(guard, intruder, polygon_data)

        los_line.set_data([guard.x, intruder.x], [guard.y, intruder.y])
        if visible:
            status_text.set_text("STATUS: ZŁAPANY ")
        else:
           status_text.set_text("STATUS: UKRYTY ")
            
        fig.canvas.draw_idle()

    # Podpięcie zdarzenia kliknięcia myszką do wykresu
    cid = fig.canvas.mpl_connect('button_press_event', on_click)
    
    plt.show()

if __name__ == "__main__":
    # punktu testowe
    mock_vertices = [
        Point(0, 0), Point(10, 0), Point(10, 3), Point(3, 3), 
        Point(3, 10), Point(0, 10)
    ]
    my_gallery = Polygon(vertices=mock_vertices)
    
    # Stawiamy strażnika 
    my_guard = Point(1, 1)
    
    draw_gallery(my_gallery, my_guard)