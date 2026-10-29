-- Primero se deben borrar todas las tablas (de detalle a maestro) y luego añadirlas (de maestro a detalle)

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
    apertura_socios DATE NOT NULL,
    cierre_socios DATE NOT NULL,
    apertura_no_socios DATE NOT NULL,
    cierre_no_socios DATE NOT NULL
);

CREATE TABLE Persona (
    id_persona INTEGER PRIMARY KEY NOT NULL,
    dni_nie TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('socio', 'no socio')),  -- socio o no socio
    numero_socio INTEGER UNIQUE                                 -- NULL si es no socio
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