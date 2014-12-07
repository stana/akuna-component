Akuna Component
===============

Declarative component registration/lookup inspired by ZCA component architecture with a simple api allowing for great decoupling between component clients and components.


Best explained as an example:

    >>> class Bike(object): 
    ...     pass
    ...
    >>> class MountainBike(Bike): 
    ...     pass
    ...
    >>> class RoadBike(Bike): 
    ...     pass
    ...

    >>> class Request(object): 
    ...     pass
    ...

    >>> class View(object):
    ...     def render_view(self):
    ...         pass
    ...


Our View components:

    >>> from akuna.component import register_component
    ...


Some generic BikeView component (extending View):

    >>> @register_component(context=('Bike', 'Request'))
    ... class GenericBikeView(View):
    ...     def __init__(self, bike, request):
    ...         pass 
    ...         


A more specific MountainBikeView component:

    >>> @register_component(context=('MountainBike', 'Request'))
    ... class MountainBikeView(View):
    ...     def __init__(self, mountain_bike, request): 
    ...         pass
    ...


Some example context objects to test our component setup:

    >>> road_bike = RoadBike()
    >>> mountain_bike = MountainBike()
    >>> request = Request()
 

Finally component lookup to find most applicable component for a given context:

    >>> from akuna.component import query_component 
    >>>
    >>> query_component('View', context=(mountain_bike, request))
    <class '__main__.MountainBikeView'>


Similar query but for *RoadBike, Request* context. Note the Generic View component being returned as we don't have a specific *RoadBike* view component (RoadBike *is a* Bike and we have registered a generic Bike view):

    >>> query_component('View', context=(road_bike, request))
    <class '__main__.GenericBikeView'>


Components could also be registered using a component name, and without context. Or providing *is_a* argument to override type.  This could be useful when registering functions as components.  Usually we would search components by type (eg. *View*, *Factory*):

    >>> @register_component(is_a='Factory', name='mountainbike')
    ... def mountainbike_factory():
    ...     pass
    ...

Components could be objects:

    >>> class Factory(object): 
    ...     pass
    ...

    >>> class MyFactory(Factory): 
    ...     pass
    ...

    >>> my_factory = MyFactory()
    >>> register_component(my_factory)
    ...

Factory component search will return MyFactory instance:

    >>> query_component('Factory')      #doctest: +ELLIPSIS
    <__main__.MyFactory object at ...>


More specific search by *component name*:

    >>> query_component('Factory', name='mountainbike')     #doctest: +ELLIPSIS   
    <function mountainbike_factory ...>


You could instantiate a component when looking it up. Context objects will be passed to the component as constructor args:

    >>> query_component('View', context=(road_bike, request), instantiate=True)   #doctest: +ELLIPSIS
    <__main__.GenericBikeView object at ...>


If component not found, query_component will return *None*. **get_component** could be used in exactly the same way as query_component but error will be thrown if component not found:

    >>> from akuna.component import get_component
    >>> get_component('Factory', name='blah')       #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ComponentDoesNotExist:...


Django Update View form hook example
------------------------------------

This simple example extends Django's Update View to add a form class component hook. Form classes registered by content model name of the object being updated.

    from django.views.generic.edit import UpdateView

    class UpdateViewWithFormHook(UpdateView):
        def get_form_class(self):
            obj_to_upd = self.get_object()
            content_model_name = obj_to_upd._meta.model_name
            if not self.form_class:
                try:
                    # our form hook
                    self.form_class = query_component('Form', name=content_model_name)
                except ComponentDoesNotExist:
                    # fallback to some generic form 
                    self.form_class = modelform_factory(obj_to_upd.__class__)

            return super(UpdateViewWithFormHook, self).get_form_class()


Just register a few forms which will plug into the above view based on the model_name of the object being updated.

    @register_component(name='customer')
    class CustomerForm(forms.Form):
        pass  
 
    @register_component(name='cartitem')
    class CartItemForm(forms.Form):
        pass
