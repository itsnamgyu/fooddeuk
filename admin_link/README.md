# Admin Link

### Basic usage

```
{% load admin_link %}
...
{% admin_link instance action label %}
```

where `action` can be:

- `'changelist'`: list
- `'change'`: edit
- `'add'`: create
- `'delete'`: delete

This will display a link to the admin page, _only if_ the current user has permissions to that page.

_Don't forget wrap the string with quotes._

## Custom template

To customize the appearance of the link, you can use the `admin_link_url` tag to get the raw url of the admin link.

### Usage

```
{% load admin_link %}
...
{% admin_link_url instance action  as url %}
{% if url %}
    <a href="{{ url }}>Click on the magic link!</a>
{% else %}
    <p>You don't have permission to use the magic link! Haw haw!</p>
{% endif%}
```
