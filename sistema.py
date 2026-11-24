from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, time
from typing import Dict, List, Optional


# ==========================================
# MÓDULO DE PERSONAS Y SEGURIDAD
# ==========================================

class Persona(ABC):
    """Clase abstracta base para entidades demográficas."""

    def __init__(
        self,
        id_persona: str,
        documento: str,
        nombres: str,
        apellidos: str,
        correo: str,
        telefono: str,
    ) -> None:
        self._id: str = id_persona
        self._documento: str = documento
        self.nombres: str = nombres
        self.apellidos: str = apellidos
        self.correo: str = correo
        self.telefono: str = telefono
        self._usuario: Optional[Usuario] = None

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor: str) -> None:
        self._documento = valor

    @property
    def usuario(self) -> Optional[Usuario]:
        return self._usuario

    @usuario.setter
    def usuario(self, usr: Optional[Usuario]) -> None:
        self._usuario = usr

    def get_nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}".strip()

    def actualizar_datos(self, correo: str, telefono: str) -> bool:
        if not correo or not telefono:
            return False
        self.correo = correo
        self.telefono = telefono
        return True

    @abstractmethod
    def describir_rol(self) -> str:
        pass

    def __str__(self) -> str:
        return f"[{self._id}] {self.get_nombre_completo()} (Doc: {self._documento})"


class Estudiante(Persona):
    """Hereda de Persona y representa al alumno inscrito."""

    def __init__(
        self,
        id_persona: str,
        documento: str,
        nombres: str,
        apellidos: str,
        correo: str,
        telefono: str,
        codigo_estudiantil: str,
        fecha_ingreso: date,
    ) -> None:
        super().__init__(id_persona, documento, nombres, apellidos, correo, telefono)
        self._codigo_estudiantil: str = codigo_estudiantil.strip()
        self.fecha_ingreso: date = fecha_ingreso
        self.matriculas: List[Matricula] = []
        self.calificaciones: List[Calificacion] = []
        self.asistencias: List[Asistencia] = []
        self._asignaturas_aprobadas: List[str] = []

    @property
    def codigo_estudiantil(self) -> str:
        return self._codigo_estudiantil

    @codigo_estudiantil.setter
    def codigo_estudiantil(self, codigo: str) -> None:
        self._codigo_estudiantil = codigo.strip()

    def registrar_asignatura_aprobada(self, asignatura_id: str) -> None:
        if asignatura_id not in self._asignaturas_aprobadas:
            self._asignaturas_aprobadas.append(asignatura_id)

    def consultar_promedio(self, calificaciones_filtradas: Optional[List[Calificacion]] = None) -> float:
        lista = calificaciones_filtradas if calificaciones_filtradas is not None else self.calificaciones
        if not lista:
            return 0.0
        total = sum(c.nota_obtenida for c in lista)
        return round(total / len(lista), 2)

    def validar_prerrequisitos(self, materia_id: str, catalogo_asignaturas: Dict[str, Asignatura]) -> bool:
        materia = catalogo_asignaturas.get(materia_id)
        if not materia:
            return False
        for req in materia.obtener_prerrequisitos():
            if req.id not in self._asignaturas_aprobadas:
                return False
        return True

    def describir_rol(self) -> str:
        return f"Estudiante ({self._codigo_estudiantil})"


class Docente(Persona):
    """Hereda de Persona y representa al profesor."""

    def __init__(
        self,
        id_persona: str,
        documento: str,
        nombres: str,
        apellidos: str,
        correo: str,
        telefono: str,
        titulo_academico: str,
        departamento: str,
    ) -> None:
        super().__init__(id_persona, documento, nombres, apellidos, correo, telefono)
        self.titulo_academico: str = titulo_academico
        self.departamento: str = departamento
        self.registros_docente: List[RegistroDocente] = []

    def registrar_nota(
        self,
        evaluacion_id: str,
        estudiante: Estudiante,
        nota: float,
        id_calificacion: str = "CAL-AUTO",
        observacion: str = "Registrada por docente",
        grupo_id: Optional[str] = None,
        asignatura_id: Optional[str] = None,
    ) -> Calificacion:
        cal = Calificacion(
            id_calificacion,
            evaluacion_id,
            estudiante.id,
            nota,
            observacion,
            grupo_id=grupo_id,
            asignatura_id=asignatura_id,
        )
        estudiante.calificaciones.append(cal)
        return cal

    def describir_rol(self) -> str:
        return f"Docente - {self.titulo_academico} ({self.departamento})"


class Usuario:
    """Gestiona credenciales y acceso vinculada a una Persona."""

    def __init__(
        self,
        id_usuario: str,
        persona_id: str,
        username: str,
        password_hash: str,
        rol: str,
        estado: bool = True,
        persona: Optional[Persona] = None,
    ) -> None:
        self._id: str = id_usuario
        self._persona_id: str = persona_id
        self.username: str = username
        self._password_hash: str = password_hash
        self.rol: str = rol
        self.estado: bool = estado
        self.persona: Optional[Persona] = persona
        if persona is not None:
            persona.usuario = self

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    @property
    def persona_id(self) -> str:
        return self._persona_id

    @persona_id.setter
    def persona_id(self, valor: str) -> None:
        self._persona_id = valor

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @password_hash.setter
    def password_hash(self, nuevo_hash: str) -> None:
        self._password_hash = nuevo_hash

    def autenticar(self, password: str) -> bool:
        return self.estado and (self._password_hash == password)

    def cambiar_password(self, old_pass: str, new_pass: str) -> bool:
        if self._password_hash == old_pass and len(new_pass) >= 4:
            self._password_hash = new_pass
            return True
        return False

    def __str__(self) -> str:
        estado_txt = "ACTIVO" if self.estado else "INACTIVO"
        return f"Usuario[{self._id}] @{self.username} | Rol: {self.rol} | {estado_txt}"


# ==========================================
# MÓDULO ACADÉMICO ESTRUCTURAL
# ==========================================

class ProgramaAcademico:
    """Representa una carrera o programa académico."""

    def __init__(
        self,
        id_programa: str,
        nombre: str,
        codigo: str,
        duracion_semestres: int,
    ) -> None:
        self._id: str = id_programa
        self.nombre: str = nombre
        self.codigo: str = codigo
        self.duracion_semestres: int = duracion_semestres
        self.asignaturas: List[Asignatura] = []

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    def agregar_materia(self, materia: Asignatura) -> None:
        if materia not in self.asignaturas:
            self.asignaturas.append(materia)

    def __str__(self) -> str:
        return f"Programa[{self._id}] {self.nombre} ({self.codigo}) - {self.duracion_semestres} sem."


class Asignatura:
    """Representa una materia con relación reflexiva de prerrequisitos."""

    def __init__(
        self,
        id_asignatura: str,
        nombre: str,
        creditos: int,
        programa_id: str,
        prerrequisitos: Optional[List[Asignatura]] = None,
    ) -> None:
        self._id: str = id_asignatura
        self.nombre: str = nombre
        self.creditos: int = creditos
        self._programa_id: str = programa_id
        self.prerrequisitos: List[Asignatura] = prerrequisitos if prerrequisitos is not None else []
        self.grupos: List[Grupo] = []

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    @property
    def programa_id(self) -> str:
        return self._programa_id

    @programa_id.setter
    def programa_id(self, valor: str) -> None:
        self._programa_id = valor

    def obtener_prerrequisitos(self) -> List[Asignatura]:
        return list(self.prerrequisitos)

    def agregar_prerrequisito(self, asignatura: Asignatura) -> None:
        if asignatura not in self.prerrequisitos and asignatura is not self:
            self.prerrequisitos.append(asignatura)

    def __str__(self) -> str:
        return f"Asignatura[{self._id}] {self.nombre} ({self.creditos} cr.)"


class PeriodoAcademico:
    """Representa el ciclo lectivo (ej. 2026-1)."""

    def __init__(
        self,
        id_periodo: str,
        nombre: str,
        fecha_inicio: date,
        fecha_fin: date,
        activo: bool = True,
    ) -> None:
        self._id: str = id_periodo
        self.nombre: str = nombre
        self.fecha_inicio: date = fecha_inicio
        self.fecha_fin: date = fecha_fin
        self.activo: bool = activo
        self.grupos: List[Grupo] = []
        self.periodos_matricula: List[PeriodoMatricula] = []

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    def es_periodo_vigente(self) -> bool:
        hoy = date.today()
        return self.activo and (self.fecha_inicio <= hoy <= self.fecha_fin)

    def __str__(self) -> str:
        return f"Periodo[{self._id}] {self.nombre} ({self.fecha_inicio} a {self.fecha_fin})"


class PeriodoMatricula:
    """Controla fechas habilitadas para inscripción."""

    def __init__(
        self,
        id_periodo_matricula: str,
        periodo_id: str,
        fecha_inicio_matricula: date,
        fecha_fin_matricula: date,
    ) -> None:
        self._id: str = id_periodo_matricula
        self._periodo_id: str = periodo_id
        self.fecha_inicio_matricula: date = fecha_inicio_matricula
        self.fecha_fin_matricula: date = fecha_fin_matricula

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    @property
    def periodo_id(self) -> str:
        return self._periodo_id

    @periodo_id.setter
    def periodo_id(self, valor: str) -> None:
        self._periodo_id = valor

    def esta_habilitado(self) -> bool:
        hoy = date.today()
        return self.fecha_inicio_matricula <= hoy <= self.fecha_fin_matricula

    def __str__(self) -> str:
        return f"PeriodoMatricula[{self._id}] ({self.fecha_inicio_matricula} - {self.fecha_fin_matricula})"


# ==========================================
# MÓDULO DE CURSOS Y AULAS
# ==========================================

class Grupo:
    """Sección de una asignatura ofertada en un período."""

    def __init__(
        self,
        id_grupo: str,
        materia_id: str,
        periodo_id: str,
        cupo_maximo: int,
        asignatura: Optional[Asignatura] = None,
    ) -> None:
        self._id: str = id_grupo
        self._materia_id: str = materia_id
        self._periodo_id: str = periodo_id
        self.cupo_maximo: int = cupo_maximo
        self.asignatura: Optional[Asignatura] = asignatura
        self.registro_docente: Optional[RegistroDocente] = None
        self.horarios: List[Horario] = []
        self.inscripciones: List[InscripcionAsignatura] = []
        self.evaluaciones: List[Evaluacion] = []
        self.asistencias: List[Asistencia] = []

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    @property
    def materia_id(self) -> str:
        return self._materia_id

    @materia_id.setter
    def materia_id(self, valor: str) -> None:
        self._materia_id = valor

    @property
    def periodo_id(self) -> str:
        return self._periodo_id

    @periodo_id.setter
    def periodo_id(self, valor: str) -> None:
        self._periodo_id = valor

    def verificar_cupo(self) -> bool:
        activos = sum(1 for ins in self.inscripciones if ins.estado_asignatura != "RETIRADA")
        return activos < self.cupo_maximo

    def inscribir_estudiante(self) -> bool:
        return self.verificar_cupo()

    def __str__(self) -> str:
        materia_txt = self.asignatura.nombre if self.asignatura else self._materia_id
        return f"Grupo[{self._id}] {materia_txt} | Cupo:{len(self.inscripciones)}/{self.cupo_maximo}"


class RegistroDocente:
    """Asigna un docente a un grupo."""

    def __init__(
        self,
        id_registro: str,
        docente_id: str,
        grupo_id: str,
        fecha_asignacion: date,
        horas_semanales: int = 4,
        max_horas_permitidas: int = 20,
    ) -> None:
        self._id: str = id_registro
        self._docente_id: str = docente_id
        self._grupo_id: str = grupo_id
        self.fecha_asignacion: date = fecha_asignacion
        self.horas_semanales: int = horas_semanales
        self.max_horas_permitidas: int = max_horas_permitidas

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    @property
    def docente_id(self) -> str:
        return self._docente_id

    @docente_id.setter
    def docente_id(self, valor: str) -> None:
        self._docente_id = valor

    @property
    def grupo_id(self) -> str:
        return self._grupo_id

    @grupo_id.setter
    def grupo_id(self, valor: str) -> None:
        self._grupo_id = valor

    def confirmar_carga_horaria(self) -> bool:
        return self.horas_semanales <= self.max_horas_permitidas

    def __str__(self) -> str:
        return f"RegistroDocente[{self._id}] Docente:{self._docente_id} -> Grupo:{self._grupo_id}"


class Aula:
    """Espacio físico o aula virtual."""

    def __init__(
        self,
        id_aula: str,
        bloque: str,
        numero: str,
        capacidad: int,
        es_virtual: bool = False,
    ) -> None:
        self._id: str = id_aula
        self.bloque: str = bloque
        self.numero: str = numero
        self.capacidad: int = capacidad
        self.es_virtual: bool = es_virtual
        self.horarios: List[Horario] = []

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    def validar_disponibilidad(self, dia: str, hora: str) -> bool:
        for h in self.horarios:
            if h.dia_semana.upper() == dia.upper() and str(h.hora_inicio) <= hora <= str(h.hora_fin):
                return False
        return True

    def __str__(self) -> str:
        tipo = "Virtual" if self.es_virtual else "Física"
        return f"Aula[{self._id}] {self.bloque}-{self.numero} ({tipo}, cap. {self.capacidad})"


class Horario:
    """Franja horaria asignada a un grupo en un aula."""

    def __init__(
        self,
        id_horario: str,
        grupo_id: str,
        aula_id: str,
        dia_semana: str,
        hora_inicio: time,
        hora_fin: time,
    ) -> None:
        self._id: str = id_horario
        self._grupo_id: str = grupo_id
        self._aula_id: str = aula_id
        self.dia_semana: str = dia_semana
        self.hora_inicio: time = hora_inicio
        self.hora_fin: time = hora_fin

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    @property
    def grupo_id(self) -> str:
        return self._grupo_id

    @grupo_id.setter
    def grupo_id(self, valor: str) -> None:
        self._grupo_id = valor

    @property
    def aula_id(self) -> str:
        return self._aula_id

    @aula_id.setter
    def aula_id(self, valor: str) -> None:
        self._aula_id = valor

    def consultar_cruces(self, otros_horarios: Optional[List[Horario]] = None) -> bool:
        if not otros_horarios:
            return False
        for otro in otros_horarios:
            if otro is self:
                continue
            if otro._aula_id == self._aula_id and otro.dia_semana.upper() == self.dia_semana.upper():
                if self.hora_inicio < otro.hora_fin and otro.hora_inicio < self.hora_fin:
                    return True
        return False

    def __str__(self) -> str:
        return f"Horario[{self._id}] {self.dia_semana} {self.hora_inicio}-{self.hora_fin} (Aula:{self._aula_id})"


# ==========================================
# MÓDULO DE MATRÍCULA Y EVALUACIONES
# ==========================================

class Matricula:
    """Registro de matrícula del estudiante en un período."""

    def __init__(
        self,
        id_matricula: str,
        estudiante_id: str,
        periodo_id: str,
        fecha_matricula: date,
        costo_total: float = 0.0,
        valor_credito: float = 150000.0,
    ) -> None:
        self._id: str = id_matricula
        self._estudiante_id: str = estudiante_id
        self._periodo_id: str = periodo_id
        self.fecha_matricula: date = fecha_matricula
        self.costo_total: float = costo_total
        self._valor_credito: float = valor_credito
        self.pagada: bool = False
        self.inscripciones: List[InscripcionAsignatura] = []

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    @property
    def estudiante_id(self) -> str:
        return self._estudiante_id

    @estudiante_id.setter
    def estudiante_id(self, valor: str) -> None:
        self._estudiante_id = valor

    @property
    def periodo_id(self) -> str:
        return self._periodo_id

    @periodo_id.setter
    def periodo_id(self, valor: str) -> None:
        self._periodo_id = valor

    def calcular_costo(self, creditos_inscritos: Optional[int] = None) -> float:
        if creditos_inscritos is not None:
            self.costo_total = creditos_inscritos * self._valor_credito
        else:
            activas = [i for i in self.inscripciones if i.estado_asignatura != "RETIRADA"]
            creditos = sum(i.grupo.asignatura.creditos for i in activas if i.grupo and i.grupo.asignatura)
            self.costo_total = creditos * self._valor_credito
        return self.costo_total

    def confirmar_pago(self) -> None:
        self.pagada = True

    def __str__(self) -> str:
        estado_pago = "PAGADA" if self.pagada else "PENDIENTE"
        return f"Matricula[{self._id}] Est:{self._estudiante_id} | Costo:${self.costo_total:,.0f} ({estado_pago})"


class InscripcionAsignatura:
    """Detalle de inscripción de un grupo dentro de una matrícula."""

    def __init__(
        self,
        id_inscripcion: str,
        matricula_id: str,
        grupo_id: str,
        estado_asignatura: str = "CURSANDO",
        grupo: Optional[Grupo] = None,
    ) -> None:
        self._id: str = id_inscripcion
        self._matricula_id: str = matricula_id
        self._grupo_id: str = grupo_id
        self.estado_asignatura: str = estado_asignatura
        self.grupo: Optional[Grupo] = grupo
        if grupo is not None:
            grupo.inscripciones.append(self)

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    @property
    def matricula_id(self) -> str:
        return self._matricula_id

    @matricula_id.setter
    def matricula_id(self, valor: str) -> None:
        self._matricula_id = valor

    @property
    def grupo_id(self) -> str:
        return self._grupo_id

    @grupo_id.setter
    def grupo_id(self, valor: str) -> None:
        self._grupo_id = valor

    def retirar_asignatura(self) -> None:
        self.estado_asignatura = "RETIRADA"

    def __str__(self) -> str:
        return f"Inscripcion[{self._id}] Grupo:{self._grupo_id} | Estado:{self.estado_asignatura}"


class Evaluacion:
    """Actividad evaluativa de un grupo."""

    def __init__(
        self,
        id_evaluacion: str,
        grupo_id: str,
        titulo: str,
        porcentaje_peso: float,
        fecha_entrega: date,
    ) -> None:
        self._id: str = id_evaluacion
        self._grupo_id: str = grupo_id
        self.titulo: str = titulo
        self.porcentaje_peso: float = porcentaje_peso
        self.fecha_entrega: date = fecha_entrega
        self.calificaciones: List[Calificacion] = []

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    @property
    def grupo_id(self) -> str:
        return self._grupo_id

    @grupo_id.setter
    def grupo_id(self, valor: str) -> None:
        self._grupo_id = valor

    def validar_porcentaje(self, acumulado_grupo: float = 0.0) -> bool:
        return (acumulado_grupo + self.porcentaje_peso) <= 100.0 and self.porcentaje_peso > 0

    def __str__(self) -> str:
        return f"Evaluacion[{self._id}] {self.titulo} ({self.porcentaje_peso}%) - Entrega:{self.fecha_entrega}"


class Calificacion:
    """Nota de un estudiante en una evaluación."""

    def __init__(
        self,
        id_calificacion: str,
        evaluacion_id: str,
        estudiante_id: str,
        nota_obtenida: float,
        observacion: str = "",
        grupo_id: Optional[str] = None,
        asignatura_id: Optional[str] = None,
    ) -> None:
        self._id: str = id_calificacion
        self._evaluacion_id: str = evaluacion_id
        self._estudiante_id: str = estudiante_id
        self.nota_obtenida: float = nota_obtenida
        self.observacion: str = observacion
        self.grupo_id: Optional[str] = grupo_id
        self.asignatura_id: Optional[str] = asignatura_id

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    @property
    def evaluacion_id(self) -> str:
        return self._evaluacion_id

    @evaluacion_id.setter
    def evaluacion_id(self, valor: str) -> None:
        self._evaluacion_id = valor

    @property
    def estudiante_id(self) -> str:
        return self._estudiante_id

    @estudiante_id.setter
    def estudiante_id(self, valor: str) -> None:
        self._estudiante_id = valor

    def editar_nota(self, nueva_nota: float) -> None:
        if 0.0 <= nueva_nota <= 5.0:
            self.nota_obtenida = nueva_nota

    def __str__(self) -> str:
        extra = ""
        if self.asignatura_id or self.grupo_id:
            extra = f" | Asig:{self.asignatura_id or '-'} / Grp:{self.grupo_id or '-'}"
        return f"Calificacion[{self._id}] Est:{self._estudiante_id} | Nota:{self.nota_obtenida}{extra}"


class Asistencia:
    """Registro de asistencia de un estudiante en un grupo."""

    def __init__(
        self,
        id_asistencia: str,
        grupo_id: str,
        estudiante_id: str,
        fecha: date,
        presente: bool = True,
    ) -> None:
        self._id: str = id_asistencia
        self._grupo_id: str = grupo_id
        self._estudiante_id: str = estudiante_id
        self.fecha: date = fecha
        self.presente: bool = presente

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        self._id = valor

    @property
    def grupo_id(self) -> str:
        return self._grupo_id

    @grupo_id.setter
    def grupo_id(self, valor: str) -> None:
        self._grupo_id = valor

    @property
    def estudiante_id(self) -> str:
        return self._estudiante_id

    @estudiante_id.setter
    def estudiante_id(self, valor: str) -> None:
        self._estudiante_id = valor

    def registrar_falta(self) -> None:
        self.presente = False

    def __str__(self) -> str:
        estado = "Asistió" if self.presente else "Faltó"
        return f"Asistencia[{self._id}] {self.fecha} | Est:{self._estudiante_id} | {estado}"


# ==========================================
# MENÚ PRINCIPAL
# ==========================================

class SistemaAcademicoApp:
    def __init__(self) -> None:
        self.estudiantes: List[Estudiante] = []
        self.docentes: List[Docente] = []
        self.usuarios: List[Usuario] = []
        self.programas: List[ProgramaAcademico] = []
        self.asignaturas: List[Asignatura] = []
        self.periodos: List[PeriodoAcademico] = []
        self.periodos_matricula: List[PeriodoMatricula] = []
        self.grupos: List[Grupo] = []
        self.registros_docente: List[RegistroDocente] = []
        self.aulas: List[Aula] = []
        self.horarios: List[Horario] = []
        self.matriculas: List[Matricula] = []
        self.inscripciones: List[InscripcionAsignatura] = []
        self.evaluaciones: List[Evaluacion] = []
        self.calificaciones: List[Calificacion] = []
        self.asistencias: List[Asistencia] = []
        self.cargar_datos_iniciales()

    def cargar_datos_iniciales(self) -> None:
        """Carga datos precargados y relacionados para probar de inmediato."""
        prog = ProgramaAcademico("PRG-01", "Ingeniería de Sistemas", "SNIES-101", 10)
        self.programas.append(prog)

        # Asignaturas (con relación reflexiva de prerrequisitos)
        asig1 = Asignatura("ASG-01", "Fundamentos de Programación", 3, prog.id)
        asig2 = Asignatura("ASG-02", "Programación Orientada a Objetos", 4, prog.id, prerrequisitos=[asig1])
        asig3 = Asignatura("ASG-03", "Bases de Datos", 3, prog.id, prerrequisitos=[asig1])
        for a in (asig1, asig2, asig3):
            prog.agregar_materia(a)
            self.asignaturas.append(a)

        # Grupos (dos grupos distintos para ASG-02 y un grupo para ASG-03)
        grp1 = Grupo("GRP-01", asig2.id, "2026-1", 30, asignatura=asig2)
        grp2 = Grupo("GRP-02", asig3.id, "2026-1", 25, asignatura=asig3)
        grp3 = Grupo("GRP-03", asig2.id, "2026-1", 25, asignatura=asig2)
        asig2.grupos.extend([grp1, grp3])
        asig3.grupos.append(grp2)
        self.grupos.extend([grp1, grp2, grp3])

        # Docente
        doc = Docente(
            "PER-10",
            "91234567",
            "Carlos",
            "Mendoza",
            "carlos.mendoza@ucc.edu.co",
            "3105556677",
            "Magíster en Ingeniería",
            "Sistemas y Computación",
        )
        self.docentes.append(doc)

        # Estudiantes ya inscritos
        est1 = Estudiante(
            "PER-01",
            "1098765432",
            "Camila",
            "Rojas",
            "camila.rojas@ucc.edu.co",
            "3001112233",
            "EST-01",
            date(2025, 1, 20),
        )
        est1.registrar_asignatura_aprobada(asig1.id)

        est2 = Estudiante(
            "PER-02",
            "1095432198",
            "Mateo",
            "Gómez",
            "mateo.gomez@ucc.edu.co",
            "3012223344",
            "EST-02",
            date(2025, 7, 15),
        )
        est2.registrar_asignatura_aprobada(asig1.id)

        est3 = Estudiante(
            "PER-03",
            "1092223344",
            "Valentina",
            "Pérez",
            "valentina.perez@ucc.edu.co",
            "3159998877",
            "EST-03",
            date(2026, 1, 18),
        )
        self.estudiantes.extend([est1, est2, est3])

        # Matrículas e inscripciones (est1 en GRP-01 y GRP-02; est2 en GRP-03 de la misma ASG-02)
        mat1 = Matricula("MAT-01", est1.id, "2026-1", date(2026, 1, 15), valor_credito=150000.0)
        ins1 = InscripcionAsignatura("INS-01", mat1.id, grp1.id, "CURSANDO", grupo=grp1)
        ins2 = InscripcionAsignatura("INS-02", mat1.id, grp2.id, "CURSANDO", grupo=grp2)
        mat1.inscripciones.extend([ins1, ins2])
        mat1.calcular_costo()
        mat1.confirmar_pago()
        est1.matriculas.append(mat1)

        mat2 = Matricula("MAT-02", est2.id, "2026-1", date(2026, 1, 16), valor_credito=150000.0)
        ins3 = InscripcionAsignatura("INS-03", mat2.id, grp3.id, "CURSANDO", grupo=grp3)
        mat2.inscripciones.append(ins3)
        mat2.calcular_costo()
        est2.matriculas.append(mat2)

        self.matriculas.extend([mat1, mat2])
        self.inscripciones.extend([ins1, ins2, ins3])

        # Calificaciones iniciales asociadas a asignatura y grupo
        c1 = Calificacion("CAL-01", "EVA-01", est1.id, 4.5, "Parcial 1", grupo_id=grp1.id, asignatura_id=asig2.id)
        c2 = Calificacion("CAL-02", "EVA-02", est1.id, 4.0, "Proyecto", grupo_id=grp1.id, asignatura_id=asig2.id)
        c3 = Calificacion("CAL-03", "EVA-03", est1.id, 4.2, "Taller SQL", grupo_id=grp2.id, asignatura_id=asig3.id)
        est1.calificaciones.extend([c1, c2, c3])

        c4 = Calificacion("CAL-04", "EVA-04", est2.id, 3.8, "Parcial 1", grupo_id=grp3.id, asignatura_id=asig2.id)
        est2.calificaciones.append(c4)

        self.calificaciones.extend([c1, c2, c3, c4])

    def _buscar_estudiante_por_codigo(self, codigo: str) -> Optional[Estudiante]:
        codigo_limpio = codigo.strip().lower()
        for est in self.estudiantes:
            if est.codigo_estudiantil.strip().lower() == codigo_limpio:
                return est
        return None

    def _buscar_asignatura_por_id(self, id_asig: str) -> Optional[Asignatura]:
        id_limpio = id_asig.strip().lower()
        for asig in self.asignaturas:
            if asig.id.strip().lower() == id_limpio:
                return asig
        return None

    def _buscar_grupo_por_id(self, id_grp: str) -> Optional[Grupo]:
        id_limpio = id_grp.strip().lower()
        for grp in self.grupos:
            if grp.id.strip().lower() == id_limpio:
                return grp
        return None

    def crear_estudiante(self) -> None:
        id_p = input("ID Persona (ej. PER-04): ").strip()
        doc = input("Documento: ").strip()
        nom = input("Nombres: ").strip()
        ape = input("Apellidos: ").strip()
        cor = input("Correo: ").strip()
        tel = input("Teléfono: ").strip()
        cod = input("Código estudiantil (ej. EST-04): ").strip()
        est = Estudiante(id_p, doc, nom, ape, cor, tel, cod, date.today())
        self.estudiantes.append(est)
        print(f"\n>>> Estudiante creado con éxito: {est} | Código: '{est.codigo_estudiantil}' <<<")

    def crear_asignatura(self) -> None:
        id_a = input("ID Asignatura (ej. ASG-04): ").strip()
        nom = input("Nombre de la asignatura: ").strip()
        cred = int(input("Créditos (ej. 3): ").strip())
        prog_id = input("ID Programa Académico (ej. PRG-01): ").strip()
        asig = Asignatura(id_a, nom, cred, prog_id)
        self.asignaturas.append(asig)
        for p in self.programas:
            if p.id == prog_id:
                p.agregar_materia(asig)
        print(f"\n>>> Asignatura creada con éxito: {asig} <<<")

    def crear_grupo(self) -> None:
        if self.asignaturas:
            print("Asignaturas disponibles:", [f"{a.id} ({a.nombre})" for a in self.asignaturas])
        id_g = input("ID Grupo (ej. GRP-04): ").strip()
        mat_id = input("ID Asignatura: ").strip()
        per_id = input("ID Período (ej. 2026-1): ").strip()
        cupo = int(input("Cupo máximo (ej. 25): ").strip())
        asig_obj = self._buscar_asignatura_por_id(mat_id)
        grp = Grupo(id_g, mat_id, per_id, cupo, asignatura=asig_obj)
        if asig_obj:
            asig_obj.grupos.append(grp)
        self.grupos.append(grp)
        print(f"\n>>> Grupo creado con éxito: {grp} <<<")

    def asignar_estudiante_a_asignatura_y_grupo(self) -> None:
        if not self.estudiantes:
            print("\n>>> Primero crea un estudiante (opción 1). <<<")
            return

        print("Estudiantes disponibles:")
        for e in self.estudiantes:
            print(f" - Código: '{e.codigo_estudiantil}' | Nombre: {e.get_nombre_completo()}")

        cod_est = input("Código del estudiante: ").strip()
        est = self._buscar_estudiante_por_codigo(cod_est)
        if not est:
            print(f"\n>>> No se encontró el estudiante con código '{cod_est}'. <<<")
            return

        if self.asignaturas:
            print("Asignaturas disponibles:")
            for a in self.asignaturas:
                print(f" - ID: '{a.id}' | {a.nombre} ({a.creditos} créditos)")
        id_asig = input("ID de la asignatura (si no existe, se creará): ").strip()
        asig = self._buscar_asignatura_por_id(id_asig)
        if not asig:
            nom_asig = input("Nombre de la nueva asignatura: ").strip() or f"Asignatura {id_asig}"
            cred_txt = input("Créditos [3]: ").strip()
            cred = int(cred_txt) if cred_txt else 3
            asig = Asignatura(id_asig, nom_asig, cred, "PRG-01")
            self.asignaturas.append(asig)

        grupos_asig = [g for g in self.grupos if g.materia_id.lower() == asig.id.lower() or g.asignatura is asig]
        if grupos_asig:
            print(f"Grupos disponibles para {asig.nombre}:")
            for g in grupos_asig:
                print(f" - ID: '{g.id}' | Período: {g.periodo_id} | Cupo: {len(g.inscripciones)}/{g.cupo_maximo}")
        elif self.grupos:
            print("Todos los grupos existentes:")
            for g in self.grupos:
                print(f" - ID: '{g.id}' | Materia: {g.materia_id} | Cupo: {len(g.inscripciones)}/{g.cupo_maximo}")

        id_grp = input("ID del grupo (si no existe, se creará): ").strip()
        grp = self._buscar_grupo_por_id(id_grp)
        if not grp:
            per_id = input("ID Período [2026-1]: ").strip() or "2026-1"
            cupo_txt = input("Cupo máximo [30]: ").strip()
            cupo = int(cupo_txt) if cupo_txt else 30
            grp = Grupo(id_grp, asig.id, per_id, cupo, asignatura=asig)
            self.grupos.append(grp)
        elif grp.asignatura is None:
            grp.asignatura = asig

        if grp not in asig.grupos:
            asig.grupos.append(grp)

        if not grp.inscribir_estudiante():
            print(f"\n>>> El grupo '{grp.id}' no tiene cupos disponibles. <<<")
            return

        mat = est.matriculas[0] if est.matriculas else None
        if not mat:
            id_mat = f"MAT-{len(self.matriculas) + 1:02d}"
            mat = Matricula(id_mat, est.id, grp.periodo_id, date.today(), valor_credito=150000.0)
            est.matriculas.append(mat)
            self.matriculas.append(mat)

        id_ins = f"INS-{len(self.inscripciones) + 1:02d}"
        ins = InscripcionAsignatura(id_ins, mat.id, grp.id, "CURSANDO", grupo=grp)
        mat.inscripciones.append(ins)
        mat.calcular_costo()
        self.inscripciones.append(ins)

        print("\n>>> ASIGNACIÓN REALIZADA CON ÉXITO <<<")
        print(f" - Estudiante: {est.get_nombre_completo()} (Código: {est.codigo_estudiantil})")
        print(f" - Asignatura: {asig.nombre} (ID: {asig.id}, {asig.creditos} créditos)")
        print(f" - Grupo: {grp.id} (Cupos usados: {len(grp.inscripciones)}/{grp.cupo_maximo})")
        print(f" - Matrícula actualizada: {mat.id} | Costo total: ${mat.costo_total:,.0f}")

    def ver_matricula_estudiante(self) -> None:
        if not self.estudiantes:
            print("\n>>> No hay estudiantes registrados todavía. <<<")
            return

        print("Estudiantes disponibles:")
        for e in self.estudiantes:
            print(f" - Código: '{e.codigo_estudiantil}' | Nombre: {e.get_nombre_completo()} | Matrículas: {len(e.matriculas)}")

        cod = input("Código del estudiante: ").strip()
        est = self._buscar_estudiante_por_codigo(cod)
        if not est:
            print(f"\n>>> No se encontró el estudiante con código '{cod}'. <<<")
            return

        if not est.matriculas:
            print(f"\n>>> El estudiante '{est.get_nombre_completo()}' aún no tiene matrícula registrada. <<<")
            return

        for mat in est.matriculas:
            mat.calcular_costo()
            estado_pago = "PAGADA" if mat.pagada else "PENDIENTE"
            print("\n>>> DETALLE DE MATRÍCULA <<<")
            print(f" - ID Matrícula: {mat.id} | Período: {mat.periodo_id} | Fecha: {mat.fecha_matricula}")
            print(f" - Estudiante: {est.get_nombre_completo()} ({est.codigo_estudiantil})")
            print(f" - Estado financiero: {estado_pago} | Costo total: ${mat.costo_total:,.0f}")
            print(" - Asignaturas / Grupos inscritos:")
            if not mat.inscripciones:
                print("    (Sin asignaturas inscritas)")
            for ins in mat.inscripciones:
                asig_nombre = ins.grupo.asignatura.nombre if (ins.grupo and ins.grupo.asignatura) else "N/A"
                creditos = ins.grupo.asignatura.creditos if (ins.grupo and ins.grupo.asignatura) else 0
                print(
                    f"    * [{ins.id}] Grupo: {ins.grupo_id} | Asignatura: {asig_nombre} "
                    f"({creditos} cr.) | Estado: {ins.estado_asignatura}"
                )

            if not mat.pagada:
                confirmar = input("¿Deseas confirmar el pago de esta matrícula ahora? (s/n): ").strip().lower()
                if confirmar == "s":
                    mat.confirmar_pago()
                    print(f" >>> Pago confirmado para la matrícula {mat.id}. <<<")

    def agregar_nota_estudiante(self) -> None:
        if not self.estudiantes:
            print("\n>>> Primero crea un estudiante (opción 1). <<<")
            return

        print("Estudiantes disponibles:")
        for e in self.estudiantes:
            print(f" - Código: '{e.codigo_estudiantil}' | Nombre: {e.get_nombre_completo()}")

        cod = input("Código del estudiante: ").strip()
        est = self._buscar_estudiante_por_codigo(cod)
        if not est:
            print(f"\n>>> No se encontró el estudiante con código '{cod}'. <<<")
            return

        print("\n¿Cómo deseas asociar la nota?")
        print("1. Por Asignatura")
        print("2. Por Grupo")
        modo = input("Elige 1 o 2: ").strip()

        asig_id: Optional[str] = None
        grp_id: Optional[str] = None

        if modo == "1":
            if self.asignaturas:
                print("Asignaturas disponibles:", [f"{a.id} ({a.nombre})" for a in self.asignaturas])
            id_a = input("ID de la asignatura: ").strip()
            asig_obj = self._buscar_asignatura_por_id(id_a)
            asig_id = asig_obj.id if asig_obj else id_a
            if asig_obj and asig_obj.grupos:
                if len(asig_obj.grupos) > 1:
                    print("Esta asignatura tiene varios grupos:", [g.id for g in asig_obj.grupos])
                    grp_elegido = input(f"ID del grupo [{asig_obj.grupos[0].id}]: ").strip()
                    grp_id = grp_elegido if grp_elegido else asig_obj.grupos[0].id
                else:
                    grp_id = asig_obj.grupos[0].id
        elif modo == "2":
            if self.grupos:
                print("Grupos disponibles:", [f"{g.id} (Asig: {g.materia_id})" for g in self.grupos])
            id_g = input("ID del grupo: ").strip()
            grp_obj = self._buscar_grupo_por_id(id_g)
            grp_id = grp_obj.id if grp_obj else id_g
            if grp_obj:
                asig_id = grp_obj.asignatura.id if grp_obj.asignatura else grp_obj.materia_id
        else:
            print("\n>>> Opción no válida. <<<")
            return

        titulo_eva = input("Nombre de la evaluación (ej. Parcial 1): ").strip() or "Evaluación"
        porcentaje_txt = input("Porcentaje de peso [25.0]: ").strip()
        porcentaje = float(porcentaje_txt) if porcentaje_txt else 25.0
        nota = float(input("Nota obtenida (0.0 a 5.0): ").strip())
        obs = input("Observación (opcional): ").strip() or titulo_eva

        if not (0.0 <= nota <= 5.0):
            print("\n>>> La nota debe estar entre 0.0 y 5.0. <<<")
            return

        eva = Evaluacion(
            f"EVA-{len(self.evaluaciones) + 1:02d}",
            grp_id or "GRP-SIN-ASIGNAR",
            titulo_eva,
            porcentaje,
            date.today(),
        )
        self.evaluaciones.append(eva)

        cal = Calificacion(
            f"CAL-{len(self.calificaciones) + 1:02d}",
            eva.id,
            est.id,
            nota,
            obs,
            grupo_id=grp_id,
            asignatura_id=asig_id,
        )
        eva.calificaciones.append(cal)
        est.calificaciones.append(cal)
        self.calificaciones.append(cal)

        print("\n>>> NOTA REGISTRADA CON ÉXITO <<<")
        print(f" - Estudiante: {est.get_nombre_completo()} ({est.codigo_estudiantil})")
        print(f" - Asignatura: {asig_id or 'No especificada'} | Grupo: {grp_id or 'No especificado'}")
        print(f" - Evaluación: {eva.titulo} ({eva.porcentaje_peso}%) | Nota: {cal.nota_obtenida}")

    def calcular_promedio_estudiante(self) -> None:
        if not self.estudiantes:
            print("\n>>> No hay estudiantes registrados todavía. <<<")
            return

        print("Estudiantes disponibles:")
        for e in self.estudiantes:
            print(f" - Código: '{e.codigo_estudiantil}' | Nombre: {e.get_nombre_completo()} | Notas actuales: {len(e.calificaciones)}")

        cod = input("Código del estudiante: ").strip()
        est = self._buscar_estudiante_por_codigo(cod)
        if not est:
            print(f"\n>>> No se encontró el estudiante con código '{cod}'. <<<")
            return

        if not est.calificaciones:
            print("\n>>> Este estudiante aún no tiene notas registradas. Usa la opción 6 para agregar notas. <<<")
            return

        print("\n¿Cómo deseas calcular el promedio?")
        print("1. Promedio general (todas las notas)")
        print("2. Promedio por Asignatura")
        print("3. Promedio por Grupo")
        tipo = input("Elige 1, 2 o 3: ").strip()

        filtradas = est.calificaciones
        etiqueta = "General"

        if tipo == "2":
            print("Asignaturas disponibles:", [f"{a.id} ({a.nombre})" for a in self.asignaturas])
            filtro_asig = input("ID de la asignatura a consultar: ").strip().lower()
            filtradas = [c for c in est.calificaciones if (c.asignatura_id or "").lower() == filtro_asig]
            etiqueta = f"Asignatura '{filtro_asig}'"
        elif tipo == "3":
            print("Grupos disponibles:", [g.id for g in self.grupos])
            filtro_grp = input("ID del grupo a consultar: ").strip().lower()
            filtradas = [c for c in est.calificaciones if (c.grupo_id or "").lower() == filtro_grp]
            etiqueta = f"Grupo '{filtro_grp}'"
        elif tipo != "1":
            print("\n>>> Opción no válida. <<<")
            return

        promedio = est.consultar_promedio(filtradas)
        detalle_notas = [f"{c.observacion}: {c.nota_obtenida}" for c in filtradas]

        print("\n>>> CÁLCULO DE PROMEDIO <<<")
        print(f" - Estudiante: {est.get_nombre_completo()} (Código: {est.codigo_estudiantil})")
        print(f" - Criterio: {etiqueta}")
        print(f" - Notas consideradas: {detalle_notas}")
        print(f" - Promedio: {promedio}")

    def modificar_estudiante(self) -> None:
        if not self.estudiantes:
            print("\n>>> No hay estudiantes registrados todavía. <<<")
            return

        codigos_disponibles = [e.codigo_estudiantil for e in self.estudiantes]
        print(f"Códigos registrados: {codigos_disponibles}")
        cod = input("Código estudiantil a modificar: ").strip()

        est = self._buscar_estudiante_por_codigo(cod)
        if not est:
            print(f"\n>>> No se encontró ningún estudiante con el código '{cod}'. Códigos válidos: {codigos_disponibles} <<<")
            return

        nuevo_correo = input("Nuevo correo: ").strip()
        nuevo_tel = input("Nuevo teléfono: ").strip()
        est.actualizar_datos(nuevo_correo, nuevo_tel)
        print(f"\n>>> Datos actualizados: {est} | Código: {est.codigo_estudiantil} | Correo: {est.correo} | Tel: {est.telefono} <<<")

    def imprimir_objetos(self) -> None:
        print("\n>>> OBJETOS REGISTRADOS EN EL SISTEMA <<<")
        print("\n=== ESTUDIANTES (CON NOTAS POR MATERIA Y GRUPO) ===")
        for e in self.estudiantes:
            materias_inscritas = [
                f"{i.grupo.asignatura.nombre} ({i.grupo_id})"
                for m in e.matriculas
                for i in m.inscripciones
                if i.grupo and i.grupo.asignatura and i.estado_asignatura != "RETIRADA"
            ]
            print(f" - {e} | Código: {e.codigo_estudiantil} | Promedio general: {e.consultar_promedio()}")
            print(f"   * Materias/Grupos inscritos: {materias_inscritas if materias_inscritas else 'Ninguna'}")

            if not e.calificaciones:
                print("   * Notas por materia: (Sin calificaciones registradas)")
            else:
                notas_por_materia: Dict[str, List[Calificacion]] = {}
                for cal in e.calificaciones:
                    clave_asig = cal.asignatura_id or "SIN-ASIGNATURA"
                    notas_por_materia.setdefault(clave_asig, []).append(cal)

                print("   * Notas detalladas por materia:")
                for asig_id, lista_cals in notas_por_materia.items():
                    asig_obj = self._buscar_asignatura_por_id(asig_id)
                    nombre_asig = asig_obj.nombre if asig_obj else asig_id
                    prom_materia = e.consultar_promedio(lista_cals)
                    detalle = [
                        f"[{c.grupo_id or 'Sin grupo'}] {c.observacion}: {c.nota_obtenida}"
                        for c in lista_cals
                    ]
                    print(f"     -> {nombre_asig} ({asig_id}) | Promedio: {prom_materia} | Notas: {detalle}")

        print("\n=== ASIGNATURAS Y SUS GRUPOS ===")
        for a in self.asignaturas:
            reqs = [r.nombre for r in a.obtener_prerrequisitos()]
            grupos_de_materia = [
                g for g in self.grupos if g.materia_id.lower() == a.id.lower() or g.asignatura is a
            ]
            print(f" - {a} | Total grupos: {len(grupos_de_materia)} | Prerrequisitos: {reqs}")
            if not grupos_de_materia:
                print("   * (Sin grupos abiertos)")
            else:
                for g in grupos_de_materia:
                    estudiantes_grupo = []
                    for ins in g.inscripciones:
                        if ins.estado_asignatura != "RETIRADA":
                            est_obj = next(
                                (est for est in self.estudiantes for m in est.matriculas if m.id == ins.matricula_id),
                                None,
                            )
                            if est_obj:
                                cals_grp = [c.nota_obtenida for c in est_obj.calificaciones if (c.grupo_id or "").lower() == g.id.lower()]
                                estudiantes_grupo.append(f"{est_obj.get_nombre_completo()} (Notas: {cals_grp})")
                    print(
                        f"   * Grupo [{g.id}] | Período: {g.periodo_id} | Cupo: {len(g.inscripciones)}/{g.cupo_maximo} "
                        f"| Inscritos: {estudiantes_grupo if estudiantes_grupo else 'Ninguno'}"
                    )

        print("\n=== RESUMEN GENERAL DE GRUPOS ===")
        for g in self.grupos:
            print(f" - {g} | Período: {g.periodo_id} | Inscripciones activas: {len(g.inscripciones)}")

    def mostrar_menu(self) -> None:
        print("\n========================================================")
        print(" SISTEMA GESTIÓN ACADÉMICA Y CAMPUS VIRTUAL (POO)")
        print("========================================================")
        print("1. Crear Estudiante")
        print("2. Crear Asignatura")
        print("3. Crear Grupo")
        print("4. Asignar Estudiante a Asignatura y Grupo")
        print("5. Ver Matrícula de Estudiante")
        print("6. Agregar Nota a Estudiante (por Asignatura o Grupo)")
        print("7. Calcular Promedio de Estudiante (general, asignatura o grupo)")
        print("8. Modificar contacto de Estudiante")
        print("9. Imprimir objetos registrados (con notas por materia y grupos)")
        print("0. Salir")

    def menu(self) -> None:
        while True:
            self.mostrar_menu()
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                self.crear_estudiante()
            elif opcion == "2":
                self.crear_asignatura()
            elif opcion == "3":
                self.crear_grupo()
            elif opcion == "4":
                self.asignar_estudiante_a_asignatura_y_grupo()
            elif opcion == "5":
                self.ver_matricula_estudiante()
            elif opcion == "6":
                self.agregar_nota_estudiante()
            elif opcion == "7":
                self.calcular_promedio_estudiante()
            elif opcion == "8":
                self.modificar_estudiante()
            elif opcion == "9":
                self.imprimir_objetos()
            elif opcion == "0":
                print("\n>>> Saliendo del sistema... <<<")
                break
            else:
                print("\n>>> Opción no válida. Intenta nuevamente. <<<")

            input("\nPresiona ENTER para continuar...")


if __name__ == "__main__":
    app = SistemaAcademicoApp()
    app.menu()