!pip install openmeteo_requests
import openmeteo_requests
import datetime

class IncreaseSpeed():
  def __init__(self, current_speed: int, max_speed: int):
    self.current = current_speed
    self.max=max_speed
  def __iter__(self):
    return self
  def __next__(self):
    self.current += 10
    if self.current == self.max:
      #print("Maximum speed is reached")
      return self.current
    else:
      if self.current <= self.max:
        return self.current
      raise StopIteration
      

class DecreaseSpeed():
  def __init__(self, current_speed: int, target_speed=0):
    self.current = current_speed
    self.target = target_speed
    #self.min == 0
  def __iter__(self):
    return self
  def __next__(self):
    self.current -= 10
    if self.current == 0:
      #print("Minimum speed is reached. Car is stopped")
      return self.current
    else:
      while self.current > 0:
        return self.current
      raise StopIteration

class Car():

  cars = 0

  def __init__(self, max_speed: int, current_speed=0):
    self.current = current_speed
    self.max = max_speed
    if current_speed<0:
      print("Wrong speed value - number should be greater than 0")
    if current_speed>0:
      self.state = "On the road"
      Car.cars +=1
    else:
      self.state = "Off the road"

  def accelerate(self, upper_border=None):
    if self.state == "Off the road":
      Car.cars+=1
      self.state = "On the road"
    if self.current == self.max:
      print('Maximum speed is reached')
      return
    else:
      if upper_border != None:
        if upper_border<=0:
          print("Wrong speed value - number should be greater than 0")
          return
        if self.current > upper_border:
          print(f"Oops! Current speed is greater than {upper_border} km/h! If you want to decrease speed use 'brake' button instead")
          return
        if upper_border>self.max:
          print(f"Can't ride so fast! Maximum speed is {self.max} km/h!")
          return
        else:
          acceleration = IncreaseSpeed(self.current, upper_border)
          while self.current < upper_border:
            self.current = next(acceleration)
            print(f"Driving at {self.current} km/h")
      else:
        acceleration = IncreaseSpeed(self.current, self.max)
        self.current = next(acceleration)
        return f'Speed increased up to {self.current} km/h'

  def brake(self, lower_border=None):
    if self.current == 0:
      print('Speed is 0 km/h')
      return
    else:
      if lower_border !=None:
        if lower_border<0:
          print("Wrong speed value - number should be greater than 0")
          return
        if lower_border>self.current:
          print(f"Oops! Current speed is less than {lower_border} km/h! If you want to increase speed use 'accelerate' button instead")
          return
        else:
          braking=DecreaseSpeed(self.current, lower_border)
          while self.current > lower_border:
            self.current = next(braking)
            print(f"Driving at {self.current} km/h")
      else:
        braking = DecreaseSpeed(self.current)
        self.current = next(braking)
        return f'Speed decreased down to {self.current} km/h'

  def parking(self):
    if self.state == "Off the road":
      return
    Car.cars -= 1
    self.current=0
    self.state = "Off the road"
    print(f'Car is parked')

  @classmethod
  def total_cars(cls):
    print(f'There are {Car.cars} on the road')

  @staticmethod
  def show_weather():
    openmeteo = openmeteo_requests.Client()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
    "latitude": 33.8688, #Sydney 
    "longitude": 151.2093,
    "current": ["temperature_2m", "apparent_temperature", "rain", "wind_speed_10m"],
    "wind_speed_unit": "ms",
    "timezone": "Australia/Sydney"
    }

    response = openmeteo.weather_api(url, params=params)[0]

    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_apparent_temperature = current.Variables(1).Value()
    current_rain = current.Variables(2).Value()
    current_wind_speed_10m = current.Variables(3).Value()

    print(f"Current time: {datetime.datetime.fromtimestamp(current.Time()+response.UtcOffsetSeconds())} {response.TimezoneAbbreviation().decode()}")
    print(f"Current temperature: {round(current_temperature_2m, 0)} C")
    print(f"Current apparent_temperature: {round(current_apparent_temperature, 0)} C")
    print(f"Current rain: {current_rain} mm")
    print(f"Current wind_speed: {round(current_wind_speed_10m, 1)} m/s")