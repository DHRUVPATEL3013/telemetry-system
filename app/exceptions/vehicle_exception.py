class VehicleDoesNotExist(Exception):
  pass
class VehicleAlreadyExist(Exception):
  pass
class CurrentStateNotFound(Exception):
  pass
class NoAlertsFound(Exception):
  pass
class ActiveDeviceAlreadyExists(Exception):
  pass
class NoActiveDeviceToReplace(Exception):
  pass