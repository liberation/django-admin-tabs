# -*- coding: utf-8 -*-
from django.contrib.admin.helpers import AdminForm, Fieldset
from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import csrf_protect_m
from django.db import transaction

class AdminCol(object):
    """
    One column in the admin pages.
    """
    def __init__(self, fieldsets, name=None, css_id=None, css_classes=None):
        """
        `css_classes`: list of css classes
        """
        self.name = name
        self._fieldsets = {} # names of fieldsets for now (real Fieldsets should be better)
        for idx, fieldset in enumerate(fieldsets):
            self.add_fieldset(fieldset, idx)
        self.css_id = css_id
        self.css_classes = css_classes

    def add_fieldset(self, fieldset, position=None):
        if not position:
                position = len(self)
        self._fieldsets[position] = fieldset

    @property
    def fieldsets(self):
        """
        Returns the sorted fieldsets (the sort is made on the key, which is the position)
        """
        keys = self._fieldsets.keys()
        keys.sort()
        return map(self._fieldsets.get, keys)

    def __contains__(self, item):
        return item in self.fieldsets

    def __len__(self):
        return len(self._fieldsets)

    def get_fieldsets(self, request, obj=None):
        """
        Returns fieldsets, as expected by Django...
        """
        return self.get_elements(request, obj=obj) # Without inlines
    
    def get_elements(self, request, obj=None, include_inlines=False):
        col_elements = []
        for fieldset_config in self.fieldsets:
            if fieldset_config.inline is not None:
                if not include_inlines:
                    continue # not inlines here
                col_element = (
                    fieldset_config.name,
                    {"inline": fieldset_config.inline}
                )
            else: # Classic fieldset
                col_element = (
                    fieldset_config.name,
                    {
                        "fields": fieldset_config.fields,
                        "classes": fieldset_config.css_classes,
                    }
                )
            col_elements.append(col_element)
        return col_elements


class AdminTab(object):
    """
    One Tab in the admin pages.
    """
    def __init__(self, name, cols, enabled=True):
        self.name = name
        self.enabled = enabled
        self._cols = {}
        for idx, col in enumerate(cols):
            self.add_col(col, idx)
    
    def add_col(self, col, position=None):
        # Position is not an attribute of the col, but of the relation tab=>col
        if not position:
                position = len(self)
        # FIXME: manage position insertion
        self._cols[position] = col
    
    @property
    def cols(self):
        """
        Returns the sorted cols (the sort is made on the key, which is the position)
        """
        keys = self._cols.keys()
        keys.sort()
        return map(self._cols.get, keys)
    
    def __iter__(self):
        return self.cols.__iter__()

    def __len__(self):
        return len(self._cols)
    
    def __getitem__(self, item):
        """
        Returns a col by its position.
        """
        return self._cols[item]
    
    def medias(self):
        return 

class AdminFieldsetConfig(object):
    """
    Wrapper to define the admin Fieldset.
    See https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets
    for the original syntax.
    
    It can be a real Fieldset or an Inline.
    """
    def __init__(self, fields=None, inline=None, name=None, css_classes=None, description=None):
        self.description = description
        self.css_classes = css_classes or []
        self.fields = fields
        self.inline = inline
        self.name = name
    
    def __iter__(self):
        return self.fields.__iter__()
    
    def __getitem__(self, item):
        return getattr(self, item)


class Config(dict):
    """
    Basic extension of a dict object to manage the attributes order in class
    definition.
    """
    creation_counter = 0

    def __init__(self, *args, **kwargs):
        self.creation_counter = Config.creation_counter
        Config.creation_counter += 1
        return super(Config, self).__init__(*args, **kwargs)


class Tabs(object):
    """
    Base class for the tabs object.
    
    Manages the tabs order in __setattr__ and __delattr__.
    """

    def __init__(self, *args, **kwargs):
        # Set the property to store the tabs order automatically from 
        # __setattr__ and __delattr__
        object.__setattr__(self, "tabs_order", [])

    def __setattr__(self, name, value):
        # Manage the tabs_order
        if not name.startswith("_"):
            self.tabs_order.append(name)
        super(Tabs, self).__setattr__(name, value)

    def __delattr__(self, name):
        # Manage the tabs_order
        if not name.startswith("_"):
            self.tabs_order.remove(name)
        super(Tabs, self).__delattr__(name)


class MetaAdminPageConfig(type):
    """
    This metaclass make inheritance between the inner classes of the PageConfig
    classes.
    """
    def __new__(mcs, name, base, dct):
        it = type.__new__(mcs, name, base, dct)

        def _manage_config_class_inheritance(config_class_name):
            """
            Manage the ihneritance of the config classes (TabsConfig, ColsConfig
            and FieldsetsConfig):

            - inherit attributes from parent when not setted in current class
            - remove parent attribute when setted to None in current class
            - merge with parent ones if setted also in current class

            :param config_class_name: could be "TabsConfig", "ColsConfig" or
                                      "FieldsetsConfig"
            """
            _final_attrs = {}  # Attrs that will be finally added to the created class
            reverse_mro = list(it.mro())
            reverse_mro.reverse()
            for cls in reverse_mro:
                if not hasattr(cls, config_class_name): continue
                # config_class will be cls.TabsConfig, cls.ColsConfig or
                # cls.FieldsetsConfig, according to the given config_class_name
                # param
                config_class = getattr(cls, config_class_name)
                for attr_name in dir(config_class):
                    # Lets look for the Config attribute of the current inner class
                    attr = getattr(config_class, attr_name)
                    # We keep Config instances AND attr_name already in _final_attrs
                    # because they can be overwritten by None
                    if not isinstance(attr, Config) and not attr_name in _final_attrs: continue
                    # Setting some attr to None remove an attr that was setted in a 
                    # parent class
                    if attr is None and attr_name in _final_attrs:
                        del _final_attrs[attr_name]
                        delattr(config_class, attr_name)
                    else:
                        # Merge with parent's attr if exists
                        if attr_name in _final_attrs:
                            config = Config(**_final_attrs[attr_name])  # Copy it
                            config.update(attr)
                            attr = config
                        _final_attrs[attr_name] = attr

            # Add selected Config attributes in the created class
            # final_class_config is the it.TabsConfig, it.ColsConfig or 
            # it.FieldsetsConfig, according to the given config_class_name param
            # (Do not confuse with the cls.X ones: `it` is current created class,
            # `cls` are the parent classes from which we inherit attributes)
            final_class_config = getattr(it, config_class_name)
            for attr_name, attr in _final_attrs.iteritems():
                setattr(final_class_config, attr_name, attr)
            return _final_attrs

        # --- Make the TabsConfig attributes overwrittable and inheritable
        _manage_config_class_inheritance("TabsConfig")

        # --- Make the ColsConfig attributes overwrittable and inheritable
        _manage_config_class_inheritance("ColsConfig")

        # --- Make the FieldsetsConfig attributes overwrittable and inheritable
        _manage_config_class_inheritance("FieldsetsConfig")

        # --- Define a default tabs order if user as not provided one
        if not hasattr(it.TabsConfig, 'tabs_order'):
            tabs_order = [attr for attr in dir(it.TabsConfig) if not attr.startswith('_')]
            tabs_order.sort(key=lambda attr: getattr(it.TabsConfig, attr).creation_counter)
            setattr(it.TabsConfig, "tabs_order", tabs_order)
        return it

class TabbedPageConfig(object):
    """
    Subsclass it to be able to manage the tabs.
    Define in the inner class Fields the fieldsets you will use in your cols.
    """
    __metaclass__ = MetaAdminPageConfig
    class FieldsetsConfig(object): pass
    class ColsConfig(object): pass
    class TabsConfig(object): pass
    
    def __init__(self, request, model_admin, obj_or_id=None):
        # Create these inner classes at runtime
        # to prevent from sharing them between instances
        self.Fields = type("Fields", (object,), {})
        self.Cols = type("Cols", (object,), {})
        self.Tabs = Tabs()  # Instantiate it to be able to define __setattr__
                            # and __delattr__
                            # TODO: instanciate also Fields and Cols?
        self.model_admin = model_admin
        self.request=request
        # Populate the fieldsets
        for f in dir(self.FieldsetsConfig):
            if f.startswith("_"): continue
            fields = getattr(self.FieldsetsConfig, f)
            if not fields: continue
            fieldsetconfig = AdminFieldsetConfig(**fields)
            setattr(self.Fields, f, fieldsetconfig)
        # Put AdminCols instance in self.Cols
        for f in dir(self.ColsConfig):
            if f.startswith("_"): continue
            # Make a copy, as it is a dict static properties
            # and we are making change on it
            cols = getattr(self.ColsConfig, f)
            if not cols: continue
            ColsConfig = dict(cols)
            # We want AdminFieldsetConfig instances, not names 
            ColsConfig['fieldsets'] = map(lambda k: getattr(self.Fields, k), ColsConfig['fieldsets']) 
            # Col instance need to know about its AdminFormConfig parent
#            ColsConfig["page_config"] = self
            setattr(self.Cols, f, AdminCol(**ColsConfig))
            del ColsConfig
        # Put AdminTabs instances in self.Tabs
        for f in self.TabsConfig.tabs_order:
            # Make a copy, as it is a dict static properties
            # and we are making change on it
            tabs = getattr(self.TabsConfig, f)
            if not tabs: continue
            tabconfig = dict(tabs)
            # We want ColsConfig instances, not names
            tabconfig['cols'] = map(lambda k: getattr(self.Cols, k), tabconfig['cols'])
            setattr(self.Tabs, f, AdminTab(**tabconfig))

    def __iter__(self):
        for attr in self.Tabs.tabs_order:
            yield getattr(self.Tabs, attr)
    
    @property
    def tabs(self):
        return self.__iter__()

class TabbedModelAdmin(ModelAdmin):
    
    declared_fieldsets = []
    page_config_class = TabbedPageConfig
    def __init__(self, *args, **kwargs):
        self._page_config = None  # For caching, warning, it'a class consistent
                                  # Override get_page_config for changing Tabs 
                                  # at run time
        return super(TabbedModelAdmin, self).__init__(*args, **kwargs)

    def get_page_config(self, request, obj_or_id=None, **kwargs):
        """
        Returns the page config for the current model_admin.
        
        Override this method to be able to change Tabs, Cols and Fields at 
        runtime.
        `obj_or_id` could be an instance or a pk or None (when you call it from a 
        change_view extended, you have only the pk).
        """
        if self._page_config is None:
            self._page_config = self.page_config_class(request, self, obj_or_id=obj_or_id)
        return self._page_config
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = []
        page_config = self.get_page_config(request, obj_or_id=obj)
        for tab in page_config:
            for col in tab:
                fieldsets += col.get_fieldsets(request, obj)
        return fieldsets
    
    def get_form(self, request, obj=None, **kwargs):
        self.declared_fieldsets = self.get_fieldsets(request, obj)
        return super(TabbedModelAdmin, self).get_form(request, obj, **kwargs)
    
    @csrf_protect_m
    @transaction.commit_on_success
    def change_view(self, request, object_id, form_url='', extra_context=None):
        if extra_context is None:
            extra_context = {}
        page_config = self.get_page_config(request, obj_or_id=object_id)
        extra_context.update({'page_config': page_config})
        try:
            # django 1.4
            return super(TabbedModelAdmin, self).change_view(request, object_id, form_url=form_url, extra_context=extra_context)
        except TypeError:
            # django 1.3
            return super(TabbedModelAdmin, self).change_view(request, object_id, extra_context=extra_context)
    
    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        if extra_context is None:
            extra_context = {}
        page_config = self.get_page_config(request)
        extra_context.update({'page_config': page_config})
        return super(TabbedModelAdmin, self).add_view(request, form_url=form_url, extra_context=extra_context)

