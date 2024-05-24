# PlaywrightAutomation
Using Playwright to automate browser tasks.

## setup
Create a virtual env and install playwright

```python
python -m venv venv # create virtual environment
.\venv\Scripts\activate # OR: 'source venv/Scripts/active' if on Unix
pip install pytest-playwright # require playwright
playwright install # let playwright install its dependencies
pytest # run pytest which will run test_* files to make sure all works
```

## tailwind build

```cli
npx tailwindcss -i ./css/pre-styles.css -o ./css/styles.css --watch
```

## run server
Start the flask server at http://127.0.0.1:5000 with:

```cli
flask run
```
Run in debug with `--debug` - has file watching
Make accessible on the LAN with `--host=0.0.0.0`.