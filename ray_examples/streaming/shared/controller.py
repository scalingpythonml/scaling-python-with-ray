#tag::shared[]
class BaseTemperatureController:
    def __init__(self, id: str):
        self.current_setting = None
        self.previous_command = -1
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
        print(f'Controller {self.id} new temperature setting {desired} up delta {updelta} '
              f'down delta {downdelta}')
        self.current_setting = desired
        self.up_delta = updelta
        self.down_delta = down_delta

    # Process new measurements
    def process_sensordata(self, sensor: dict) ->bool:
        if self.current_setting is not None:           # desired temperature is set, otherwise ignore
            # calculate desired action
            measurement = sensor['measurement']
            action = -1
            if measurement > (self.current_setting + self.up_delta):
                action = 1
            if measurement < (self.current_setting - self.down_delta):
                action = 0
            if action >= 0 and self.previous_command != action:  # new action
                self.previous_command = action
                # publish new action to kafka
                return True
            else:
                return False
        else:
            return False
#end::shared[]
