from pygame import Vector2
points = [Vector2(1, 1), Vector2(2, 2), Vector2(2, 1)]

output = [[points[x], points[(x+1) % len(points)]] for x in range(len(points))]

print(output)