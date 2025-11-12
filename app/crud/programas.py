from fastapi import logger
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

def update_url_pdf(db: Session, url: str, cod: int) -> bool:
    try:
        query = text(f"""UPDATE programas_formacion SET url_pdf= :url_pdf 
                    WHERE cod_programa = :cod""")
        db.execute(query, {"url_pdf": url, "cod": cod})
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar contraseña: {e}")
        raise Exception("Error de base de datos al actualizar la contraseña")
    
    
def get_programa_by_cod(db: Session, cod: int):
    try:
        query = text(f"""SELECT * FROM programas_formacion 
                    WHERE cod_programa = :cod""")
        result = db.execute(query, {"cod": cod}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener programa por código: {e}")
        raise Exception("Error de base de datos al obtener el programa")