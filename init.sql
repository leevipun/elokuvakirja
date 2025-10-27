DELETE FROM categories;
INSERT INTO categories (name) VALUES
('Action'),
('Comedy'),
('Drama'),
('Horror'),
('Romance'),
('Sci-Fi'),
('Documentary');

DELETE FROM streaming_platforms;
INSERT INTO streaming_platforms (name) VALUES
('Netflix'),
('Amazon Prime Video'),
('Hulu'),
('Disney+'),
('HBO Max'),
('Apple TV+'),
('Paramount+');

DELETE FROM directors;
INSERT INTO directors (name) VALUES
('Steven Spielberg'),
('Martin Scorsese'),
('Christopher Nolan'),
('Quentin Tarantino'),
('James Cameron'),
('Ridley Scott'),
('Peter Jackson');
