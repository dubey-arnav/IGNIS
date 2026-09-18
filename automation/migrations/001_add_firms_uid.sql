-- automation/migrations/001_add_firms_uid.sql
-- Safe to run more than once.
ALTER TABLE thermal_events ADD COLUMN IF NOT EXISTS firms_uid TEXT;
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_thermal_events_firms_uid'
    ) THEN
        ALTER TABLE thermal_events ADD CONSTRAINT uq_thermal_events_firms_uid UNIQUE (firms_uid);
    END IF;
END $$;
