# PlaywrightAutomation
Using Playwright to automate browser tasks.

## Build
Vite is used as a static resource builder and compiles the TS files to `/assets_compiled/bundled` from the base directory.
Tailwind is used for CSS and compiles `/static/css/` to `/static/css/styles.css`.
Flask runs the web server and has a blueprint in `assets_blueprint.py` which is then imported into `app.py` and allows use of the `asset()` function and access to the `is_production` setting.

### setup
Create a virtual env and install playwright

```python
python -m venv venv # create virtual environment
.\venv\Scripts\activate # OR: 'source venv/Scripts/active' if on Unix
pip install pytest-playwright # require playwright
playwright install # let playwright install its dependencies
pytest # run pytest which will run test_* files to make sure all works
```

### tailwind build

```cli
npx tailwindcss -i ./static/css/pre-styles.css -o ./static/css/styles.css --watch
```

### run server
Start the flask server at http://127.0.0.1:5000 with:

```cli
flask run --port 8000
```
Run in debug with `--debug` - has file watching
Make accessible on the LAN with `--host=0.0.0.0`.

### compile static resources with vite
```cli
npm run dev
```
Runs the vite development server with compiles TypeScript into `assets_compiled/bundled`.

## Resources

Vite & Flask integration: https://dev.to/wtho/get-started-with-alpinejs-and-typescript-4dgf