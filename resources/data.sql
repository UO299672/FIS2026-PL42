-- Carga inicial de datos. Se cargan de maestro a detalle

INSERT INTO Categoria (id_categoria, nombre) VALUES
(1, 'Natación'),
(2, 'Yoga'),
(3, 'Pilates'),
(4, 'Tenis'),
(5, 'Baloncesto'),
(6, 'Spinning');

INSERT INTO Instalacion (id_instalacion, nombre) VALUES
(1, 'Piscina'),
(2, 'Sala 1'),
(3, 'Pista de tenis'),
(4, 'Pabellón'),
(5, 'Gimnasio');   -- sin actividades: todo libre

INSERT INTO Oferta (id_oferta, anio, apertura_socios, cierre_socios, apertura_no_socios, cierre_no_socios) VALUES
(1, 2026, '2026-01-01', '2026-12-31', '2026-01-01', '2026-12-31'),
(2, 2027, '2027-08-25', '2027-09-05', '2027-09-08', '2027-09-20');

INSERT INTO Persona (id_persona, dni_nie, nombre, tipo, numero_socio) VALUES
(1, '12345678A', 'Ana García',      'socio',    1001),
(2, '23456789B', 'Luis Pérez',      'socio',    1002),
(3, '34567890C', 'Marta Díaz',      'socio',    1003),
(4, '45678901D', 'Pablo Ruiz',      'socio',    1004),
(5, '56789012E', 'Lucía Gómez',     'socio',    1005),
(6, '67890123F', 'Carlos Vega',     'no socio', NULL),
(7, '78901234G', 'Elena Mora',      'no socio', NULL),
(8, '89012345H', 'Jorge Ramos',     'no socio', NULL),
(9, 'X1234567L', 'Sofía Müller',    'no socio', NULL);

-- dia_actividad: 1 = lunes ... 7 = domingo
INSERT INTO Actividad (id_actividad, id_oferta, id_categoria, id_instalacion, nivel, hora_inicio, hora_fin, dia_actividad, plazas) VALUES
(1,  1, 1, 1, 'Inicial',    '09:00', '10:00', 1, 3),
(2,  1, 1, 1, 'Avanzado',   '18:00', '19:30', 1, 20),
(3,  1, 1, 1, 'Intermedio', '10:00', '11:00', 3, 10),
(4,  1, 1, 1, 'Inicial',    '17:00', '18:00', 5, 8),
(5,  1, 2, 2, 'Inicial',    '09:30', '11:00', 2, 15),
(6,  1, 3, 2, 'Intermedio', '18:00', '19:00', 4, 12),
(7,  1, 2, 2, 'Avanzado',   '10:00', '12:00', 6, 10),
(8,  1, 6, 2, NULL,         '19:00', '20:00', 1, 20),
(9,  1, 4, 3, 'Inicial',    '09:00', '10:30', 6, 4),
(10, 1, 4, 3, 'Avanzado',   '11:00', '12:30', 7, 4),
(11, 1, 5, 4, NULL,         '19:00', '21:00', 2, 20),
(12, 2, 1, 1, 'Inicial',    '09:00', '10:00', 1, 10);

-- Solo las inscripciones 'confirmada' ocupan plaza
INSERT INTO Inscripcion (id_inscripcion, id_persona, id_actividad, estado, fecha_solicitud) VALUES
(1,  1, 1, 'confirmada', '2026-08-26 10:00:00'),
(2,  2, 1, 'confirmada', '2026-08-26 10:05:00'),
(3,  3, 1, 'confirmada', '2026-08-26 10:10:00'),
(4,  4, 1, 'en espera',  '2026-08-26 10:15:00'),
(5,  1, 2, 'confirmada', '2026-08-27 09:00:00'),
(6,  5, 2, 'confirmada', '2026-08-27 09:30:00'),
(7,  2, 3, 'confirmada', '2026-08-27 11:00:00'),
(8,  6, 3, 'confirmada', '2026-09-08 09:00:00'),
(9,  7, 3, 'cancelada',  '2026-09-08 09:30:00'),
(10, 1, 5, 'confirmada', '2026-08-28 12:00:00'),
(11, 2, 5, 'confirmada', '2026-08-28 12:10:00'),
(12, 3, 5, 'confirmada', '2026-08-28 12:20:00'),
(13, 4, 5, 'confirmada', '2026-08-28 12:30:00'),
(14, 5, 6, 'confirmada', '2026-08-29 08:00:00'),
(15, 8, 7, 'confirmada', '2026-09-09 10:00:00'),
(16, 6, 8, 'confirmada', '2026-09-09 10:30:00'),
(17, 9, 9, 'confirmada', '2026-09-10 10:00:00'),
(18, 8, 9, 'confirmada', '2026-09-10 10:05:00'),
(19, 3, 10,'confirmada', '2026-08-30 10:00:00'),
(20, 4, 11,'confirmada', '2026-08-30 10:30:00'),
(21, 5, 11,'confirmada', '2026-08-30 10:40:00'),
(22, 6, 11,'en espera',  '2026-09-09 11:00:00');