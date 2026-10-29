-- Carga inicial de datos

INSERT INTO Categoria (id_categoria, nombre) VALUES
    (1, 'Natación'),
    (2, 'Pilates'),
    (3, 'Acondicionamiento Físico'),
    (4, 'Padel'),
    (5, 'Tenis');

INSERT INTO Instalacion (id_instalacion, nombre) VALUES
    (1, 'Piscina'),
    (2, 'Sala polivalente'),
    (3, 'Gimnasio'),
    (4, 'Pista de padel'),
    (5, 'Pista de tenis');

INSERT INTO Oferta (id_oferta, anio, apertura_socios, cierre_socios, apertura_no_socios, cierre_no_socios) VALUES
    (1, 2027, '2027-01-10', '2027-01-20', '2027-01-21', '2027-01-31');
