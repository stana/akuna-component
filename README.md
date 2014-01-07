Akuna Component
===============

Simple component based development lib prototype for python allowing for a very decoupled design between client code using the components and components. 

Components could be registered by **type** they provide, **context** in which they operate and **name**. They could then be searched by these same parameteres. 

For example, a few content types:

    >>> class Bike(object): pass
    ... 
    >>> class MountainBike(Bike): pass
    ... 
    >>> class RoadBike(Bike): pass
    ... 


Parent view class:

    >>> class DetailView(object):
    ...     def render_view(self):
    ...         pass
    ... 


Some generic BikeView component (extending DetailView):

    >>> class GenericBikeView(DetailView):
    ...     pass
    ...


A more specific MountainBikeView component:

    >>> class MountainBikeView(DetailView):
    ...     pass
    ...


A dummy request:

    >>> class HttpRequest(object): pass
    ...


Now component registration:

    >>> from akuna.component import register_component
    ...
    >>> register_component(GenericBikeView,  context=('Bike',         'HttpRequest'))
    >>> register_component(MountainBikeView, context=('MountainBike', 'HttpRequest'))


And finally component lookup. First we will need some context objects:

    >>> road_bike = RoadBike()
    >>> mountain_bike = MountainBike()
    >>> request = HttpRequest()
    ...

    >>> from akuna.component import query_component 
    

Find most applicable component providing DetailView type in *mountain_bike, request* context.

    >>> query_component('DetailView', context=(mountain_bike, request))
    <class '__main__.MountainBikeView'>


Similar query but for *road_bike, request* context. NOTE the Generic View component being returned (registered for generic *Bike* type) as we don't have a specific *RoadBike* view component.

    >>> query_component('DetailView', context=(road_bike, request))
    <class '__main__.GenericBikeView'>


Components could also be registered using a component name, and without context.

    >>> class GenericFactory(object): pass
    ... 
    >>> class MountainBikeFactory(object): pass
    ... 

Components could be objects:

    >>> generic_factory = GenericFactory()

Or functions:

    >>> def mountainbike_factory():
    ...     pass


Could also 'cheat' and provide *is_a* string argument when registering so component classes don't have to extend some generic class.  This is also useful when registering functions as components.  Usually we would search components by this *is_a* type (eg. *DetailView*, *Factory*).

    >>> register_component(generic_factory,      is_a='Factory')
    >>> register_component(mountainbike_factory, is_a='Factory', name='mountainbike')


Generic Factory component search:

    >>> query_component('Factory')      #doctest: +ELLIPSIS
    <__main__.GenericFactory object at ...>


More specific search by *component name*:

    >>> query_component('Factory', name='mountainbike')     #doctest: +ELLIPSIS   
    <function mountainbike_factory ...>


filter_components returns a list of component, name dictionaries: 

    >>> from akuna.component import filter_components
    >>> filter_components('Factory')    #doctest: +ELLIPSIS
    [{'component': <__main__.GenericFactory object at ...>, 'name': ''}, {'component': <function mountainbike_factory ...>, 'name': 'mountainbike'}]


If component not found, query_component will return None. get_component could be used in exactly the same way as query_component but error will be thrown if component not found:

    >>> from akuna.component import get_component
    >>> get_component('Factory', name='blah')       #doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ComponentDoesNotExist: 'No Component Found for type: "Factory", context: (), name: "blah"'

