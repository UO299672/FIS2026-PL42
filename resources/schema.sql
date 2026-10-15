-- Primero se deben borrar todas las tablas (de detalle a maestro) y luego añadirlas (de maestro a detalle)
drop table if exists HistorialInscripcion;
drop table if exists Inscripcion;
drop table if exists PeriodoInscripcion;
drop table if exists ActividadDia;
drop table if exists Actividad;
drop table if exists Persona;
drop table if exists Instalacion;
drop table if exists Categoria;
 
-- Las maestro son las que son más simples, no tienen FK.
 
-- Tabla para gestionar las categorias de actividad (catalogo fijo en este sprint)
CREATE TABLE Categoria (
    id_categoria INTEGER PRIMARY KEY NOT NULL,
    nombre_categoria VARCHAR(255) NOT NULL UNIQUE      -- Natacion, Pilates, Acondicionamiento Fisico, Padel, Tenis
);
 
-- Tabla para gestionar las instalaciones del centro deportivo
CREATE TABLE Instalacion (
    id_instalacion INTEGER PRIMARY KEY NOT NULL,
    nombre_instalacion VARCHAR(255) NOT NULL UNIQUE
);
 
-- Tabla para gestionar las personas usuarias (socios y no socios)
CREATE TABLE Persona (
    id_persona INTEGER PRIMARY KEY AUTOINCREMENT,
    dni_nie VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(255) NOT NULL,
    apellidos VARCHAR(255) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    correo TEXT NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    tipo_persona TEXT NOT NULL CHECK (tipo_persona IN ('SOCIO', 'NO_SOCIO')),
    numero_socio INTEGER UNIQUE,                       -- solo si tipo_persona = 'SOCIO'
    CHECK ((tipo_persona = 'SOCIO' AND numero_socio IS NOT NULL)
        OR (tipo_persona = 'NO_SOCIO' AND numero_socio IS NULL))
);
 
-- Tabla para gestionar las actividades de la oferta
CREATE TABLE Actividad (
    id_actividad INTEGER PRIMARY KEY AUTOINCREMENT,
    id_categoria INTEGER NOT NULL,
    id_instalacion INTEGER,                            -- se asigna despues de crear la actividad (puede ser NULL)
    nivel TEXT NOT NULL CHECK (nivel IN ('INICIACION', 'MEDIO', 'AVANZADO')),
    hora_inicio TEXT NOT NULL,                         -- formato HH:MM
    hora_fin TEXT NOT NULL,                            -- formato HH:MM
    plazas_totales INTEGER NOT NULL CHECK (plazas_totales > 0),
    fecha_primera_sesion DATE NOT NULL,
    CHECK (hora_inicio < hora_fin),
    FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria),
    FOREIGN KEY (id_instalacion) REFERENCES Instalacion(id_instalacion)
);
 
-- Tabla para los dias de la semana en que se imparte cada actividad (misma hora para todos los dias)
CREATE TABLE ActividadDia (
    id_actividad_dia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_actividad INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),   -- 1 = lunes ... 7 = domingo
    UNIQUE (id_actividad, dia_semana),
    FOREIGN KEY (id_actividad) REFERENCES Actividad(id_actividad)
);
 
-- Tabla para los periodos de inscripcion de cada actividad (uno para socios y otro para no socios)
CREATE TABLE PeriodoInscripcion (
    id_periodo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_actividad INTEGER NOT NULL,
    tipo_persona TEXT NOT NULL CHECK (tipo_persona IN ('SOCIO', 'NO_SOCIO')),
    fecha_apertura DATE NOT NULL,
    fecha_cierre DATE NOT NULL,
    UNIQUE (id_actividad, tipo_persona),
    CHECK (fecha_apertura <= fecha_cierre),
    FOREIGN KEY (id_actividad) REFERENCES Actividad(id_actividad)
);
 
-- Tabla para gestionar las inscripciones de las personas en las actividades
CREATE TABLE Inscripcion (
    id_inscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_persona INTEGER NOT NULL,
    id_actividad INTEGER NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('CONFIRMADA', 'EN_LISTA_ESPERA', 'CANCELADA')),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- fecha y hora de la inscripcion o de entrada en lista de espera
    fecha_cancelacion TIMESTAMP,                           -- solo si estado = 'CANCELADA'
    FOREIGN KEY (id_persona) REFERENCES Persona(id_persona),
    FOREIGN KEY (id_actividad) REFERENCES Actividad(id_actividad)
);
 
-- Una persona solo puede tener una inscripcion activa por actividad (si cancela, puede volver a inscribirse)
CREATE UNIQUE INDEX IF NOT EXISTS idx_inscripcion_activa
    ON Inscripcion (id_persona, id_actividad)
    WHERE estado <> 'CANCELADA';
 
-- Tabla para el historico de cambios de estado de las inscripciones
CREATE TABLE HistorialInscripcion (
    id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
    id_inscripcion INTEGER NOT NULL,
    estado_anterior TEXT,                                  -- NULL en el primer registro
    estado_nuevo TEXT NOT NULL,
    motivo TEXT NOT NULL,                                  -- inscripcion / cancelacion / promocion desde lista de espera
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_inscripcion) REFERENCES Inscripcion(id_inscripcion)
);