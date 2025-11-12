from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

def insertar_datos_en_bd(db: Session, df_programas, df_centros):
    programas_insertados = 0
    programas_actualizados = 0
    centros_insertados = 0
    centros_actualizados = 0
    errores = []

    # 1. Insertar programas
    insert_programa_sql = text("""
        INSERT INTO programas_formacion (
            cod_programa, version, nombre, nivel, tiempo_duracion, estado, url_pdf
        ) VALUES (
            :cod_programa, :version, :nombre, :nivel, :tiempo_duracion, :estado, :url_pdf
        )
        ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)
    """)

    for idx, row in df_programas.iterrows():
        try:
            result = db.execute(insert_programa_sql, row.to_dict())
            if result.rowcount == 1:
                programas_insertados += 1
            elif result.rowcount == 2:
                programas_actualizados += 1
        except SQLAlchemyError as e:
            msg = f"Error al insertar programa (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al insertar: {e}")

    # 2. Insertar centros
    insert_centros_formacion_sql = text("""
        INSERT INTO centros_formacion (
            cod_centro, nombre_centro, cod_regional, nombre_regional
        ) VALUES (
            :cod_centro, :nombre_centro, :cod_regional, :nombre_regional
        )
    """)

    for idx, row in df_centros.iterrows():
        try:
            result = db.execute(insert_centros_formacion_sql, row.to_dict())
            if result.rowcount == 1:
                centros_insertados += 1
            elif result.rowcount == 2:
                centros_actualizados += 1
        except SQLAlchemyError as e:
            msg = f"Error al insertar centro (índice {idx}): {e}"
            errores.append(msg)
            logger.error(f"Error al insertar: {e}")

    # Confirmar cambios
    db.commit()

    return {
        "programas_insertados": programas_insertados,
        "programas_actualizados": programas_actualizados,
        "centro_insertados": centros_insertados,
        "centro_actualizados": centros_actualizados,
        "errores": errores,
        "mensaje": "Carga completada con errores" if errores else "Carga completada exitosamente"
    }
