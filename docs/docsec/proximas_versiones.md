Prioridades Sugeridas para la Próxima Versión
1. Mejoras de Rendimiento y Escalabilidad
Caché Persistente: Implementar un sistema de caché en disco (SQLite o pickle) para evitar reprocesar datos grandes entre sesiones.
Procesamiento por Lotes: Optimizar el manejo de conjuntos de datos masivos con procesamiento incremental.
Índices Espaciales Mejorados: Expandir el uso de índices espaciales a todos los servicios (no solo geología).
2. Funcionalidades Avanzadas de Visualización
Exportación 3D: Generar modelos 3D de las secciones geológicas (formato OBJ, GLTF).
Comparación de Secciones: Herramienta para comparar múltiples perfiles lado a lado.
Anotaciones Interactivas: Permitir al usuario añadir notas, marcadores y mediciones personalizadas en el preview.
3. Integración con Estándares Geológicos
Soporte GeoSciML: Exportar datos en formatos estándar de la industria.
Integración con GeoPackage: Usar GeoPackage como formato nativo de proyecto en lugar de Shapefiles.
Soporte para Modelos de Bloques: Importar y visualizar modelos de bloques 3D en las secciones.
4. Experiencia de Usuario
Asistente de Configuración: Wizard paso a paso para usuarios nuevos.
Plantillas de Proyecto: Guardar y cargar configuraciones predefinidas.
Modo Oscuro: Tema visual oscuro para el diálogo principal.
Internacionalización: Añadir traducciones (español, francés, portugués).
5. Calidad y Mantenimiento
Cobertura de Tests: Aumentar la cobertura de pruebas unitarias al 80%+.
Documentación de API: Generar documentación completa de la API pública.
Benchmarking Automatizado: Añadir tests de rendimiento en CI/CD.
6. Características Específicas Solicitadas por Usuarios
Revisar el tracker de issues en GitHub para identificar las solicitudes más votadas.
Priorizar bugs críticos reportados por la comunidad.
📋 Proceso Recomendado
Crear un Milestone en GitHub para la v2.3.0
Abrir Issues para cada característica propuesta
