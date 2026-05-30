import os
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
    """Prosi użytkownika o wybór poziomu i wczytuje punkty z pliku tekstowego."""
    print("Dostępne poziomy: 1, 2, 3")
    while True:
        level = input("Wybierz poziom (1-3): ").strip()
        filename = f"poziom{level}.txt"

        if level in ["1", "2", "3"]:
            if os.path.exists(filename):
                break
            else:
                print(f"[Błąd]: Nie znaleziono pliku '{filename}' w folderze programu!")
        else:
            print("[Błąd]: Nieprawidłowy wybór. Wpisz 1, 2 lub 3.")

    vertices = []
    print(f"Wczytywanie punktów z pliku: {filename}...")

    with open(filename, "r") as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            if not line:  # Pomiń puste linie
                continue
            try:
                x_str, y_str = line.split()
                pt = Point(float(x_str), float(y_str))
                vertices.append(pt)
            except ValueError:
                print(f"[Ostrzeżenie]: Ignoruję błędną linię {line_num}: '{line}'")

    return Polygon(vertices=vertices)

def is_simple(p: Polygon) -> bool:
    """Sprawdza, czy wielokąt jest prosty (brak samoprzecięć)."""
    n = len(p.vertices)
    if n < 3:
        return False

    for i in range(n):
        for j in range(i + 1, n):
            if abs(i - j) == 1 or abs(i - j) == n - 1:
                continue
            A, B = p.vertices[i], p.vertices[(i + 1) % n]
            C, D = p.vertices[j], p.vertices[(j + 1) % n]
            if intersect_for_validation(A, B, C, D):
                return False
    return True


def triangulate(p: Polygon) -> List[Triangle]:
    pass


def place_guards(triangles: List[Triangle]) -> List[Point]:
    pass


def is_visible(guard: Point, intruder: Point, p: Polygon) -> bool:
    pass

def fix_orientation(p: Polygon) -> Polygon:
    """Wymusza orientację przeciwną do wskazówek zegara (CCW)."""
    n = len(p.vertices)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += p.vertices[i].x * p.vertices[j].y
        area -= p.vertices[j].x * p.vertices[i].y

    if area < 0:
        print("[Orientacja]: Wykryto ruch zgodny z zegarem (CW). Odwracam na CCW.")
        p.vertices.reverse()
    else:
        print("[Orientacja]: Wykryto ruch przeciwny do zegara (CCW). Jest OK.")
    return p



# Funkcje pomocnicze do sprawdzania prostoty wielokąta
def point_placement(A: Point, B: Point, C: Point) -> bool:
    return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)

def intersect_for_validation(A: Point, B: Point, C: Point, D: Point) -> bool:
    if A == C or A == D or B == C or B == D:
        return False
    return point_placement(A, C, D) != point_placement(B, C, D) and point_placement(A, B, C) != point_placement(A, B, D)

#------------------TRIANGULACJA---------------------------------------


def cross(a: Point, b: Point, c: Point) -> float: 
  return ( (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x) )

def is_convex(a: Point, b: Point, c: Point) -> bool: 
  return cross(a, b, c) > 0

def point_in_triangle( p: Point, a: Point, b: Point, c: Point ) -> bool: 
  d1 = cross(a, b, p)
  d2 = cross(b, c, p) 
  d3 = cross(c, a, p) 
  has_negative = (d1 < 0) or (d2 < 0) or (d3 < 0)
  has_positive = (d1 > 0) or (d2 > 0) or (d3 > 0) 

  return not (has_negative and has_positive)

def is_ear( prev: Point, curr: Point, next: Point, vertices: List[Point] ) -> bool:
  if not is_convex(prev, curr, next):
     return False
  for p in vertices:
    if p in [prev, curr, next]:
       continue
    if point_in_triangle(p, prev, curr, next): 
      return False
    
  return True


def triangulate(p: Polygon) -> List[Triangle]:
  vertices = p.vertices[:]
  triangles = []

  while len(vertices) > 3: 
    ear_found = False 
    n = len(vertices)

    for i in range(n): 
      prev = vertices[(i - 1) % n] 
      curr = vertices[i] 
      next = vertices[(i + 1) % n]

      if is_ear(prev, curr, next, vertices):
        triangles.append( Triangle(prev, curr, next) )

        del vertices[i]
        ear_found = True
        break

    if not ear_found: 
      raise ValueError( "blad triangulacji brak ucha" )

  triangles.append( Triangle( vertices[0], vertices[1], vertices[2] ) )

  return triangles

#----------- STRAŻNICY --------------------------
def place_guards(triangles: List[Triangle]) -> List[Point]:
    """budowa grafu z trójkątów po triangulacji"""
    if not triangles:
        return []

    triangles_count=len(triangles)
    adj={i:[] for i in range(triangles_count)} #baza na graf
    for i in range(triangles_count):
        for j in range(i+1, triangles_count):
            t1={(triangles[i].a.x, triangles[i].a.y), (triangles[i].b.x, triangles[i].b.y), (triangles[i].c.x, triangles[i].c.y)}
            t2 = {(triangles[j].a.x, triangles[j].a.y), (triangles[j].b.x, triangles[j].b.y), (triangles[j].c.x, triangles[j].c.y)}
            if len(t1.intersection(t2))==2:
                adj[i].append(j)
                adj[j].append(i)

    point_map={} #żeby się nie dublowały
    for t in triangles:
        for p in [t.a, t.b, t.c]:
            point_map[(p.x, p.y)]=p

    colors={}
    #bazowy trojkat
    t0=triangles[0]
    colors[(t0.a.x, t0.a.y)]=0
    colors[(t0.b.x, t0.b.y)]=1
    colors[(t0.c.x, t0.c.y)]=2
    visited={0}
    stack=[0]

    while stack:
        curr=stack.pop()
        for neighbour in adj[curr]:
            if neighbour not in visited:
                visited.add(neighbour)
                temp=triangles[neighbour]

                temp_points=[temp.a,temp.b,temp.c]
                used_colors=set()
                uncolored_point=None

                for point in temp_points:
                    key=(point.x, point.y)
                    if key in colors:
                        used_colors.add(colors[key])
                    else:
                        uncolored_point=point

                if uncolored_point is not None:
                    all_colors={0,1,2}
                    free_color=list(all_colors-used_colors)[0]
                    colors[(uncolored_point.x, uncolored_point.y)]=free_color

                stack.append(neighbour)

    groups_by_color={0: [],1: [],2: []}
    for point_key, col in colors.items():
        groups_by_color[col].append(point_map[point_key])

    #wybor straznikow po min liczbie wierzcholkow danego koloru
    min_col=min(groups_by_color, key=lambda k: len(groups_by_color[k]))

    return groups_by_color[min_col]

#-------------WIZUALIZACJA------------------
def draw_gallery(polygon_data: Polygon, triangles: List[Triangle]):
    fig, ax = plt.subplots(figsize=(8, 6))
    plt.subplots_adjust(bottom=0.2)

    n = len(polygon_data.vertices)
    max_guards = n // 3 #limit latarni z twierdzenia fiska

    player_guards = []
    triangle_patches = []

#rysowaniw wnętrza 
    for t in triangles:
        pts = [[t.a.x, t.a.y], [t.b.x, t.b.y], [t.c.x, t.c.y]]
        poly_t = MatplotPolygon(pts, closed=True, fill=True, facecolor='gray', edgecolor='black', alpha=0.9)
        ax.add_patch(poly_t)
        triangle_patches.append((t, poly_t))

#rysowanie zewnętrza
    poly_points = [[pt.x, pt.y] for pt in polygon_data.vertices]
    outline_patch = MatplotPolygon(poly_points, closed=True, fill=False, ec='black', lw=3, zorder=3)
    ax.add_patch(outline_patch)

#latarnie
    guards_plot, = ax.plot([], [], 'yo', markersize=12, markeredgecolor='black', label="Twoje Latarnie", zorder=4)

    status_text = ax.text(0.5, -0.15, f"Postaw latarnie w rogach. Limit: {max_guards}",
                          transform=ax.transAxes, ha='center', fontsize=12, fontweight='bold')

    all_x = [p.x for p in polygon_data.vertices]
    all_y = [p.y for p in polygon_data.vertices]
    ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
    ax.set_ylim(min(all_y) - 1, max(all_y) + 1)
    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    ax.set_title("Oświetl Całą Galerię", fontsize=14)

    def on_click(event):
        if event.xdata is None or event.ydata is None:
            return

#tworzymy punkt w miejscu kliknięcia
        click_point = Point(event.xdata, event.ydata)
        closest_vertex = min(polygon_data.vertices,
                             key=lambda v: (v.x - click_point.x) ** 2 + (v.y - click_point.y) ** 2)

        dist_sq = (closest_vertex.x - click_point.x) ** 2 + (closest_vertex.y - click_point.y) ** 2
        if dist_sq > 0.5:
            status_text.set_text("Kliknij bliżej któregoś z rogów galerii!")
            fig.canvas.draw_idle()
            return

#dodawanie i usuwanie punktów
        vertex_key = (closest_vertex.x, closest_vertex.y)
        existing_keys = [(g.x, g.y) for g in player_guards]

        if vertex_key in existing_keys:
            idx = existing_keys.index(vertex_key)
            player_guards.pop(idx)
        else:
            if len(player_guards) >= max_guards:
                status_text.set_text(f"Wykorzystałeś limit {max_guards} latarni! Kliknij w istniejącą, by ją usunąć.")
                fig.canvas.draw_idle()
                return
            player_guards.append(closest_vertex)

        guards_plot.set_data([g.x for g in player_guards], [g.y for g in player_guards])

        oświetlone_trójkąty = 0
        active_keys = {(g.x, g.y) for g in player_guards}

        for t_geom, t_patch in triangle_patches:
            t_vertices = {(t_geom.a.x, t_geom.a.y), (t_geom.b.x, t_geom.b.y), (t_geom.c.x, t_geom.c.y)}

            if t_vertices.intersection(active_keys):
                t_patch.set_facecolor('yellow')  
                oświetlone_trójkąty += 1
            else:
                t_patch.set_facecolor('gray')  

        if oświetlone_trójkąty == len(triangles):
            status_text.set_text(f"BRAWO! Oświetliłeś galerię przy użyciu {len(player_guards)}/{max_guards} latarni.")
            status_text.set_color('green')
        else:
            status_text.set_text(
                f"Użyte latarnie: {len(player_guards)}/{max_guards}. Oświetlone: {oświetlone_trójkąty}/{len(triangles)} stref.")
            status_text.set_color('black')

        fig.canvas.draw_idle()

    cid = fig.canvas.mpl_connect('button_press_event', on_click)
    plt.show()


if __name__ == "__main__":
    my_gallery = load_polygon()

    if len(my_gallery.vertices) < 3:
        print("[Błąd]: Wielokąt musi mieć przynajmniej 3 wierzchołki!")
    else:
        if not is_simple(my_gallery):
            print("[Błąd]: Wielokąt nie jest prosty! Krawędzie przecinają się.")
        else:
            print("[Sukces]: Wielokąt z pliku jest prawidłowy (prosty).")

            # Sprawdzenie i korekta orientacji
            my_gallery = fix_orientation(my_gallery)

            try:
                #  Obliczenie trójkątów
                calculated_triangles = triangulate(my_gallery)
                print(f"[Sukces]: Triangulacja powiodła się. Liczba trójkątów: {len(calculated_triangles)}")
                    
                #  Uruchomienie właściwej rozgrywki
                draw_gallery(my_gallery, calculated_triangles)
                
            except ValueError as e:
                print(f"[Błąd Algorytmu]: {e}")
    # --------------------------------------------------------
   # triangles = triangulate(my_gallery)       #   triangulacja wywolanie <--------------------------------------
    # guards_positions=place_guards(triangles)
    #print("\n triangulacja test")
    #for i, t in enumerate(triangles, 1):
    #  print( f"Trójkąt {i}: " f"({t.a.x}, {t.a.y}) | " f"({t.b.x}, {t.b.y}) | " f"({t.c.x}, {t.c.y})" )
