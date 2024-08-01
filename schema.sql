BEGIN TRANSACTION;

DROP TABLE IF EXISTS automations;
DROP TABLE IF EXISTS suppliers;

CREATE TABLE suppliers (
    id UNSIGNED INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE automations (
    id UNSIGNED INTEGER PRIMARY KEY,
    type UNSIGNED INTEGER NOT NULL,
    url VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    supplier_id UNSIGNED INTEGER,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        ON DELETE CASCADE ON UPDATE NO ACTION
);

COMMIT;