# -*- coding: utf-8 -*-
from django.contrib.admin.helpers import AdminForm, Fieldset
from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import csrf_protect_m
from django.db import transaction

class AdminCol(object):
    """
    One column in the admin pages.
    """
    def __init__(self, fieldsets, name=None, css_id=None, css_class=None):
        self.name = name
        self.fieldsets = [] # names of fieldsets for now (real Fieldsets should be better)
        for fieldset in fieldsets:
            self.add_fieldset(fieldset)
        self.css_id = css_id
        self.css_class = css_class
    
    def add_fieldset(self, fieldset, position=None):
        # FIXME: manage position
        self.fieldsets.append(fieldset)
    
    def __contains__(self, item):
        return item in self.fieldsets
    
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
                    {"fields": fieldset_config.fields}
                )
            col_elements.append(col_element)
        return col_elements

class AdminTab(object):
    """
    One Tab in the admin pages.
    """
    def __init__(self, name, cols):
        self.name = name
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

class MetaAdminPageConfig(type):
    """
    This metaclass make inheritance between the inner classes of the PageConfig
    classes.
    """
    def __new__(mcs, name, base, dict):
        it = type.__new__(mcs, name, base, dict)
        # Make the FieldsetsConfig attributes overwrittable and inheritable
        for cls in it.mro():
            if not hasattr(cls, "FieldsetsConfig"): continue
            for attr in dir(cls.FieldsetsConfig):
                if attr.startswith("_"): continue
                if hasattr(it.FieldsetsConfig, attr): continue # do not override
                setattr(it.FieldsetsConfig, attr, getattr(cls.FieldsetsConfig, attr))
        # Make the ColsConfig attributes overwrittable and inheritable
        for cls in it.mro():
            if not hasattr(cls, "ColsConfig"): continue
            for attr in dir(cls.ColsConfig):
                if attr.startswith("_"): continue
                if hasattr(it.ColsConfig, attr): continue # do not override
                setattr(it.ColsConfig, attr, getattr(cls.ColsConfig, attr))
        # Make the TabsConfig attributes overwrittable and inheritable
        for cls in it.mro():
            if not hasattr(cls, "TabsConfig"): continue
            for attr in dir(cls.TabsConfig):
                if attr.startswith("_"): continue
                if hasattr(it.TabsConfig, attr): continue # do not override
                setattr(it.TabsConfig, attr, getattr(cls.TabsConfig, attr))
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
    
    def __init__(self, request, model_admin, obj=None):
        # Create these inner classes at runtime
        # to prevent from sharing them between instances
        self.Fields = type("Fields", (object,), {})
        self.Cols = type("Cols", (object,), {})
        self.Tabs = type("Tabs", (object,), {})
        self.model_admin = model_admin
        self.request=request
        # Populate the fieldsets
        for f in dir(self.FieldsetsConfig):
            if f.startswith("_"): continue
            fieldsetconfig = AdminFieldsetConfig(**getattr(self.FieldsetsConfig, f))
            setattr(self.Fields, f, fieldsetconfig)
        # Put AdminCols instance in self.Cols
        for f in dir(self.ColsConfig):
            if f.startswith("_"): continue
            # Make a copy, as it is a dict static properties
            # and we are making change on it
            ColsConfig = dict(getattr(self.ColsConfig, f))
            # We want AdminFieldsetConfig instances, not names 
            ColsConfig['fieldsets'] = map(lambda k: getattr(self.Fields, k), ColsConfig['fieldsets']) 
            # Col instance need to know about its AdminFormConfig parent
#            ColsConfig["page_config"] = self
            setattr(self.Cols, f, AdminCol(**ColsConfig))
            del ColsConfig
        # Put AdminTabs instance in self.Tabs
        for f in dir(self.TabsConfig):
            if f.startswith("_"): continue
            # Make a copy, as it is a dict static properties
            # and we are making change on it
            tabconfig = dict(getattr(self.TabsConfig, f))
            # We want ColsConfig instances, not names
            tabconfig['cols'] = map(lambda k: getattr(self.Cols, k), tabconfig['cols'])
            setattr(self.Tabs, f, AdminTab(**tabconfig))
    
    def __iter__(self):
        for attr in dir(self.Tabs):
            if attr.startswith("_"): continue
            yield getattr(self.Tabs, attr)
    
    @property
    def tabs(self):
        return self.__iter__()

class TabbedModelAdmin(ModelAdmin):
    
    declared_fieldsets = []
    page_config_class = TabbedPageConfig
    def __init__(self, *args, **kwargs):
        self._page_config = None
        return super(TabbedModelAdmin, self).__init__(*args, **kwargs)
    
    def get_page_config(self, request, obj=None, **kwargs):
        if self._page_config is None:
            self._page_config = self.page_config_class(request, self, obj=obj)
        return self._page_config
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = []
        page_config = self.get_page_config(request, obj=None)
        for tab in page_config:
            for col in tab:
                fieldsets += col.get_fieldsets(request, obj)
        return fieldsets
    
    def get_form(self, request, obj=None, **kwargs):
        self.declared_fieldsets = self.get_fieldsets(request, obj)
        return super(TabbedModelAdmin, self).get_form(request, obj, **kwargs)
    
    @csrf_protect_m
    @transaction.commit_on_success
    def change_view(self, request, object_id, extra_context=None):
        if extra_context is None:
            extra_context = {}
        page_config = self.get_page_config(request)
        extra_context.update({'page_config': page_config})
        return super(TabbedModelAdmin, self).change_view(request, object_id, extra_context)
    
    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, object_id, extra_context=None):
        if extra_context is None:
            extra_context = {}
        page_config = self.get_page_config(request)
        extra_context.update({'page_config': page_config})
        return super(TabbedModelAdmin, self).add_view(request, object_id, extra_context)

