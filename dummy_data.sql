-- =======================
-- USERS
-- =======================

INSERT INTO users (name, email, password, role, status, aadhaar, dob, gender, address)
VALUES
('Rahul Patel', 'rahul@gmail.com', '1234', 'citizen', 'active', '1234-5678-9012', '2002-05-14', 'Male', 'Sector 21, Gandhinagar'),
('Neha Sharma', 'neha@gmail.com', '1234', 'citizen', 'active', '2345-6789-0123', '2001-11-02', 'Female', 'Maninagar, Ahmedabad'),
('Amit Verma', 'amit@gmail.com', '1234', 'citizen', 'active', '3456-7890-1234', '2000-08-19', 'Male', 'Alkapuri, Vadodara'),
('Karan Shah', 'karan@gmail.com', '1234', 'citizen', 'active', '4567-8901-2345', '2002-01-10', 'Male', 'Paldi, Ahmedabad'),
('Pooja Mehta', 'pooja@gmail.com', '1234', 'citizen', 'active', '5678-9012-3456', '2001-06-30', 'Female', 'Satellite, Ahmedabad');

-- Government Officers
INSERT INTO users (name, email, password, role, gov_id, status)
VALUES
('Rahul Verma', 'rahul@gov.in', '1234', 'government', 'W-101', 'active'),
('Sunita Joshi', 'sunita@gov.in', '1234', 'government', 'S-102', 'active'),
('Anil Desai', 'anil@gov.in', '1234', 'government', 'P-103', 'active'),
('Maya Patel', 'maya@gov.in', '1234', 'government', 'E-104', 'active');

-- COMPLAINTS

INSERT INTO complaints
(title, description, location, department, citizen_id, priority, status, image, date)
VALUES
(
 'Garbage Overflow Near Society',
 'Garbage bins are overflowing for the last 3 days causing foul smell.',
 'Sector 21, Gandhinagar',
 'Sanitation',
 1,
 'High',
 'Pending',
 NULL,
 '2024-01-15'
),
(
 'Street Light Not Working',
 'Street light outside my house is not working at night.',
 'Maninagar East, Ahmedabad',
 'Electricity',
 2,
 'Medium',
 'In Progress',
 NULL,
 '2024-01-16'
),
(
 'Water Leakage on Road',
 'Continuous water leakage damaging the road surface.',
 'Alkapuri Main Road, Vadodara',
 'Water Supply',
 3,
 'High',
 'Pending',
 NULL,
 '2024-01-17'
),
(
 'Potholes After Rain',
 'Large potholes causing traffic jams and accidents.',
 'Paldi Cross Road, Ahmedabad',
 'Public Works',
 4,
 'High',
 'Resolved',
 NULL,
 '2024-01-10'
),
(
 'Irregular Garbage Collection',
 'Garbage collection vehicle does not come regularly.',
 'Satellite Area, Ahmedabad',
 'Sanitation',
 5,
 'Low',
 'Pending',
 NULL,
 '2024-01-18'
),
(
 'Broken Drainage Cover',
 'Open drainage cover is dangerous for pedestrians.',
 'Sector 7, Gandhinagar',
 'Public Works',
 1,
 'Medium',
 'In Progress',
 NULL,
 '2024-01-12'
),
(
 'Water Supply Disruption',
 'No water supply since morning.',
 'Naranpura, Ahmedabad',
 'Water Supply',
 2,
 'High',
 'Pending',
 NULL,
 '2024-01-19'
),
(
 'Street Light Flickering',
 'Light keeps flickering and turns off.',
 'Ring Road, Ahmedabad',
 'Electricity',
 3,
 'Low',
 'Resolved',
 NULL,
 '2024-01-08'
);
