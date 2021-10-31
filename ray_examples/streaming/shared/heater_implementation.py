import json

temperatureUpRate = 60      # sec
temperatureDownRate = 120   # sec

tempInterval = 10           # sec
controlInterval = 600       # sec

# Base Heater class
class BaseHeater:

    # initialize heater
    def __init__(self, id: str, current: float = 42.0, desired: float = 45.0,
                 upDelta: float = 1.0, downDelta: float = 1.0):

        self.id = id

        self.current = current
        self.desired = desired

        self.upDelta = upDelta
        self.downDelta = downDelta

        if(desired > current):
            self.command = 0
        else:
            self.command = 1

    # Submit current temperature
    def submit_temperature(self, timeInterval: int = tempInterval):
        # Update temperature
        if self.command == 0:   # Heater is on - increase temperature
            self.current = self.current + timeInterval/temperatureUpRate
        else:                   # Heater is off - decrease temperature
            self.current = self.current - timeInterval/temperatureDownRate


    # Process new controller command
    def process_control(self, msg):
        control = json.loads(msg.value().decode('UTF8'))
        self.command = control['control']
