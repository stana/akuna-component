import sys, os

def _component_backend_module():
    module_name = os.environ.get('AKUNA_COMPONENT_BACKEND') or 'akuna.component.backends.basic'
    __import__(module_name)
    return sys.modules[module_name]

def register_comp(*args, **kwargs):
    component_mod = _component_backend_module()
    component_mod.register_comp(*args, **kwargs)

def register_component(*args, **kwargs):
    if args:
        # register_comp does not take args (only kwargs) so args will only
        # contain <component> being registered if
        #    - @register_component  decorator without arguments  OR
        #    - direct call to register_component(<comp>, ...)
        register_comp(*args, **kwargs)
        return
    def wrapped_component(component):
        register_comp(component, *args, **kwargs)
        return component
    return wrapped_component

def query_component(*args, **kwargs):
    component_mod = _component_backend_module()
    return component_mod.query_component(*args, **kwargs)

def get_component(*args, **kwargs):
    component_mod = _component_backend_module()
    return component_mod.get_component(*args, **kwargs)

def filter_components(*args, **kwargs):
    component_mod = _component_backend_module()
    return component_mod.filter_components(*args, **kwargs)
