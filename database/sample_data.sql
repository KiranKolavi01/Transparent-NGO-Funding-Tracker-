-- Sample Data for NGO Database

-- Insert Donors
INSERT INTO donors (name, email) VALUES ('Alice Smith', 'alice@example.com');
INSERT INTO donors (name, email) VALUES ('Bob Jones', 'bob@example.com');
INSERT INTO donors (name, email) VALUES ('Charlie Davis', 'charlie@example.com');

-- Insert Donations
INSERT INTO donations (donor_name, project, amount, date) VALUES ('Alice Smith', 'Clean Water Initiative', 250.0, '2026-03-01 10:00:00');
INSERT INTO donations (donor_name, project, amount, date) VALUES ('Bob Jones', 'Education for All', 150.0, '2026-03-05 14:30:00');
INSERT INTO donations (donor_name, project, amount, date) VALUES ('Alice Smith', 'Reforestation Project', 100.0, '2026-03-10 09:15:00');
INSERT INTO donations (donor_name, project, amount, date) VALUES ('Charlie Davis', 'Clean Water Initiative', 500.0, '2026-03-15 16:45:00');
