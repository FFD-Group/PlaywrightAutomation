BEGIN TRANSACTION;

DROP TABLE IF EXISTS automations;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS steps;
DROP TABLE IF EXISTS uploads;
DROP TABLE IF EXISTS processing_options;

CREATE TABLE suppliers (
    id UNSIGNED INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id UNSIGNED INTEGER,
    filename TEXT NOT NULL,
    uploaded_at FLOAT NOT NULL,
    processed UNSIGNED INTEGER NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
);

CREATE TABLE automations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type UNSIGNED INTEGER NOT NULL,
    url TEXT NOT NULL,
    location TEXT NOT NULL,
    name TEXT NOT NULL,
    schedule TEXT,
    last_run_result TEXT,
    supplier_id UNSIGNED INTEGER,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
);

CREATE TABLE processing_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    options TEXT NOT NULL,
    automation_id UNSIGNED INTEGER UNIQUE,
    FOREIGN KEY (automation_id) REFERENCES automations(id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
);

CREATE TABLE steps (
    automation_id INTEGER PRIMARY KEY,
    automation_steps TEXT NOT NULL,
    FOREIGN KEY (automation_id) REFERENCES automations(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

COMMIT;