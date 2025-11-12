
from fastapi import APIRouter, UploadFile, File, Depends
import pandas as pd
from sqlalchemy.orm import Session
from io import BytesIO
from app.crud.cargar_archivos import insertar_datos_en_bd
from core.database import get_db

router = APIRouter()

@router.post("/upload-excel-pe04/")
async def upload_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    df = pd.read_excel(
        BytesIO(contents),
        engine="openpyxl",
        skiprows=4,
        usecols=[
            'CODIGO_REGIONAL', 'NOMBRE_REGIONAL', 
            'CODIGO_CENTRO', 'NOMBRE_CENTRO',
            'IDENTIFICADOR_FICHA', 
            'ESTADO_CURSO',
            'NIVEL_FORMACION',
            'NOMBRE_JORNADA',
            'FECHA_INICIO_FICHA', 'FECHA_TERMINACION_FICHA',
            'CODIGO_PROGRAMA', 'VERSION_PROGRAMA', 
            'NOMBRE_PROGRAMA_FORMACION',
            'MODALIDAD_FORMACION',
            'ETAPA_FICHA',
            'CODIGO_MUNICIPIO_CURSO',
            'NOMBRE_MUNICIPIO_CURSO',
            'NOMBRE_RESPONSABLE',
            'NOMBRE_EMPRESA',
            'TOTAL_APRENDICES',
            'TOTAL_APRENDICES_ACTIVOS'
        ],
        dtype=str
    )
    
    print(df.head())

    # Renombrar columnas según la estructura de la base de datos
    df = df.rename(columns={
        "CODIGO_REGIONAL": "cod_regional",
        "NOMBRE_REGIONAL": "nombre_regional",
        "CODIGO_CENTRO": "cod_centro",
        "NOMBRE_CENTRO": "nombre_centro",
        "IDENTIFICADOR_FICHA": "ficha",
        "ESTADO_CURSO": "estado_curso",
        "NIVEL_FORMACION": "nivel",
        "NOMBRE_JORNADA": "jornada",
        "FECHA_INICIO_FICHA": "fecha_inicio",
        "FECHA_TERMINACION_FICHA": "fecha_fin",
        "CODIGO_PROGRAMA": "cod_programa",
        "VERSION_PROGRAMA": "version",
        "NOMBRE_PROGRAMA_FORMACION": "nombre",
        "MODALIDAD_FORMACION": "modalidad",
        "ETAPA_FICHA": "etapa_ficha",
        "CODIGO_MUNICIPIO_CURSO": "cod_municipio",
        "NOMBRE_MUNICIPIO_CURSO": "nombre_municipio",
        "NOMBRE_RESPONSABLE": "nombre_responsable",
        "NOMBRE_EMPRESA": "nombre_empresa",
        "TOTAL_APRENDICES": "cupo_asignado",
        "TOTAL_APRENDICES_ACTIVOS": "num_aprendices_activos"
    })
    
    print(df.head())

    # Eliminar filas con valores faltantes en campos obligatorios
    required_fields = [
        "ficha", "cod_centro", "cod_programa", "version", "nombre", 
        "fecha_inicio", "fecha_fin", "etapa_ficha", "nombre_responsable", 
        "cod_municipio"
    ]
    df = df.dropna(subset=required_fields)

    # Convertir columnas a tipo numérico
    numeric_columns = ["ficha", "cod_programa", "cod_centro", "cod_regional"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # Convertir fechas
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce").dt.date
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce").dt.date

    # Crear DataFrame de programas únicos
    df_programas = df[["cod_programa", "version", "nombre", "nivel"]].drop_duplicates()
    df_programas["tiempo_duracion"] = 0
    df_programas["estado"] = 1
    df_programas["url_pdf"] = ""
    
    print(df_programas.head())
    
    df_centros = df[["cod_centro", "nombre_centro", "cod_regional", "nombre_regional"]].drop_duplicates()
    
    print(df_centros.head())
    

    # Eliminar columnas que ya no se necesitan del df principal
    df = df.drop('nombre', axis=1)

    resultados = insertar_datos_en_bd(db, df_programas, df_centros)
    return resultados