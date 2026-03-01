from math import sqrt

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def Magnetude(self) -> float:
        return sqrt((self.x ** 2) + (self.y ** 2))
    
    def ConvertToCord(self):
        return (self.x, self.y)
    
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
        
    def __bool__(self):
        pass
        
    def __repr__(self) -> str:
        return f"({round(self.x, 5)}, {round(self.y, 5)})"