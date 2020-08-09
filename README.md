# Django Template

## Requirements

Python 3.6.x or 3.7.x should work without problems. This template is being built mainly on 3.7.3.

## Getting Started

#### Initialize `.env`

For now, just copy the example file.

```
cp .env.example .env
```

#### Initialize Virtual Environment via `venv`

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Runserver

```
python manage.py runserver
```

## Project Customization

To ease the process of manually merging upstream changes from this base template, follow the guidelines below when you add customizations for your project

1. Customize Django project settings by modifying `/app/settings/project.py`.
2. Customize base templates and styles by modifying the placeholder files in `/static/` and `/templates/`. Refer to the `base` app on the usage of these files.
3. Customize **deployment specific** settings using `.env`. `.env` should not be checked into version control.
4. Feel free to completely modify or remove the `core` app. This is simply an example implementation.

#### New Project Checklist

- [ ] Update default site name and domain in `/app/settings/project.py`.
- [ ] Update default values in `.env.example`.
- [ ] Update copyright notice in `/templates/account/snippets/copyright.html`
- [ ] Update head tags in `/templates/base/extra_head.html`
- [ ] Update logo image in `/static/account/img/logo.png`
- [ ] Update favicon and og-image in `/static/base/img/`
- [ ] Update base styles in `/static/base/css/styles.css`
- [ ] Rewrite `core` app

## Deployment

#### Auto Deployment Script for Apache

```bash
./script/deploy_apache --host=domain.com
```

## Contribution

#### Code formatting

Use [`black`](https://black.readthedocs.io/en/stable/installation_and_usage.html).

Use `scripts/lint.sh` to auto-format all code.
