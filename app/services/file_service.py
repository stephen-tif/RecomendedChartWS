"""
Módulo de servicio de archivos
Maneja carga de archivos, validación y procesamiento
Siguiendo el Principio de Responsabilidad Única
"""
import os
import logging
from typing import Dict, Any
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from app.utils.validators import validate_file

logger = logging.getLogger(__name__)


class FileService:
    """Servicio para operaciones de archivos con validación y seguridad"""
    
    def __init__(self, upload_folder: str = None):
        """
        Inicializar FileService
        
        Args:
            upload_folder (str): Ruta de carpeta de carga. Por defecto 'uploads'
        """
        self.upload_folder = upload_folder or os.getenv('UPLOAD_FOLDER', 'uploads')
        self.allowed_extensions = {'csv', 'xlsx', 'xls', 'json'}
        self._ensure_upload_folder()
    
    def _ensure_upload_folder(self) -> None:
        """Crear carpeta de carga si no existe"""
        try:
            if not os.path.exists(self.upload_folder):
                os.makedirs(self.upload_folder)
                logger.info(f"Carpeta de carga creada: {self.upload_folder}")
        except OSError as e:
            logger.error(f"Error al crear carpeta de carga: {str(e)}")
            raise
    
    def _allowed_file(self, filename: str) -> bool:
        """
        Verificar si la extensión del archivo está permitida
        
        Args:
            filename (str): Nombre del archivo a verificar
            
        Returns:
            bool: Verdadero si la extensión está permitida
        """
        if not filename or '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self.allowed_extensions
    
    def process_upload(self, file: FileStorage) -> Dict[str, Any]:
        """
        Procesar archivo cargado con validación y verificaciones de seguridad
        
        Args:
            file: Objeto de archivo cargado de Flask
            
        Returns:
            dict: Resultado de carga con información de archivo:
                - status: 'success'
                - filename: Nombre de archivo sanitizado
                - filepath: Ruta completa del archivo
                - size: Tamaño del archivo en bytes
                
        Raises:
            ValueError: Si el tipo de archivo no está permitido o la validación falla
            OSError: Si el archivo no puede ser guardado
        """
        if not file or not file.filename:
            raise ValueError('No se proporcionó archivo')
        
        # Validar extensión del archivo
        if not self._allowed_file(file.filename):
            raise ValueError(
                f'Tipo de archivo no permitido. Tipos permitidos: {", ".join(self.allowed_extensions)}'
            )
        
        # Sanitizar nombre de archivo para seguridad
        filename = secure_filename(file.filename)
        
        if not filename:
            raise ValueError('Nombre de archivo inválido')
        
        filepath = os.path.join(self.upload_folder, filename)
        
        # Validar archivo (tamaño, etc.)
        validate_file(file)
        
        try:
            # Guardar archivo
            file.save(filepath)
            file_size = os.path.getsize(filepath)
            
            logger.info(f"Archivo cargado exitosamente: {filename} ({file_size} bytes)")
            
            return {
                'status': 'success',
                'filename': filename,
                'filepath': filepath,
                'size': file_size
            }
            
        except Exception as e:
            logger.error(f"Error al guardar archivo {filename}: {str(e)}")
            # Limpiar si el archivo fue parcialmente guardado
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            raise
