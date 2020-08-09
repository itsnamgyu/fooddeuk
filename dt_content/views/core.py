import logging
from typing import Tuple

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import ContextMixin, TemplateView

from ..menu import get_nav_menu_list
from ..mixins import PreviewModeMixin
from ..models import *


class PageContextMixin(PreviewModeMixin, ContextMixin):
    """
    Examle usage:

    URL path: /menus/<parent_menu_slug>/<child_menu_slug?>
    URL pattern: /menus/<path:menu_path>
    `menu_base_url`: "/menus"
    `menu_path_kwarg`: "menu_path"

    ## Optimization Notes
    - Need to combine `get_current_menu` and `get_menu_list` for optimal performance.
      These methods are called for **every** page load.
    """

    menu_base_url = "/"
    menu_path_kwarg = "menu_path"

    def get_menu_base_url(self):
        return str(self.menu_base_url)  # may be lazy

    def get_current_menu(self, request):
        menu_path = self.kwargs.get(self.menu_path_kwarg)
        if not menu_path:
            return None

        slugs = menu_path.split("/")

        if len(slugs) not in [1, 2]:
            logging.warning("Invalid menu_path {}".format(menu_path))

        parent_slug = slugs[0]
        parent = get_object_or_404(Menu, url_slug=parent_slug, parent=None)

        if len(slugs) == 2:
            child_slug = slugs[1]
            child = get_object_or_404(Menu, url_slug=child_slug, parent=parent)
            return child

        return parent

    def get_nav_menu_list(self):
        return get_nav_menu_list(
            self.get_menu_base_url(), self.request.path, self.get_preview_mode()
        )

    def get_page_context_data(self, **kwargs):
        page_context = dict()

        current_menu = self.get_current_menu(self.request)
        nav_menu_list = self.get_nav_menu_list()

        nav_menu = None
        if current_menu:
            if current_menu.parent:
                parent_menu = current_menu.parent
                child_menu = current_menu
            else:
                parent_menu = current_menu
                child_menu = None

            # Search parent
            for menu in nav_menu_list:
                if menu["id"] == parent_menu.id:
                    nav_menu = menu
                    break
            else:
                logging.warning("Could not find current parent menu in menu_list")

            # Search child if exists
            if child_menu:
                for menu in nav_menu["children"]:
                    if menu["id"] == child_menu.id:
                        nav_menu = menu
                        break
                else:
                    logging.warning("Could not find current child menu in menu_list")
            page_context["content_section"] = current_menu.get_content_section()
            page_context["nav_menu"] = nav_menu

        page_context["nav_menu_list"] = nav_menu_list
        page_context["dt_content_preview_mode"] = self.get_preview_mode()

        return page_context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_page_context_data())
        return context


PageMixin = PageContextMixin  # deprecated


class PageView(PageContextMixin, TemplateView):
    """
    Examle usage:

    URL path: /menus/<parent_menu_slug>/<child_menu_slug?>
    URL pattern: /menus/<path:menu_path>
    `menu_base_url`: "/menus"
    `menu_path_kwarg`: "menu_path"

    ## Optimization Notes
    - Need to combine `get_current_menu` and `get_menu_list` for optimal performance.
      These methods are called for **every** page load.
    """
