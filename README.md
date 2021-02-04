# Véritable Application en Ligne pour Épreuves Notées et Traitement des Interviews Nominatives

Django application to manage remote semifinals @Prologin

## Start hacking

On first install :

```
git clone git@github.com:prologin/valentin
cd valentin
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

You must have a valid config to start the django app. To do so :

```
cp valentin/valentin/settings/{conf.sample,dev}.py
```

## Issues

If you have noticed an issue please open an issue on this repository.

However for security issues you must, instead of opening an issue, send
an email to sadm@prologin.org
