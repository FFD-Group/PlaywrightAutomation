BEGIN TRANSACTION;

DROP TABLE IF EXISTS automations;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS steps;

CREATE TABLE suppliers (
    id UNSIGNED INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE automations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type UNSIGNED INTEGER NOT NULL,
    url VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    schedule VARCHAR(255),
    last_run_result VARCHAR(255),
    supplier_id UNSIGNED INTEGER,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
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