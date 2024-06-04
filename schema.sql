CREATE TABLE Suppliers (
    id PRIMARY KEY AUTOINCREMENT INTEGER,
    name UNIQUE VARCHAR(255),
    download_url VARCHAR(255),
    download_path VARCHAR(255),
    FOREIGN KEY (download_type) REFERENCES DownloadTypes(id),
    FOREIGN KEY (file_type) REFERENCES FileTypes(id)
);

CREATE TABLE DownloadTypes (
    id PRIMARY KEY AUTOINCREMENT INTEGER,
    name VARCHAR(255)
);

CREATE TABLE FileTypes (
    id PRIMARY KEY AUTOINCREMENT INTEGER,
    name VARCHAR(255)
);