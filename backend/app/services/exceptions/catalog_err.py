class DeviceAlreadyExistsError(Exception):
    """Устройство с таким (brand, type, name) уже существует."""
    pass

class DeviceNotFoundError(Exception):
    pass