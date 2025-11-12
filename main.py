from fastapi import FastAPI, staticfiles
from fastapi.middleware.cors import CORSMiddleware
from app.router import usuarios, auth
from app.router import cargar_archivos
from app.router import programas

app = FastAPI()

app.mount("/static", staticfiles.StaticFiles(directory="static"), name="static")

# Incluir en el objeto app los routers
app.include_router(usuarios.router, prefix="/usario", tags=["servicios usuario"])
app.include_router(auth.router, prefix="/auth", tags=["servicios de login"])
app.include_router(cargar_archivos.router, prefix="/cargar", tags=["cargar archivos excel"])
app.include_router(programas.router)

# Configuración de CORS para permitir todas las solicitudes desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Permitir estos métodos HTTP
    allow_headers=["*"],  # Permitir cualquier encabezado en las solicitudes
)

@app.get("/")
def read_root():
    return {
                "message": "ok",
                "autor": "ADSO 2925888 - Andres Jimenez M",
            }