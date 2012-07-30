from django.contrib import admin
from django.contrib.admin.options import StackedInline

from example_admintabs_project.example_app.models import Article, Category

from admin_tabs.helpers import TabbedModelAdmin, TabbedPageConfig, Config


class ArticlePageConfig(TabbedPageConfig):
    class FieldsetsConfig:
        titles = Config(fields=["title", "subtitle"], name="Title & Subtitle")
        miscdata = Config(fields=["modified_at", "created_at", "is_online"], name="Dates & State")
        content = Config(name="Content", fields=["content"])
        authors = Config(name="Authors", inline="ArticleToUserInline")
        categories = Config(name="Category", inline="ArticleToCategoryInline")
    
    class ColsConfig:
        content_col = Config(name="Contenu", fieldsets=["content"], css_classes=["col1"])
        titles_col = Config(name="Titles", fieldsets=["titles", "miscdata"], css_classes=["col1"])
        authors_col = Config(name="Authors", fieldsets=["authors"], css_classes=["col1"])
        categories_col = Config(name="Categories", fieldsets=["categories"], css_classes=["col1"])
    
    class TabsConfig:
        main_tab = Config(name="Main", cols=["content_col", "titles_col"])
        secondary_tab = Config(name="Relations", cols=["authors_col", "categories_col"])


class ArticleToUserInline(StackedInline):
    model = Article.authors.through


class ArticleToCategoryInline(StackedInline):
    model = Article.categories.through


class ArticleAdmin(TabbedModelAdmin):
    page_config_class = ArticlePageConfig
    readonly_fields = ('created_at', 'modified_at')
    inlines = (ArticleToUserInline, ArticleToCategoryInline)
    change_form_template = 'example_app/change_form.html'

    class Media:
        css = {
            "all": ("example_app/css/jquery-ui-1.8.22.custom.css", "example_app/css/tabs.css")
        }
        js = ("example_app/js/jquery-ui-1.8.22.custom.min.js",)  # Note: was modified to use django.jQuery and not jQuery

admin.site.register(Article, ArticleAdmin)
admin.site.register(Category)