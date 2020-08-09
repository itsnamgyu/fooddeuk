from django.urls import path
from django.views.generic import TemplateView

from .views.console import *
from .views.examples import *
from .views.utils import *

app_name = "dt-content"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path(
        "toggle-preview-mode",
        TogglePreviewModeView.as_view(),
        name="toggle-preview-mode",
    ),
    path("menus/", MenuListView.as_view(), name="menu-list"),
    path("menus/create/", MenuCreateView.as_view(), name="menu-create"),
    path("menus/update/<slug:slug>/", MenuUpdateView.as_view(), name="menu-update"),
    path("submenus/create/", SubmenuCreateView.as_view(), name="submenu-create"),
    path(
        "submenus/update/<slug:slug>/",
        SubmenuUpdateView.as_view(),
        name="submenu-update",
    ),
    path("menus/delete/<slug:slug>/", MenuDeleteView.as_view(), name="menu-delete"),
    path(
        "content-sections/",
        ContentSectionListView.as_view(),
        name="content-section-list",
    ),
    path(
        "content-sections/update/<slug:slug>/",
        ContentSectionUpdateView.as_view(),
        name="content-section-update",
    ),
    path(
        "content-section/delete/<slug:slug>/",
        ContentSectionDeleteView.as_view(),
        name="content-section-delete",
    ),
    path("content-blocks/", ContentBlockListView.as_view(), name="content-block-list"),
    path(
        "content-block/delete/<slug:slug>/",
        ContentBlockDeleteView.as_view(),
        name="content-block-delete",
    ),
    path("blurbs/", BlurbListView.as_view(), name="blurb-list"),
    path("blurbs/update/<slug:slug>/", BlurbUpdateView.as_view(), name="blurb-update"),
    path("image-blurbs/", ImageBlurbListView.as_view(), name="image-blurb-list"),
    path(
        "image-blurbs/update/<slug:slug>/",
        ImageBlurbUpdateView.as_view(),
        name="image-blurb-update",
    ),
    path(
        "rich-text-blocks/update/<slug:slug>/",
        RichTextBlockUpdateView.as_view(),
        name="rich-text-block-update",
    ),
    path(
        "rich-text-blocks/create/",
        RichTextBlockCreateView.as_view(),
        name="rich-text-block-create",
    ),
    path("example/block/", ExampleStaticBlockView.as_view(), name="example-block"),
    path(
        "example/section/", ExampleStaticSectionView.as_view(), name="example-section"
    ),
    path("example/blurb/", ExampleBlurbView.as_view(), name="example-blurb"),
    path(
        "example/image-blurb/",
        ExampleImageBlurbView.as_view(),
        name="example-image-blurb",
    ),
    path(
        "example/site_test/index/",
        ExampleSiteIndexView.as_view(),
        name="example-site-index",
    ),
    path(
        "example/site_test/<path:menu_path>/",
        ExampleSitePageView.as_view(),
        name="example-site-page",
    ),
    path(
        "example/site_test/",
        ExampleSitePageView.as_view(),
        name="example-site-page-base",
    ),
]
