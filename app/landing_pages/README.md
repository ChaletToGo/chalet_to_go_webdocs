# Landing pages

Reserve one package per campaign here, each with `routes.py`, `templates/`, `static/` and its own content. Register its APIRouter and named static mount in `app/main.py` under an explicit URL prefix. Use shared assets through `url_for('static', path='images/...')` and shared language negotiation from `app.shared.i18n`. Do not import templates or catalogs from another project.
