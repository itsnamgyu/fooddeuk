import os

from .models import *


def get_nav_menu_list(base_url, request_path=None, preview_mode=False):
    menu_dict = dict()
    menus = list(Menu.objects.all())

    # Parent menus
    for menu in menus:
        if not menu.parent_id:
            if menu.redirect_to:
                href = menu.redirect_to
            else:
                # TODO may not be appropriate to use os.path.join
                href = os.path.join(base_url, menu.url_slug)
            # TODO comparing request_path with redirect url (which may or may not be a full URL)
            active = request_path and request_path.find(href) == 0

            menu_dict[menu.id] = dict(
                id=menu.id,
                title=menu.title,
                href=href,
                active=active,
                disabled=menu.disabled,
                children=list(),
            )

    # Child menus
    for menu in menus:
        if menu.parent_id:
            parent_dict = menu_dict[menu.parent_id]
            if menu.redirect_to:
                href = menu.redirect_to
            else:
                # TODO may not be appropriate to use os.path.join
                href = os.path.join(base_url, parent_dict["href"], menu.url_slug)

            # TODO comparing request_path with redirect url (which may or may not be a full URL)
            active = request_path and request_path.find(href) == 0
            parent_dict["children"].append(
                dict(
                    id=menu.id,
                    title=menu.title,
                    parent=parent_dict,
                    href=href,
                    active=active,
                    disabled=menu.disabled,
                )
            )

    return list(menu_dict.values())
