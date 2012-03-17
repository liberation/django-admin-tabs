from django.test import TestCase

from admin_tabs.helpers import TabbedPageConfig, Config

__all__ = [
    "TabsConfigsInheritanceTests",
    "TabsConfigOrderTests",
    "ColsConfigIneritanceTests",
    "FieldsetsConfigIneritanceTests"
]

class TabsConfigsInheritanceTests(TestCase):

    def test_should_inherit_from_parent(self):
        """
        When a PageConfig inherit from another, it must inherit the tabs of its
        parent.
        """

        class A(TabbedPageConfig):

            class TabsConfig:
                a_tab = Config(name='a_tab')

        class AB(A):

            class TabsConfig:
                b_tab = Config(name="b_tab")

        class AD(A):

            class TabsConfig:
                d_tab = Config(name="d_tab")

        class ABC(AB):

            class TabsConfig:
                c_tab = Config(name="c_tab")

        # A must have only its attribute
        self.failUnless(hasattr(A.TabsConfig, "a_tab"))
        self.assertEqual(A.TabsConfig.a_tab["name"], "a_tab")
        self.failIf(hasattr(A.TabsConfig, "b_tab"))

        # AB must have its attribute and A's one
        self.failUnless(hasattr(AB.TabsConfig, "b_tab"))
        self.failUnless(hasattr(AB.TabsConfig, "a_tab"))
        self.assertEqual(AB.TabsConfig.a_tab["name"], "a_tab")
        self.assertEqual(AB.TabsConfig.b_tab["name"], "b_tab")
        self.failIf(hasattr(AB.TabsConfig, "c_tab"))
        self.failIf(hasattr(AB.TabsConfig, "d_tab"))

        # ABC must have its attribute, AB's one and A's one
        self.failUnless(hasattr(ABC.TabsConfig, "c_tab"))
        self.failUnless(hasattr(ABC.TabsConfig, "b_tab"))
        self.failUnless(hasattr(ABC.TabsConfig, "a_tab"))
        self.assertEqual(ABC.TabsConfig.a_tab["name"], "a_tab")
        self.assertEqual(ABC.TabsConfig.b_tab["name"], "b_tab")
        self.assertEqual(ABC.TabsConfig.c_tab["name"], "c_tab")
        self.failIf(hasattr(ABC.TabsConfig, "d_tab"))

    def test_none_should_remove_inherited_tab(self):
        """
        When a class inherit from another, it could remove some tab attribute
        in setting it with None value.
        """

        class A(TabbedPageConfig):
            
            class TabsConfig:
                a_tab = Config(name='a_tab')
                none_tab = Config(name='none_tab')

        class AB(A):
            
            class TabsConfig:
                b_tab = Config(name="b_tab")
                none_tab = None

        # A must have all its attribute
        self.failUnless(hasattr(A.TabsConfig, "a_tab"))
        self.failUnless(hasattr(A.TabsConfig, "none_tab"))

        # AB must have its attribute and A's one, but not the None overidden
        self.failUnless(hasattr(AB.TabsConfig, "b_tab"))
        self.failUnless(hasattr(AB.TabsConfig, "a_tab"))
        self.failIf(hasattr(AB.TabsConfig, "none_tab"))

    def test_should_merge_non_overriden_attributes(self):
        """
        When inheriting from a parent, you can set only the attributes of a tab
        that you want to ovverride.
        """
        class A(TabbedPageConfig):

            class TabsConfig:
                tab = Config(name="myname", cols=["a", "b", "c"])

        class AB(A):

            class TabsConfig:
                tab = Config(cols=["b", "c", "a"])

        self.assertEqual(A.TabsConfig.tab["cols"], ["a", "b", "c"])
        self.assertEqual(AB.TabsConfig.tab["cols"], ["b", "c", "a"])
        self.assertEqual(AB.TabsConfig.tab["name"], "myname")


class TabsConfigOrderTests(TestCase):
    
    def test_should_keep_natural_order(self):
        """
        With no order asked, the order must be the order of the tabs in the
        python file.
        """

        class A(TabbedPageConfig):
            
            class TabsConfig:
                # We suffix names with integers to check that the final order 
                # will not be alphanumeric
                tab42 = Config(name='first')
                tab18 = Config(name='second')
                tab37 = Config(name='third')
                
        self.assertEqual(A.TabsConfig.tabs_order, ["tab42", "tab18", "tab37"])

    def test_user_defined_tabs_order_should_have_priority(self):

        class A(TabbedPageConfig):
            
            class TabsConfig:
                tabs_order = ["tab1", "tab2", "tab3"]
                tab2 = Config(name='second')
                tab1 = Config(name='first')
                tab3 = Config(name='third')
                
        self.assertEqual(A.TabsConfig.tabs_order, ["tab1", "tab2", "tab3"])


class ColsConfigIneritanceTests(TestCase):

    def test_should_inherit_from_parent(self):
        """
        When a PageConfig inherit from another, it must inherit the cols of its
        parent.
        """

        class A(TabbedPageConfig):

            class ColsConfig:
                a_col = Config(name='a_col')

        class AB(A):

            class ColsConfig:
                b_col = Config(name="b_col")

        class AD(A):

            class ColsConfig:
                d_col = Config(name="d_col")

        class ABC(AB):

            class ColsConfig:
                c_col = Config(name="c_col")

        # A must have only its attribute
        self.failUnless(hasattr(A.ColsConfig, "a_col"))
        self.assertEqual(A.ColsConfig.a_col["name"], "a_col")
        self.failIf(hasattr(A.ColsConfig, "b_col"))

        # AB must have its attribute and A's one
        self.failUnless(hasattr(AB.ColsConfig, "b_col"))
        self.failUnless(hasattr(AB.ColsConfig, "a_col"))
        self.assertEqual(AB.ColsConfig.a_col["name"], "a_col")
        self.assertEqual(AB.ColsConfig.b_col["name"], "b_col")
        self.failIf(hasattr(AB.ColsConfig, "c_col"))
        self.failIf(hasattr(AB.ColsConfig, "d_col"))

        # ABC must have its attribute, AB's one and A's one
        self.failUnless(hasattr(ABC.ColsConfig, "c_col"))
        self.failUnless(hasattr(ABC.ColsConfig, "b_col"))
        self.failUnless(hasattr(ABC.ColsConfig, "a_col"))
        self.assertEqual(ABC.ColsConfig.a_col["name"], "a_col")
        self.assertEqual(ABC.ColsConfig.b_col["name"], "b_col")
        self.assertEqual(ABC.ColsConfig.c_col["name"], "c_col")
        self.failIf(hasattr(ABC.ColsConfig, "d_col"))

    def test_none_should_remove_inherited_tab(self):
        """
        When a class inherit from another, it could remove some col attribute
        in setting it with None value.
        """

        class A(TabbedPageConfig):
            
            class ColsConfig:
                a_col = Config(name='a_col')
                none_col = Config(name='none_col')

        class AB(A):
            
            class ColsConfig:
                b_col = Config(name="b_col")
                none_col = None

        # A must have all its attribute
        self.failUnless(hasattr(A.ColsConfig, "a_col"))
        self.failUnless(hasattr(A.ColsConfig, "none_col"))

        # AB must have its attribute and A's one, but not the None overidden
        self.failUnless(hasattr(AB.ColsConfig, "b_col"))
        self.failUnless(hasattr(AB.ColsConfig, "a_col"))
        self.failIf(hasattr(AB.ColsConfig, "none_col"))

    def test_should_merge_non_overriden_attributes(self):
        """
        When inheriting from a parent, you can set only the attributes of a col
        that you want to ovverride.
        """
        class A(TabbedPageConfig):

            class ColsConfig:
                col = Config(name="myname", fieldsets=["a", "b", "c"])

        class AB(A):

            class ColsConfig:
                col = Config(fieldsets=["b", "c", "a"])

        self.assertEqual(A.ColsConfig.col["fieldsets"], ["a", "b", "c"])
        self.assertEqual(AB.ColsConfig.col["fieldsets"], ["b", "c", "a"])
        self.assertEqual(AB.ColsConfig.col["name"], "myname")


class FieldsetsConfigIneritanceTests(TestCase):

    def test_should_inherit_from_parent(self):
        """
        When a PageConfig inherit from another, it must inherit the fieldsets of its
        parent.
        """

        class A(TabbedPageConfig):

            class FieldsetsConfig:
                a_fieldset = Config(name='a_fieldset')

        class AB(A):

            class FieldsetsConfig:
                b_fieldset = Config(name="b_fieldset")

        class AD(A):

            class FieldsetsConfig:
                d_fieldset = Config(name="d_fieldset")

        class ABC(AB):

            class FieldsetsConfig:
                c_fieldset = Config(name="c_fieldset")

        # A must have only its attribute
        self.failUnless(hasattr(A.FieldsetsConfig, "a_fieldset"))
        self.assertEqual(A.FieldsetsConfig.a_fieldset["name"], "a_fieldset")
        self.failIf(hasattr(A.FieldsetsConfig, "b_fieldset"))

        # AB must have its attribute and A's one
        self.failUnless(hasattr(AB.FieldsetsConfig, "b_fieldset"))
        self.failUnless(hasattr(AB.FieldsetsConfig, "a_fieldset"))
        self.assertEqual(AB.FieldsetsConfig.a_fieldset["name"], "a_fieldset")
        self.assertEqual(AB.FieldsetsConfig.b_fieldset["name"], "b_fieldset")
        self.failIf(hasattr(AB.FieldsetsConfig, "c_fieldset"))
        self.failIf(hasattr(AB.FieldsetsConfig, "d_fieldset"))

        # ABC must have its attribute, AB's one and A's one
        self.failUnless(hasattr(ABC.FieldsetsConfig, "c_fieldset"))
        self.failUnless(hasattr(ABC.FieldsetsConfig, "b_fieldset"))
        self.failUnless(hasattr(ABC.FieldsetsConfig, "a_fieldset"))
        self.assertEqual(ABC.FieldsetsConfig.a_fieldset["name"], "a_fieldset")
        self.assertEqual(ABC.FieldsetsConfig.b_fieldset["name"], "b_fieldset")
        self.assertEqual(ABC.FieldsetsConfig.c_fieldset["name"], "c_fieldset")
        self.failIf(hasattr(ABC.FieldsetsConfig, "d_fieldset"))

    def test_none_should_remove_inherited_tab(self):
        """
        When a class inherit from another, it could remove some fieldset
        attribute in setting it with None value.
        """

        class A(TabbedPageConfig):
            
            class FieldsetsConfig:
                a_fieldset = Config(name='a_fieldset')
                none_fieldset = Config(name='none_fieldset')

        class AB(A):
            
            class FieldsetsConfig:
                b_fieldset = Config(name="b_fieldset")
                none_fieldset = None

        # A must have all its attribute
        self.failUnless(hasattr(A.FieldsetsConfig, "a_fieldset"))
        self.failUnless(hasattr(A.FieldsetsConfig, "none_fieldset"))

        # AB must have its attribute and A's one, but not the None overidden
        self.failUnless(hasattr(AB.FieldsetsConfig, "b_fieldset"))
        self.failUnless(hasattr(AB.FieldsetsConfig, "a_fieldset"))
        self.failIf(hasattr(AB.FieldsetsConfig, "none_fieldset"))

    def test_should_merge_non_overriden_attributes(self):
        """
        When inheriting from a parent, you can set only the attributes of a 
        fieldset that you want to ovverride.
        """
        class A(TabbedPageConfig):

            class FieldsetsConfig:
                fieldset = Config(name="myname", fields=["a", "b", "c"])

        class AB(A):

            class FieldsetsConfig:
                fieldset = Config(fields=["b", "c", "a"])

        self.assertEqual(A.FieldsetsConfig.fieldset["fields"], ["a", "b", "c"])
        self.assertEqual(AB.FieldsetsConfig.fieldset["fields"], ["b", "c", "a"])
        self.assertEqual(AB.FieldsetsConfig.fieldset["name"], "myname")
