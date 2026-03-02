from math import sqrt
from random import randint
#Classes
 
class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def Magnetude(self) -> float:
        return sqrt((self.x ** 2) + (self.y ** 2))
    
    def ConvertToCord(self):
        return (self.x, self.y)
    
    @staticmethod
    def RandomVector(minX, minY, maxX, maxY):
        return Vector2(randint(minX, maxX), randint(minY, maxY))
    
    def __add__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x + other.x, self.y + other.y)
        elif type(other) == float or type(other) == int:
            return Vector2(self.x + other, self.y + other)
        else:
            raise TypeError(f"Vector2 cannot be added by {type(other)}")
        
    def __sub__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x - other.x, self.y - other.y)
        elif type(other) == float or type(other) == int:
            return Vector2(self.x - other, self.y - other)
        else:
            raise TypeError(f"Vector2 cannot be subtracted by {type(other)}")
        
    def __mul__(self, other):
        if type(other) == int or type(other) == float:
            return Vector2(self.x * other, self.y * other)
        else:
            raise TypeError("Vector2 can only be multiplied by scaler value")
        
    def __repr__(self) -> str:
        return f"({round(self.x, 5)}, {round(self.y, 5)})"
    
class Color:
    WHITE = (255, 255, 255)
    BLACK = (  0,   0,   0)
    RED =   (255,   0,   0)
    GREEN = (  0, 255,   0)
    BLUE =  (  0,   0, 255)

class GameObject:
    def __init__(self, initPosition: Vector2, initVelocity: Vector2, radius):
        self.position = initPosition
        self.velocity = initVelocity
        self.radius = radius

    def UpdatePosition(self, deltaTime):
        self.position += self.velocity * deltaTime

