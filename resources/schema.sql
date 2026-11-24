-- Primero se deben borrar todas las tablas (de detalle a maestro) y luego añadirlas (de maestro a detalle)

drop table if exists Recibo;
drop table if exists Remesa;
drop table if exists Inscripcion;
drop table if exists Actividad;
drop table if exists Oferta;
drop table if exists Persona;
drop table if exists Instalacion;
drop table if exists Categoria;

CREATE TABLE Categoria (
    id_categoria INTEGER PRIMARY KEY NOT NULL,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE Instalacion (
    id_instalacion INTEGER PRIMARY KEY NOT NULL,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE Oferta (
    id_oferta INTEGER PRIMARY KEY NOT NULL,
    anio INTEGER NOT NULL UNIQUE,
    apertura_socios DATE,
    cierre_socios DATE,
    apertura_no_socios DATE,
    cierre_no_socios DATE
);

CREATE TABLE Persona (
    id_persona INTEGER PRIMARY KEY NOT NULL,
    dni_nie TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('socio', 'no socio')),  -- socio o no socio
    numero_socio INTEGER UNIQUE,                                -- NULL si es no socio
    cuenta_bancaria TEXT                                        -- IBAN donde se cargan los recibos
);

CREATE TABLE Actividad (
    id_actividad INTEGER PRIMARY KEY NOT NULL,
    id_oferta INTEGER NOT NULL,
    id_categoria INTEGER NOT NULL,
    id_instalacion INTEGER,
    nivel TEXT,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,                                     -- formato HH:MM
    dia_actividad INTEGER NOT NULL CHECK (dia_actividad BETWEEN 1 AND 7),  -- 1 = lunes ... 7 = domingo
    plazas INTEGER NOT NULL CHECK (plazas >= 0),
    fecha_inicio DATE,                                          -- primer día en que se imparte
    fecha_fin DATE,                                             -- último día en que se imparte
    precio_socio REAL NOT NULL DEFAULT 0,                       -- cuota mensual para socios
    precio_no_socio REAL NOT NULL DEFAULT 0,                    -- cuota mensual para no socios
    FOREIGN KEY (id_oferta) REFERENCES Oferta(id_oferta),
    FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria),
    FOREIGN KEY (id_instalacion) REFERENCES Instalacion(id_instalacion)
);

CREATE TABLE Inscripcion (
    id_inscripcion INTEGER PRIMARY KEY NOT NULL,
    id_persona INTEGER NOT NULL,
    id_actividad INTEGER NOT NULL,
    estado TEXT CHECK (estado IN ('confirmada', 'en espera', 'cancelada')),  -- 'confirmada' ocupa plaza
    fecha_solicitud DATETIME NOT NULL,
    FOREIGN KEY (id_actividad) REFERENCES Actividad(id_actividad),
    FOREIGN KEY (id_persona) REFERENCES Persona(id_persona)
);

CREATE TABLE Remesa (
    id_remesa INTEGER PRIMARY KEY NOT NULL,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    fecha_emision DATE NOT NULL,
    UNIQUE (anio, mes)                                          -- una sola remesa por mes
);

CREATE TABLE Recibo (
    id_recibo INTEGER PRIMARY KEY NOT NULL,
    id_remesa INTEGER NOT NULL,
    id_inscripcion INTEGER NOT NULL,
    importe REAL NOT NULL,
    cuenta_bancaria TEXT,
    fecha_emision DATE NOT NULL,
    estado TEXT NOT NULL DEFAULT 'emitido' CHECK (estado IN ('emitido')),
    FOREIGN KEY (id_remesa) REFERENCES Remesa(id_remesa),
    FOREIGN KEY (id_inscripcion) REFERENCES Inscripcion(id_inscripcion)
);
