from django.shortcuts import reverse


ACTIONS = ("changelist", "add", "change", "delete")


def get_admin_link_url(context, instance, action: str):
    if action not in ACTIONS:
        raise ValueError(
            "`action` must be one of {}. Value provided is `{}`.".format(
                ACTIONS, action
            )
        )

    try:
        app = instance._meta.app_label
        model = instance._meta.model_name
    except AttributeError:
        return None

    url_name = "admin:%s_%s_%s" % (app, model, action)

    if action in ("change", "delete"):
        args = (instance.pk,)
    else:
        args = ()

    url = reverse(
        url_name, args=args, current_app=context.request.resolver_match.app_name
    )
    full_url = "{}?admin_link_redirect={}".format(url, context.request.get_full_path())

    return full_url


def has_permission(context, instance, action: str):
    user = context.request.user

    try:
        app = instance._meta.app_label
        model = instance._meta.model_name
    except AttributeError:
        return False

    return user.has_perm("{}.{}_{}".format(app, action, model))
