import sys, os

def _component_backend_module():
    module_name = os.environ.get('AKUNA_COMPONENT_BACKEND') or 'akuna.component.backends.basic'
    __import__(module_name)
    return sys.modules[module_name]

def register_component(*args, **kwargs):
    component_mod = _component_backend_module()
    component_mod.register_component(*args, **kwargs)

def query_component(*args, **kwargs):
    component_mod = _component_backend_module()    
    return component_mod.query_component(*args, **kwargs)

def get_component(*args, **kwargs):
    component_mod = _component_backend_module()    
    return component_mod.get_component(*args, **kwargs)

def filter_components(*args, **kwargs):
    component_mod = _component_backend_module()    
    return component_mod.filter_components(*args, **kwargs)
