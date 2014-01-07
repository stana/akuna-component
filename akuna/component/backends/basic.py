from itertools import product
from inspect import isclass, isroutine
import timeit

from akuna.component import errors

import logging

logger = logging.getLogger('akuna.component')

COMPONENT_REGISTRY = {}
COMPONENT_CACHE = {}


def _entry_exists(reg_entry, component, name):
    for e in reg_entry:
        if e['component'] == component and e['name'] == name:
            return True

def _set_registry(key, component, context=(), name=''):
    context_key = ''.join(context)
    reg_entry = {'component': component, 'name': name}


    if COMPONENT_REGISTRY.has_key(key):
        if COMPONENT_REGISTRY[key].has_key(context_key):
            if not _entry_exists(COMPONENT_REGISTRY[key][context_key], component, name):
                COMPONENT_REGISTRY[key][context_key].append(reg_entry)
        else:
            COMPONENT_REGISTRY[key][context_key] = [ reg_entry, ]
    else:
        COMPONENT_REGISTRY[key] =  { context_key: [ reg_entry, ] }



def _create_registry_entry(is_a_list, component, context_clean=(), name=''):
    for is_a_str in is_a_list:
        key = is_a_str
        if name:
            key_with_name = key + ':' + name
            _set_registry(key_with_name, component, context_clean, name)
        else:
            _set_registry(key, component, context_clean, name)

        key_with_wildcard = key + '*'
        _set_registry(key_with_wildcard, component, context_clean, name)


def _clean_is_a(is_a):
    if type(is_a) == str:
        return is_a
    elif isclass(is_a):
        return is_a.__name__
    else:
        raise errors.ComponentError('is_a must be a Class or a String')


def register_component(component, context=(), is_a='', name=''):
    context_clean = []
    if context:
        for cls in context:
            if type(cls) == str:
                # just a class name string, add to key
                context_clean.append(cls) 
            elif isclass(cls):
                context_clean.append(cls.__name__)
            else:
                raise errors.ComponentRegistrationError('context must be Class or String iterable')

    is_a_list = []
    if is_a:
        is_a_list.append( _clean_is_a(is_a) )
    else:
        # no component 'is_a' type specified, inspect component 
        # and ancestor types and register using those
        component_mro_names = None 
        if isroutine(component):
            raise errors.ComponentRegistrationError('must provide "is_a" argument for function components')
        elif isclass(component):
            component_mro_names = [ cls.__name__ for cls in component.mro() ]
        elif hasattr(component, '__class__') and hasattr(component.__class__, 'mro'):
            component_mro_names = [ cls.__name__ for cls in component.__class__.mro() ]

        if 'object' in component_mro_names: 
            component_mro_names.remove('object')

        if component_mro_names:
            for cls_name in component_mro_names:
                is_a_list.append(cls_name)
        else:
            raise errors.ComponentRegistrationError('must provide "is_a" argument')

    _create_registry_entry(is_a_list, component, context_clean, name)


def _cls_or_obj_name(x):
    if isclass(x):
        return x.__name__
    else:
        return x.__class__.__name__


def _calc_cache_key(key, context, instantiate=False):
    cache_key = key
    if context:
        context_list = [_cls_or_obj_name(c) for c in context]
        cache_key += ':' + ':'.join(context_list) 
    #cache_key += ':' + str(instantiate)
    return cache_key


def _get_from_cache(cache_key):
    return COMPONENT_CACHE[cache_key]


def _set_cache(cache_key, entry):
    if not COMPONENT_CACHE.has_key(cache_key):
        COMPONENT_CACHE[cache_key] = entry


def _search_components_old(key, context=()):
    reg_items = COMPONENT_REGISTRY.get(key)
    logger.debug('key: "%s", got reg items: %s' % (key, reg_items))
    if not reg_items:
        return []
    if not context and key.endswith('*'):
        # non specific filter_component search
        return reg_items

    logger.debug('filtering by context')

    found_items = []
    # process context
    for item in reg_items:
        if len(context) != len(item['context']):
            continue
        found = True 
        i = 0
        for cls_str in item['context']:
            if isclass(context[i]):
                mro_names = [ c.__name__ for c in context[i].mro() ]
            else:
                mro_names = [ c.__name__ for c in context[i].__class__.mro() ]
            if not cls_str in mro_names:
                found = False
                break
            i += 1
        if found:
            found_items.append(item)
    return found_items


def _search_components(key, context=()):
    reg_items = COMPONENT_REGISTRY.get(key)
    logger.debug('key: "%s", got reg items: %s' % (key, reg_items))
    if not reg_items:
        return []
    if not context and key.endswith('*'):
        # non specific filter_component search
        # there is only one list of components {<context key>: [....]} 
        return reg_items.values()[0]

    logger.debug('filtering by context')

    context_classes = []
    for c in context:
        if isclass(c):
            context_classes.append(c)
        else:
            context_classes.append(c.__class__)

    context_mro = [ cls.mro() for cls in context_classes ]
    for mro_prod in product(*context_mro):
        prod_names = [ cls.__name__ for cls in mro_prod ]
        context_key = ''.join(prod_names)
        if reg_items.has_key(context_key):
            return reg_items[context_key]

    return []


def _filter_search(key, context=(), instantiate=False):
    logger.debug('key: "%s", context: %s, instantiate: %s' % (key, [_cls_or_obj_name(c) for c in context], instantiate))
    tic = timeit.default_timer()

    # try get component from cache
    cache_key = _calc_cache_key(key, context, instantiate)
    try:
        res = _get_from_cache(cache_key)
        logger.debug('found cached entry: "%s"' % cache_key)
    except KeyError:
        # perform component search
        res = _search_components(key, context)
        _set_cache(cache_key, res)

    if instantiate:
        if context:
            res = [ {'component': r['component'](*context), 'name': r['name']} for r in res ] 
        else:
            res = [ {'component': r['component'](),         'name': r['name']} for r in res ] 
    else:
        res = [ {'component': r['component'], 'name': r['name']} for r in res ] 

    toc = timeit.default_timer()
    logger.debug('_filter_search took: %s, found: %s' % ((toc - tic), res))
    return res


def _clean_is_a(is_a):
    if type(is_a) == str:
        return is_a
    elif isclass(is_a):
        return is_a.__name__
    else:
        raise errors.ComponentFilterError('is_a must be a Class or a String')


def _get_key(is_a, name=''):
    is_a_str = _clean_is_a(is_a)
    key = is_a_str
    if name:
        key = is_a_str + ':' + name
    return key


def filter_components(is_a, context=(), name='', instantiate=False):
    is_a_str = _clean_is_a(is_a)
    key = is_a_str + '*'
    if name:
        # looks like a specific filter search by name
        # key will be something like '<is-a>:<name>'
        key = _get_key(is_a_str, name)

    return _filter_search(key, context, instantiate)


def query_component(is_a, context=(), name='', instantiate=False):
    key = _get_key(is_a, name)
    components = _filter_search(key, context=context, instantiate=instantiate)

    if not components:
        return None
    if len(components) > 1:
        raise errors.MultipleComponentsReturned('Multiple Components found for type: "%s", context: %s, name: "%s"' % (is_a, context, name))

    return components[0]['component']


def get_component(is_a, context=(), name='', instantiate=False):
    component = query_component(is_a, context=context, name=name, instantiate=instantiate)
    if not component:
        raise errors.ComponentDoesNotExist('No Component Found for type: "%s", context: %s, name: "%s"' % (is_a, context, name))

    return component
