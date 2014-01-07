class ComponentError(Exception):
    pass

class ComponentDoesNotExist(ComponentError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MultipleComponentsReturned(ComponentError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ComponentRegistrationError(ComponentError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ComponentFilterError(ComponentError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
