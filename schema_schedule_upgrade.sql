-- Add schedule fields to automations table (idempotent-ish for SQLite)
-- NOTE: SQLite doesn't support IF NOT EXISTS on ADD COLUMN, so if you re-run this
-- you'll get "duplicate column" errors. Only run once.

ALTER TABLE automations ADD COLUMN schedule_time TEXT;
ALTER TABLE automations ADD COLUMN schedule_enabled INTEGER NOT NULL DEFAULT 0;
