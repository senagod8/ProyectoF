from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.router.dependencias import get_current_user
from core.database import get_db
from app.schemas.usuarios import ActualizarUsuario, CrearUsuario, EditarPass, RetornoUsuario
from app.crud import usuarios as crud_users
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter()

@router.post("/registrar", status_code=status.HTTP_201_CREATED)
def create_user(
    user: CrearUsuario, 
    db: Session = Depends(get_db),
    user_token: RetornoUsuario = Depends(get_current_user)
):
    try:
        crear = crud_users.create_user(db, user)
        
        if user_token.id_rol != 1:
            raise HTTPException(status_code=401, detail="No tienes permiso para crear usuarios")

        if crear:
            return {"message": "Usuario creado correctamente"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/obtener-por-id/{id_usuario}", status_code=status.HTTP_200_OK, response_model=RetornoUsuario)
def get_by_id(
    id_usuario: int,
    db: Session = Depends(get_db),
    user_token: RetornoUsuario = Depends(get_current_user)
):
    try:
        result = crud_users.get_user_by_id(db, id_usuario)
    
        if result is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return result
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/obtener-por-correo/{correo}", status_code=status.HTTP_200_OK, response_model=RetornoUsuario)
def get_by_email(
    correo: str,
    db: Session = Depends(get_db),
    user_token: RetornoUsuario = Depends(get_current_user)
):
    try:
        result = crud_users.get_user_by_email(db, correo)

        if result is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return result
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/eliminar-por-id/{id_usuario}", status_code=status.HTTP_200_OK)
def delete_by_id(
    id_usuario: int,
    db: Session = Depends(get_db),
    user_token: RetornoUsuario = Depends(get_current_user)
):
    try:
        user = crud_users.get_user_by_delete(db, id_usuario)

        if user:
            return {"message": "Usuario eliminado correctamente"}
        
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
@router.put("/editar/{user_id}")
def update_user(
    user_id: int,
    user: ActualizarUsuario,
    db: Session = Depends(get_db),
    user_token: RetornoUsuario = Depends(get_current_user)
):
    try:
        success = crud_users.update_user(db, user_id, user)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el usuario")
        return {"message": "Usuario actualizado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.put("/editar_contrasenia")
def update_password(
    user: EditarPass,
    db: Session = Depends(get_db),
    user_token: RetornoUsuario = Depends(get_current_user)
):
    try:
        verificar = crud_users.verify_user_pass(db, user)
        
        if not verificar:
            raise HTTPException(status_code=400, detail="Contraseña anterior incorrecta")
        
        success = crud_users.update_password(db, user)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar la contraseña")
        return {"message": "Contraseña actualizada correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#verificar si la contraseña cambio 
#$argon2id$v=19$m=65536,t=3,p=4$UWqt1VrLubc2BiAEIKQ0Bg$FlOqiBHdfdRQjZ0rqnh8vFfzDAj+p+dzmWfXTign8oU
#$argon2id$v=19$m=65536,t=3,p=4$8p5TKmVMCYGQEiJkDOG8tw$DYj0uIp4hs/KQ5KCPKwg7lHOTezjd5WBXDzWZujQTgM