# PlaywrightAutomation
Using Playwright to automate browser tasks.

## Setup
Tailwind is used for CSS and compiles `/static/css/` to `/static/css/styles.css`.
Flask runs the web server.

### setup
Create a virtual env and install dependencies

```python
python -m venv venv # create virtual environment
.\venv\Scripts\activate # OR: 'source venv/Scripts/active' if on Unix
pip install -r requirements.txt # install dependencies
```

### tailwind build

```cli
npx tailwindcss -i ./static/css/pre-styles.css -o ./static/css/styles.css --watch
```

### initial the database
Running an SQLite3 database which is in `suppliers.sqlite`. The schema for this is `schema.sql` which
can be run using;
```python
from app import init_db
init_db()
```

#### Sample data
Sample data can be added from `sample_data.sql` using;
```python
from app import add_sample_data
add_sample_data()
```

### run server
Start the flask server at http://127.0.0.1:5000 with:

```cli
flask run --port 8000
```
Run in debug with `--debug` - has file watching
Make accessible on the LAN with `--host=0.0.0.0`.