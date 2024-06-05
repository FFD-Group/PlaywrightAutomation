BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS download_types (
    download_type_id UNSIGNED INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS file_types (
    file_type_id UNSIGNED INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Suppliers (
    supplier_id UNSIGNED INTEGER PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    download_url VARCHAR(255),
    download_path VARCHAR(255) NOT NULL,
    download_type_id INTEGER NOT NULL,
    file_type_id INTEGER NOT NULL,
    FOREIGN KEY (download_type_id) REFERENCES download_types(download_type_id)
        ON DELETE CASCADE ON UPDATE NO ACTION,
    FOREIGN KEY (file_type_id) REFERENCES file_types(file_type_id)
    ON DELETE CASCADE ON UPDATE NO ACTION
);

COMMIT;