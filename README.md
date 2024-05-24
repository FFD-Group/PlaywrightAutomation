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