
class gradient():
    def __init__(self, maxMin, gradientInfo):
        self.maxMin = maxMin
        self.valueRange = (self.maxMin[1] - self.maxMin[0])
        self.gradientInfo = gradientInfo
    
    def GetValue(self, value):
        return (value-self.maxMin[0])/self.valueRange
    
    def GetColorAtPoint(self, value):
        value = self.GetValue(value)
        