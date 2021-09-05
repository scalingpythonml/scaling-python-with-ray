class BaseTemperatureController:
    def __init__(self, id: str):
        self.currentSetting = None
        self.previousCommand = -1
        self.id = id

    # Process new message
    def process_new_message(self, message: dict):
        if 'measurement' in message:    # measurement request
            self.process_sensordata(message)
        else:                           # temp set request
            self.set_temperature(message)

    # set new temperature
    def set_temperature(self, setting: dict):
        desired = setting['temperature']
        updelta = setting['up_delta']
        downdelta = setting['down_delta']
        print(f'Controller {self.id} new temperature setting {desired} up delta {updelta} down delta {downdelta}')
        self.currentSetting = desired
        self.upDelta = updelta
        self.downDelta = downdelta

    # Process new measurements
    def process_sensordata(self, sensor: dict) ->bool:
        if self.currentSetting is not None:           # desired temperature is set, otherwise ignore
            # calculate desired action
            measurement = sensor['measurement']
            action = -1
            if measurement > (self.currentSetting + self.upDelta):
                action = 1
            if measurement < (self.currentSetting - self.downDelta):
                action = 0
            if action >= 0 and self.previousCommand != action:  # new action
                self.previousCommand = action
                # publish new action to kafka
                return True
            else:
                return False
        else:
            return False