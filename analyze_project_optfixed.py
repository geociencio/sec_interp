#!/usr/bin/env python3
"""
analyze_project_opt2.py - Analiza estructura del proyecto para IA
Versión optimizada con mejoras de rendimiento y funcionalidad
"""

import os
import sys
import ast
import json
import pathlib
import subprocess
import mmap
import gc
import time
import signal
import traceback
import threading
from typing import Dict, List, Any, Optional, Iterator
from dataclasses import dataclass, asdict
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict
from contextlib import contextmanager
import fnmatch
import logging

# Configuración básica de logging (se ajustará en main)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# ==================== EXCEPCIONES PERSONALIZADAS ====================
class TimeoutException(Exception):
    """Excepción para timeouts"""
    pass

class AnalysisError(Exception):
    """Excepción base para errores de análisis"""
    pass

# ==================== CONTEXT MANAGER PARA TIMEOUT ====================
@contextmanager
def timeout(seconds: int):
    """Context manager para timeout de operaciones"""
    def signal_handler(signum, frame):
        raise TimeoutException(f"Timeout después de {seconds} segundos")

    # Configurar signal (solo funciona en main thread)
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# ==================== CACHE LRU MEJORADO ====================
class LRUCache:
    """Cache LRU más eficiente que lru_cache para grandes volúmenes"""
    def __init__(self, maxsize: int = 256):
        self.cache = OrderedDict()
        self._lock = threading.Lock()
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any:
        """Obtener valor del cache"""
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None

    def set(self, key: str, value: Any) -> None:
        """Establecer valor en cache"""
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

    def clear(self) -> None:
        """Limpiar cache"""
        with self._lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    def stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        with self._lock:
            total = self.hits + self.misses
            return {
                "size": len(self.cache),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": self.hits / total if total > 0 else 0,
                "maxsize": self.maxsize
            }

# ==================== TRACKER DE PROGRESO ====================
class ProgressTracker:
    """Tracker de progreso con estadísticas en tiempo real"""
    def __init__(self, total_files: int):
        self.total = total_files
        self.processed = 0
        self.start_time = time.time()
        self.file_times = []
        self.last_update = 0

    def update(self, file_path: pathlib.Path, processing_time: float) -> None:
        """Actualizar progreso"""
        self.processed += 1
        self.file_times.append(processing_time)

        # Actualizar cada 10 archivos o cada 2 segundos
        current_time = time.time()
        if (self.processed % 10 == 0 or
            current_time - self.last_update > 2):
            self._display_progress()
            self.last_update = current_time

    def _display_progress(self) -> None:
        """Mostrar progreso en consola"""
        elapsed = time.time() - self.start_time
        percent = (self.processed / self.total) * 100 if self.total > 0 else 0

        # Calcular ETA
        if self.file_times and self.processed > 0:
            avg_time = sum(self.file_times) / len(self.file_times)
            remaining = self.total - self.processed
            eta = remaining * avg_time
            eta_str = f"{eta:.0f}s"
        else:
            eta_str = "calculando..."

        # Mostrar con colores ANSI
        # Mostrar con colores ANSI
        # print(f"\r\033[K📊 Progreso: {self.processed}/{self.total} ({percent:.1f}%) | "
        #       f"Tiempo: {elapsed:.0f}s | ETA: {eta_str}", end="", flush=True)
        # Use simple log for progress to avoid spamming log file, or keep print for CLI interactive feel
        # Keeping print for interactive CLI feel but respecting cleaner output guidelines
        sys.stdout.write(f"\r\033[K📊 Progreso: {self.processed}/{self.total} ({percent:.1f}%) | "
                         f"Tiempo: {elapsed:.0f}s | ETA: {eta_str}")
        sys.stdout.flush()

    def complete(self) -> Dict[str, Any]:
        """Completar tracker y retornar estadísticas"""
        elapsed = time.time() - self.start_time
        print()  # Nueva línea

        return {
            "total_files": self.total,
            "processed": self.processed,
            "elapsed_time": elapsed,
            "avg_time_per_file": sum(self.file_times) / len(self.file_times) if self.file_times else 0,
            "files_per_second": self.processed / elapsed if elapsed > 0 else 0
        }

# ==================== DATA CLASSES ====================
@dataclass
class ModuleAnalysis:
    """Análisis de un módulo Python"""
    name: str
    lines: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    complexity_score: float
    dependencies: List[str]
    todo_comments: List[str]

@dataclass
class ProjectContext:
    """Contexto completo del proyecto"""
    project_name: str
    structure: Dict[str, Any]
    entry_points: List[str]
    tech_stack: Dict[str, List[str]]
    patterns: Dict[str, Any]
    technical_debt: List[str]
    optimization_opportunities: List[str]
    security_issues: List[str]

# ==================== ANALIZADOR PRINCIPAL ====================
# ==================== ANALIZADOR PRINCIPAL ====================
class ProjectAnalyzer:
    DEFAULT_CONFIG = {
        "quality_weights": {
            "docstrings": 3,
            "complexity_low": 3,     # <= thresholds.complexity_low
            "complexity_medium": 2,  # <= thresholds.complexity_medium
            "complexity_high": 1,    # <= thresholds.complexity_high
            "size_small": 2,         # <= thresholds.size_small
            "size_medium": 1,        # <= thresholds.size_medium
            "has_main": 1,
            "no_syntax_error": 1
        },
        "thresholds": {
            "complexity_low": 5,
            "complexity_medium": 10,
            "complexity_high": 15,
            "size_small": 200,
            "size_medium": 400
        }
    }

    def __init__(self, project_path: str, max_workers: int = None, exclude_patterns: List[str] = None):
        self.project_path = pathlib.Path(project_path).resolve()
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.exclude_patterns_args = exclude_patterns or []

        # Caches optimizados
        self.ast_cache = LRUCache(maxsize=512)
        self.file_cache = LRUCache(maxsize=256)

        # Grafo de dependencias (Adjacency List: {node: {neighbors}})
        self.import_graph = {}

        # Estado para análisis incremental
        self.state_file = self.project_path / ".analyzer_state.json"
        self._state = {"modules": {}, "timestamps": {}, "metadata": {}}

        # Log de errores
        self.error_log = []

        # Contexto del proyecto
        self.context = ProjectContext(
            project_name=self.project_path.name,
            structure={},
            entry_points=[],
            tech_stack={},
            patterns={},
            technical_debt=[],
            optimization_opportunities=[],
            security_issues=[]
        )

        # Cargar estado si existe
        # Cargar configuración
        self.config = self._load_config()

        # Cargar estado si existe
        self._load_state()

    def _load_config(self) -> Dict[str, Any]:
        """Carga configuración desde analyzer_config.json o usa defaults"""
        config = self.DEFAULT_CONFIG.copy()
        config_path = self.project_path / "analyzer_config.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge recursivo simple (solo 1 nivel)
                    for key, value in user_config.items():
                        if isinstance(value, dict) and key in config:
                            config[key].update(value)
                        else:
                            config[key] = value
                logger.info(f"⚙️ Configuración cargada desde {config_path.name}")
            except Exception as e:
                logger.warning(f"⚠️ Error cargando config, usando defaults: {e}")
        
        return config

    # ==================== MÉTODOS PRINCIPALES ====================

    def analyze(self) -> Dict[str, Any]:
        """Ejecuta análisis completo optimizado"""
        logger.info(f"🔍 Analizando proyecto: {self.context.project_name}")
        logger.info(f"📁 Ruta: {self.project_path}")
        logger.info(f"⚡ Workers: {self.max_workers}")
        logger.info("-" * 50)

        start_time = time.time()

        try:
            # 1. Obtener archivos Python con filtrado inteligente
            logger.info("📂 Escaneando archivos...")
            python_files = self._get_python_files_filtered()
            logger.info(f"📄 Encontrados {len(python_files)} archivos .py")

            # 2. Configurar tracker de progreso
            tracker = ProgressTracker(len(python_files))

            # 3. Análisis paralelo con control de memoria
            logger.info("⚙️ Analizando módulos...")
            modules_data = []

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Procesar en batches para control de memoria
                batch_size = 50
                for i in range(0, len(python_files), batch_size):
                    batch = python_files[i:i + batch_size]

                    # Enviar batch al executor
                    futures = {}
                    for py_file in batch:
                        future = executor.submit(self._analyze_single_module_optimized, py_file)
                        futures[future] = py_file
                        logger.debug(f"lanzados {len(futures)} trabajos en este batch")
                    # Procesar resultados del batch
                    logger.debug(f"empezando as_completed con {len(futures)} futures")
                    for future in as_completed(futures):
                        file_path = futures[future]
                        try:
                            # Timeout por archivo individual
                            start_file_time = time.time()
                            logger.debug(f"future OK para {futures[future]}")
                            module_data = future.result(timeout=45)
                            logger.debug(f"future.result OK para {file_path}")

                            if module_data:
                                modules_data.append(module_data)
                                logger.debug(f"añadido a modules_data -> {module_data['path']}")
                            else:
                                logger.debug(f"module_data es None / vacío para {file_path}")
                                # Actualizar tracker
                                processing_time = time.time() - start_file_time
                                tracker.update(file_path, processing_time)

                        except TimeoutError:
                            logger.warning(f"⏰ Timeout procesando {file_path}")
                            self._log_error(file_path, "Timeout (45s)")
                        except Exception as e:
                            logger.debug(f"future ERROR para {file_path}: {type(e).__name__} - {e}")
                            logger.error(f"⚠️ Error en {file_path}: {str(e)[:100]}")
                            self._log_error(file_path, str(e))

                    # Liberar memoria entre batches
                    if i % 100 == 0:
                        gc.collect()

            # Mostrar estadísticas del progreso
            tracker_stats = tracker.complete()

            logger.info(f"\n✅ Análisis de módulos completado")
            logger.info(f"   ⏱️  Tiempo total: {tracker_stats['elapsed_time']:.1f}s")
            logger.info(f"   📈 Velocidad: {tracker_stats['files_per_second']:.1f} archivos/segundo")

            # 4. Análisis posterior optimizado
            logger.info("\n📊 Procesando análisis posteriores...")
            analyses = self._run_post_analysis(modules_data)

            # 5. Guardar resultados
            logger.info("\n💾 Guardando resultados...")
            self._save_context_optimized(analyses)

            # 6. Mostrar estadísticas de cache
            self._print_cache_stats()

            # 7. Calcular tiempo total
            total_time = time.time() - start_time
            logger.info(f"\n{'='*50}")
            logger.info(f"🎉 ANÁLISIS COMPLETADO EN {total_time:.1f} SEGUNDOS")
            logger.info(f"{'='*50}")

            return analyses

        except KeyboardInterrupt:
            logger.info("\n\n⏹️  Análisis interrumpido por el usuario")
            return {}
        except Exception as e:
            logger.exception(f"\n❌ Error crítico durante el análisis: {e}")
            traceback.print_exc()
            return {}

    def _run_post_analysis(self, modules_data: List[Dict]) -> Dict[str, Any]:
        """Ejecutar análisis posteriores optimizados"""
        # Ejecutar análisis en paralelo cuando sea posible
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Preparar tareas
            tasks = {
                "structure": executor.submit(self._analyze_structure, modules_data),
                "entry_points": executor.submit(self._find_entry_points),
                "dependencies": executor.submit(self._analyze_dependencies_optimized, modules_data),
                "complexity": executor.submit(self._analyze_complexity, modules_data),
                "patterns": executor.submit(self._detect_patterns_advanced, modules_data),
                "debt": executor.submit(self._find_technical_debt, modules_data),
                "optimizations": executor.submit(self._find_optimizations, modules_data),
                "security": executor.submit(self._find_security_issues, modules_data),
                "metrics": executor.submit(self._calculate_project_metrics, modules_data)
            }

            # Recoger resultados
            analyses = {}
            for name, future in tasks.items():
                try:
                    analyses[name] = future.result(timeout=30)
                except TimeoutError:
                    logger.warning(f"⏰ Timeout en análisis {name}")
                    analyses[name] = {}
                except Exception as e:
                    logger.error(f"⚠️ Error en análisis {name}: {e}")
                    analyses[name] = {}

        return analyses

    # ==================== MÉTODOS OPTIMIZADOS DE ANÁLISIS ====================

    def _load_exclusion_patterns(self) -> List[str]:
        """Carga patrones de exclusión de .analyzerignore o .gitignore"""
        patterns = []
        
        # 1. Prioridad: .analyzerignore
        ignore_file = self.project_path / ".analyzerignore"
        if ignore_file.exists():
            try:
                with open(ignore_file, 'r', encoding='utf-8') as f:
                    patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                logger.info(f"📄 Cargados {len(patterns)} patrones de .analyzerignore")
            except Exception as e:
                logger.warning(f"⚠️ Error leyendo .analyzerignore: {e}")

        # 2. Fallback: .gitignore
        if not patterns:
            gitignore = self.project_path / ".gitignore"
            if gitignore.exists():
                try:
                    with open(gitignore, 'r', encoding='utf-8') as f:
                        patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    logger.info(f"📄 Cargados {len(patterns)} patrones de .gitignore")
                except:
                    pass

        # 3. Defaults si no hay configuración
        if not patterns:
            patterns = [
                "__pycache__", ".git", ".venv", "venv", "env",
                ".tox", ".pytest_cache", ".mypy_cache", ".coverage",
                "build", "dist", "*.egg-info"
            ]
            logger.info("ℹ️ Usando patrones de exclusión por defecto")

        # 4. Merge CLI args
        if self.exclude_patterns_args:
            logger.info(f"➕ Añadiendo {len(self.exclude_patterns_args)} patrones de CLI")
            patterns.extend(self.exclude_patterns_args)

        return patterns

    def _get_python_files_filtered(self) -> List[pathlib.Path]:
        """Obtener archivos Python con filtrado inteligente"""
        logger.debug("entra _get_python_files_filtered")
        python_files = []
        
        exclusion_patterns = self._load_exclusion_patterns()
        
        logger.debug(f"rglob iniciado en {self.project_path}")
        for py_file in self.project_path.rglob("*.py"):
            rel_path = str(py_file.relative_to(self.project_path))
            
            # Filtrar por patrones de exclusión usando fnmatch
            # Probamos tanto el path relativo completo como el nombre del archivo/directorio
            should_exclude = False
            for pattern in exclusion_patterns:
                # Normalizar patrón para directorios
                if pattern.endswith('/'):
                    pattern = pattern[:-1]
                
                # Coincidencia exacta o glob
                if fnmatch.fnmatch(rel_path, pattern) or \
                   fnmatch.fnmatch(py_file.name, pattern) or \
                   any(fnmatch.fnmatch(part, pattern) for part in py_file.relative_to(self.project_path).parts):
                    should_exclude = True
                    break
            
            if should_exclude:
                # logger.debug(f"descartado por exclusiones {py_file}")
                continue

            # Filtrar archivos de test
            if self._is_test_file(py_file):
                # logger.debug(f"descartado por test-file {py_file}")
                continue

            python_files.append(py_file)
            # logger.debug(f"añadido {py_file}")

        logger.debug(f"total python_files {len(python_files)}")
        logger.debug(f"va a retornar {len(python_files)} archivos")
        return sorted(python_files)

    def _analyze_single_module_optimized(self, py_file: pathlib.Path) -> Optional[Dict]:
        """Analiza un solo módulo de forma optimizada"""
        logger.debug(f"analizando {py_file.name}")
        rel_path = str(py_file.relative_to(self.project_path))
        logger.debug(f"rel_path = {rel_path}")

        try:
            # ----------  CACHE  ----------
            file_mtime = py_file.stat().st_mtime
            cached_state = self._state["modules"].get(rel_path)
            logger.debug(f"cached_state {'HIT' if cached_state else 'MISS'}")

            if (cached_state and
                self._state["timestamps"].get(rel_path, 0) >= file_mtime):
                logger.debug(f"usa cache para {rel_path}")
                return cached_state

            # ----------  LECTURA Y ANÁLISIS  ----------
            # ❌ Quitamos el timeout con señales (no válido en workers)
            content = self._read_file_fast(py_file)
            if not content:
                return None

            # Parsear AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                # Archivo con sintaxis inválida: análisis básico
                return {
                    "path": rel_path,
                    "lines": content.count('\n') + 1,
                    "functions": [],
                    "classes": [],
                    "imports": [],
                    "complexity": 0,
                    "docstrings": {"module": False, "classes": {}, "functions": {}},
                    "has_main": False,
                    "file_size_kb": py_file.stat().st_size / 1024,
                    "syntax_error": True
                }

            # Cachear AST para uso futuro
            self.ast_cache.set(rel_path, tree)

            # Extraer información del módulo
            module_data = {
                "path": rel_path,
                "lines": content.count('\n') + 1,
                "functions": self._extract_functions(tree),
                "classes": self._extract_classes(tree),
                "imports": self._extract_imports_optimized(tree),
                "complexity": self._calculate_complexity_optimized(tree),
                "docstrings": self._check_docstrings(tree),
                "has_main": self._has_main_guard(tree),
                "file_size_kb": py_file.stat().st_size / 1024,
                "syntax_error": False
            }

            # Actualizar estado incremental
            self._state["modules"][rel_path] = module_data
            self._state["timestamps"][rel_path] = file_mtime
            logger.debug(f"va a retornar module_data para {rel_path} -> {module_data is not None}")
            return module_data

        # ❌ Eliminamos el bloque de TimeoutException
        except Exception as e:
            self._log_error(py_file, f"Error en análisis: {str(e)}")
            logger.debug(f"EXCEPCIÓN en {rel_path}: {type(e).__name__} - {e}")
            return None
    def _read_file_fast(self, path: pathlib.Path) -> str:
        """Lectura ultra rápida con memory mapping y cache"""
        cache_key = str(path)
        cached = self.file_cache.get(cache_key)
        if cached:
            return cached

        try:
            with open(path, 'rb') as f:
                file_size = path.stat().st_size

                # Usar memory mapping para archivos grandes (> 1MB)
                if file_size > 1024 * 1024:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        content = mm.read().decode('utf-8-sig', errors='replace')
                else:
                    # Para archivos pequeños, lectura directa
                    content = f.read().decode('utf-8-sig', errors='replace')

                # Cachear resultado
                self.file_cache.set(cache_key, content)
                return content

        except Exception as e:
            self._log_error(path, f"Error lectura: {str(e)}")
            return ""

    def _extract_imports_optimized(self, tree: ast.AST) -> List[str]:
        """Extrae imports de forma optimizada"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    if module:
                        imports.append(f"{module}.{alias.name}")
                    else:
                        imports.append(alias.name)

        # De-duplicar manteniendo orden
        seen = set()
        unique_imports = []
        for imp in imports:
            if imp not in seen:
                seen.add(imp)
                unique_imports.append(imp)

        return unique_imports

    def _calculate_complexity_optimized(self, tree: ast.AST) -> int:
        """Calcula complejidad ciclomática optimizada"""
        complexity = 0
        decision_lines = set()

        for node in ast.walk(tree):
            # Decisiones básicas
            if isinstance(node, (ast.If, ast.While, ast.For,
                               ast.Try, ast.ExceptHandler,
                               ast.AsyncFor, ast.AsyncWith)):
                complexity += 1
                if hasattr(node, 'lineno'):
                    decision_lines.add(node.lineno)

            # Operadores booleanos
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

            # Comprehensions
            elif isinstance(node, (ast.ListComp, ast.SetComp,
                                  ast.DictComp, ast.GeneratorExp)):
                complexity += len(node.generators)

        # Penalizar módulos con muchas decisiones en pocas líneas
        if decision_lines:
            density_penalty = len(decision_lines) * 0.3
            complexity += int(density_penalty)


        return complexity

    # ==================== UTILIDADES DE GRAFO (SIN NETWORKX) ====================
    def _count_edges(self) -> int:
        """Cuenta total de aristas en el grafo"""
        return sum(len(neighbors) for neighbors in self.import_graph.values())

    def _find_simple_cycles(self, limit: int = 5) -> List[List[str]]:
        """Detecta ciclos simples usando DFS"""
        cycles = []
        visited = set()
        path = []
        path_set = set()

        def dfs(u):
            if len(cycles) >= limit:
                return

            visited.add(u)
            path.append(u)
            path_set.add(u)

            if u in self.import_graph:
                for v in self.import_graph[u]:
                    if v in path_set:
                        # Ciclo detectado
                        cycle_start = path.index(v)
                        cycles.append(path[cycle_start:])
                    elif v not in visited:
                        dfs(v)
            
            path_set.remove(u)
            path.pop()

        for node in list(self.import_graph.keys()):
             if node not in visited:
                 dfs(node)
        
        return cycles

    def _count_connected_components(self) -> int:
        """Cuenta componentes débilmente conectados"""
        # Convertir a no dirigido
        undirected = {}
        for u, neighbors in self.import_graph.items():
            if u not in undirected: undirected[u] = set()
            for v in neighbors:
                undirected[u].add(v)
                if v not in undirected: undirected[v] = set()
                undirected[v].add(u)
        
        visited = set()
        count = 0
        
        for node in undirected:
            if node not in visited:
                count += 1
                # BFS
                queue = [node]
                visited.add(node)
                while queue:
                    curr = queue.pop(0)
                    for neighbor in undirected.get(curr, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
        return count

    def _analyze_dependencies_optimized(self, modules_data: List[Dict]) -> Dict:
        """Analiza dependencias del proyecto de forma optimizada"""
        dependencies = {
            "internal": [],
            "external": [],
            "third_party": [],
            "files": {},
            "import_graph": {},
            "circular_dependencies": [],
            "graph_metrics": {}
        }

        # Analizar archivos de dependencias comunes
        req_files = ["requirements.txt", "setup.py", "pyproject.toml",
                    "Pipfile", "setup.cfg", "environment.yml"]

        for req_file in req_files:
            path = self.project_path / req_file
            if path.exists():
                try:
                    content = self._read_file_fast(path)
                    if content:
                        dependencies["files"][req_file] = content[:2000]  # Limitar tamaño
                except:
                    pass

        # Construir grafo de dependencias
        import_graph = {}
        all_imports = set()

        for module in modules_data:
            module_path = module.get("path", "")
            imports = module.get("imports", [])

            if module_path:
                # Añadir nodo
                if module_path not in self.import_graph:
                    self.import_graph[module_path] = set()
                
                import_graph[module_path] = imports
                all_imports.update(imports)

                # Añadir aristas al grafo
                for imp in imports:
                    # Buscar si la importación corresponde a un módulo del proyecto
                    for other_module in modules_data:
                        other_path = other_module.get("path", "")
                        if other_path and other_path.replace('.py', '').replace('/', '.') in imp:
                            # Añadir edge: module_path -> other_path
                            self.import_graph[module_path].add(other_path)
                            # Asegurar que el destino también existe como nodo
                            if other_path not in self.import_graph:
                                self.import_graph[other_path] = set()

        dependencies["import_graph"] = import_graph

        # Detectar dependencias circulares
        try:
            cycles = self._find_simple_cycles(limit=5)
            if cycles:
                dependencies["circular_dependencies"] = cycles
        except:
            pass

        # Calcular métricas del grafo
        num_nodes = len(self.import_graph)
        if num_nodes > 0:
            try:
                num_edges = self._count_edges()
                # Density for directed graph: E / (V * (V - 1))
                max_edges = num_nodes * (num_nodes - 1)
                density = num_edges / max_edges if max_edges > 0 else 0
                
                dependencies["graph_metrics"] = {
                    "nodes": num_nodes,
                    "edges": num_edges,
                    "density": density,
                    "is_dag": len(self._find_simple_cycles(limit=1)) == 0,
                    "weakly_connected_components": self._count_connected_components()
                }
            except Exception as e:
                logger.error(f"Error calculando métricas de grafo: {e}")

        # Clasificar imports
        stdlib_modules = {
            'os', 'sys', 'json', 'pathlib', 'typing', 'datetime', 're',
            'collections', 'itertools', 'math', 'random', 'statistics',
            'functools', 'hashlib', 'base64', 'csv', 'pickle', 'sqlite3'
        }

        for imp in sorted(all_imports):
            # Determinar si es import interno (relativo)
            if imp.startswith('.') or any(seg in imp for seg in ['..', './']):
                dependencies["internal"].append(imp)
            # Determinar si es stdlib
            elif imp.split('.')[0] in stdlib_modules:
                dependencies["external"].append(imp)
            else:
                dependencies["third_party"].append(imp)

        return dependencies

    def _detect_patterns_advanced(self, modules_data: List[Dict]) -> Dict:
        """Detección mejorada de patrones usando análisis AST e Herencia"""
        patterns = {
            "mvc": {"detected": False, "confidence": 0.0, "evidence": []},
            "repository": {"detected": False, "confidence": 0.0, "evidence": []},
            "factory": {"detected": False, "confidence": 0.0, "evidence": []},
            "singleton": {"detected": False, "confidence": 0.0, "evidence": []},
            "observer": {"detected": False, "confidence": 0.0, "evidence": []},
            "decorator": {"detected": False, "confidence": 0.0, "evidence": []},
            "strategy": {"detected": False, "confidence": 0.0, "evidence": []},
            "adapter": {"detected": False, "confidence": 0.0, "evidence": []},
            "command": {"detected": False, "confidence": 0.0, "evidence": []},
            "template_method": {"detected": False, "confidence": 0.0, "evidence": []}
        }

        # Mapeo de herencia a patrones (QGIS/PyQt específico)
        inheritance_map = {
            # Views (MVC)
            'QDialog': 'mvc',
            'QMainWindow': 'mvc',
            'QWidget': 'mvc',
            'QgsDockWidget': 'mvc',
            # Models (MVC)
            'QAbstractItemModel': 'mvc',
            'QAbstractTableModel': 'mvc',
            'QAbstractListModel': 'mvc',
            'QStandardItemModel': 'mvc',
            # Command / Strategy
            'QgsProcessingAlgorithm': 'command', 
            'QgsTask': 'command',
            'QUndoCommand': 'command',
            'QgsMapTool': 'strategy',
            'QgsMapToolEmitPoint': 'strategy',
        }

        # Detectar MVC por estructura de carpetas (baja confianza)
        mvc_folders = ['controller', 'model', 'view', 'templates', 'static', 'gui', 'ui', 'core']
        for root, dirs, _ in os.walk(self.project_path):
            for dir_name in dirs:
                if any(folder in dir_name.lower() for folder in mvc_folders):
                    patterns["mvc"]["confidence"] += 0.1
                    patterns["mvc"]["evidence"].append(f"folder: {dir_name}")

        # Análisis de módulos para patrones
        for module in modules_data:
            path = module.get("path", "")
            
            # Obtener AST del cache
            tree = self.ast_cache.get(path)
            if not tree:
                continue

            # Analizar cada clase en el módulo
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    
                    # 1. Análisis de Herencia
                    for base in node.bases:
                        base_name = self._get_base_name(base)
                        if base_name in inheritance_map:
                            pattern_key = inheritance_map[base_name]
                            patterns[pattern_key]["confidence"] += 0.3
                            patterns[pattern_key]["evidence"].append(f"{path}:{class_name}({base_name})")

                    # 2. Análisis de métodos y estructura (Existente pero refinado)
                    
                    # Singleton pattern detection
                    has_new = any(isinstance(item, ast.FunctionDef) and
                                 item.name == '__new__' for item in node.body)
                    has_instance_attr = any(isinstance(item, ast.Assign) and
                                          any(hasattr(t, 'attr') and t.attr == '_instance'
                                              for t in item.targets if isinstance(t, ast.Attribute))
                                          for item in node.body)

                    if has_new or has_instance_attr:
                        patterns["singleton"]["confidence"] += 0.5
                        patterns["singleton"]["evidence"].append(f"{path}:{class_name}")

                    method_names = [item.name for item in node.body
                                   if isinstance(item, ast.FunctionDef)]
                    
                    # Factory pattern detection
                    factory_keywords = ['create', 'make', 'build', 'factory', 'get_instance']
                    if 'Factory' in class_name or \
                       any(keyword in name.lower() for name in method_names for keyword in factory_keywords):
                        patterns["factory"]["confidence"] += 0.2
                        patterns["factory"]["evidence"].append(f"{path}:{class_name}")

                    # Repository pattern detection
                    crud_methods = ['save', 'find', 'get', 'delete', 'update', 'create', 'insert']
                    if 'Repository' in class_name or \
                       (len(crud_methods) >= 3 and any(m in name.lower() for name in method_names for m in crud_methods)):
                         patterns["repository"]["confidence"] += 0.3
                         patterns["repository"]["evidence"].append(f"{path}:{class_name}")

        # Normalizar confidencias y marcar como detectados
        for pattern_name in patterns:
            # Cap confidence at 1.0
            patterns[pattern_name]["confidence"] = min(1.0, patterns[pattern_name]["confidence"])
            if patterns[pattern_name]["confidence"] > 0.4:
                patterns[pattern_name]["detected"] = True

        return patterns

    # ==================== MÉTODOS DE ESTADO Y CACHE ====================

    def _load_state(self) -> None:
        """Cargar análisis previo para procesamiento incremental"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    saved_state = json.load(f)

                    # Validar versión y estructura
                    if isinstance(saved_state, dict):
                        self._state = saved_state
                        print(f"📂 Estado cargado: {len(self._state.get('modules', {}))} módulos cacheados")
        except Exception as e:
            print(f"⚠️ No se pudo cargar estado previo: {e}")
            self._state = {"modules": {}, "timestamps": {}, "metadata": {}}

    def _save_state(self) -> None:
        """Guardar estado para análisis incrementales"""
        try:
            state_data = {
                "modules": self._state["modules"],
                "timestamps": self._state["timestamps"],
                "metadata": {
                    "project_name": self.context.project_name,
                    "save_time": time.time(),
                    "version": "2.0",
                    "total_modules": len(self._state["modules"])
                }
            }

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️ No se pudo guardar estado: {e}")

    def _print_cache_stats(self) -> None:
        """Mostrar estadísticas de los caches"""
        ast_stats = self.ast_cache.stats()
        file_stats = self.file_cache.stats()

        print("\n📊 Estadísticas de Cache:")
        print(f"   AST Cache: {ast_stats['hit_rate']:.1%} hit rate "
              f"({ast_stats['hits']} hits, {ast_stats['misses']} misses)")
        print(f"   File Cache: {file_stats['hit_rate']:.1%} hit rate "
              f"({file_stats['hits']} hits, {file_stats['misses']} misses)")

    def _log_error(self, file_path: pathlib.Path, error_msg: str) -> None:
        """Log estructurado de errores"""
        log_entry = {
            "timestamp": time.time(),
            "file": str(file_path),
            "error_message": error_msg[:500]  # Limitar tamaño
        }
        self.error_log.append(log_entry)

    # ==================== MÉTODOS ORIGINALES (OPTIMIZADOS) ====================

    def _analyze_structure(self, modules_data: List[Dict]) -> Dict:
        """Analiza estructura de archivos y directorios"""
        structure = {
            "tree": self._generate_tree_optimized(),
            "modules_count": len(modules_data),
            "file_types": self._count_file_types_optimized(),
            "size_stats": self._calculate_size_stats_optimized()
        }
        return structure

    def _generate_tree_optimized(self) -> str:
        """Genera árbol de directorios optimizado"""
        try:
            # Intentar usar tree si está disponible
            result = subprocess.run(
                ["tree", "-I", "__pycache__|*.pyc|*.pyo|*.pycache|.git|.venv|venv|env",
                 "-a", "--noreport", "-L", "4"],  # Limitar profundidad
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                return result.stdout[:1500]  # Limitar tamaño
        except:
            pass

        # Fallback manual más rápido
        tree_lines = ["./"]
        max_depth = 4
        max_files_per_dir = 8

        for root, dirs, files in os.walk(self.project_path):
            # Calcular profundidad
            depth = root[len(str(self.project_path)):].count(os.sep)
            if depth > max_depth:
                continue

            # Filtrar directorios ocultos y de sistema
            dirs[:] = [d for d in dirs if not d.startswith(('.', '_'))]

            # Añadir directorio al árbol
            indent = "    " * depth
            rel_path = os.path.relpath(root, self.project_path)
            if rel_path != ".":
                tree_lines.append(f"{indent}{os.path.basename(root)}/")

            # Añadir archivos (limitados)
            file_indent = "    " * (depth + 1)
            for i, file in enumerate(sorted(files)[:max_files_per_dir]):
                if i == max_files_per_dir - 1 and len(files) > max_files_per_dir:
                    tree_lines.append(f"{file_indent}... (+{len(files) - max_files_per_dir} más)")
                    break
                tree_lines.append(f"{file_indent}{file}")

        return "\n".join(tree_lines)

    def _count_file_types_optimized(self) -> Dict[str, int]:
        """Cuenta tipos de archivos optimizado"""
        extensions = {}
        common_exts = {'.py', '.txt', '.md', '.json', '.yml', '.yaml',
                      '.html', '.css', '.js', '.xml', '.csv', '.sql'}

        for file in self.project_path.rglob("*"):
            if file.is_file():
                ext = file.suffix.lower()
                if ext in common_exts:
                    extensions[ext] = extensions.get(ext, 0) + 1
                elif ext:  # Otras extensiones
                    extensions[ext] = extensions.get(ext, 0) + 1

        # Ordenar y limitar
        sorted_exts = sorted(extensions.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_exts[:20])

    def _calculate_size_stats_optimized(self) -> Dict[str, Any]:
        """Calcula estadísticas de tamaño optimizado"""
        total_files = 0
        total_size = 0
        python_files = 0
        python_size = 0

        # Usar os.scandir que es más rápido que rglob
        for entry in os.scandir(self.project_path):
            if entry.is_file():
                total_files += 1
                total_size += entry.stat().st_size
                if entry.name.endswith('.py'):
                    python_files += 1
                    python_size += entry.stat().st_size
            elif entry.is_dir() and not entry.name.startswith('.'):
                # Recursión limitada para subdirectorios
                for root, dirs, files in os.walk(entry.path):
                    for file in files:
                        total_files += 1
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            total_size += file_size
                            if file.endswith('.py'):
                                python_files += 1
                                python_size += file_size
                        except:
                            pass

        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "python_files": python_files,
            "python_size_mb": round(python_size / (1024 * 1024), 2),
            "avg_file_size_kb": round(total_size / total_files / 1024, 2) if total_files > 0 else 0,
            "python_percentage": round(python_size / total_size * 100, 2) if total_size > 0 else 0
        }

    def _find_entry_points(self) -> List[str]:
        """Detección mejorada de puntos de entrada"""
        entry_points = set()

        # 1. Archivos con nombres comunes
        common_patterns = ["main.py", "app.py", "run.py", "manage.py",
                          "__main__.py", "setup.py", "cli.py", "wsgi.py",
                          "asgi.py", "start.py", "server.py", "index.py",
                          "django.wsgi", "flask.app"]

        for pattern in common_patterns:
            for file in self.project_path.rglob(pattern):
                if file.is_file() and not self._is_test_file(file):
                    entry_points.add(str(file.relative_to(self.project_path)))

        # 2. Archivos con shebang de Python
        for py_file in self.project_path.rglob("*.py"):
            if self._is_test_file(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8-sig') as f:
                    first_line = f.readline()
                    if first_line.startswith('#!') and 'python' in first_line:
                        entry_points.add(str(py_file.relative_to(self.project_path)))
            except:
                continue

        return sorted(entry_points)

    def _analyze_complexity(self, modules_data: List[Dict]) -> Dict:
        """Analiza complejidad general con más métricas"""
        if not modules_data:
            return {}

        total_lines = sum(m.get("lines", 0) for m in modules_data)
        total_complexity = sum(m.get("complexity", 0) for m in modules_data)

        # Calcular métricas avanzadas
        function_counts = [len(m.get("functions", [])) for m in modules_data]
        class_counts = [len(m.get("classes", [])) for m in modules_data]

        # Encontrar módulos más complejos
        complex_modules = sorted(
            [(m.get("path", ""), m.get("complexity", 0)) for m in modules_data],
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            "total_modules": len(modules_data),
            "total_lines": total_lines,
            "total_functions": sum(function_counts),
            "total_classes": sum(class_counts),
            "average_complexity": round(total_complexity / len(modules_data), 2) if modules_data else 0,
            "max_complexity": max((m.get("complexity", 0) for m in modules_data), default=0),
            "modules_without_docstrings": sum(1 for m in modules_data
                                            if not m.get("docstrings", {}).get("module", False)),
            "avg_functions_per_module": round(sum(function_counts) / len(modules_data), 2) if modules_data else 0,
            "avg_classes_per_module": round(sum(class_counts) / len(modules_data), 2) if modules_data else 0,
            "lines_per_function": round(total_lines / sum(function_counts), 2) if sum(function_counts) > 0 else 0,
            "most_complex_modules": complex_modules,
            "complexity_distribution": self._calculate_complexity_distribution(modules_data)
        }

    def _calculate_complexity_distribution(self, modules_data: List[Dict]) -> Dict[str, int]:
        """Calcula distribución de complejidad"""
        distribution = {
            "low (0-5)": 0,
            "medium (6-15)": 0,
            "high (16-30)": 0,
            "very_high (31+)": 0
        }

        for module in modules_data:
            complexity = module.get("complexity", 0)
            if complexity <= 5:
                distribution["low (0-5)"] += 1
            elif complexity <= 15:
                distribution["medium (6-15)"] += 1
            elif complexity <= 30:
                distribution["high (16-30)"] += 1
            else:
                distribution["very_high (31+)"] += 1

        return distribution

    def _find_technical_debt(self, modules_data: List[Dict]) -> List[Dict]:
        """Identifica deuda técnica con severidad"""
        debt_items = []

        for module in modules_data:
            path = module.get("path", "")
            complexity = module.get("complexity", 0)
            lines = module.get("lines", 0)
            docstrings = module.get("docstrings", {})

            issues = []

            # Clasificar por severidad
            if complexity > 20:
                issues.append({
                    "type": "alta_complejidad",
                    "severity": "alta",
                    "message": f"Complejidad ciclomática muy alta ({complexity})",
                    "value": complexity
                })
            elif complexity > 10:
                issues.append({
                    "type": "complejidad_moderada",
                    "severity": "media",
                    "message": f"Complejidad ciclomática alta ({complexity})",
                    "value": complexity
                })

            if lines > 800:
                issues.append({
                    "type": "archivo_muy_largo",
                    "severity": "alta",
                    "message": f"Archivo muy largo ({lines} líneas)",
                    "value": lines
                })
            elif lines > 500:
                issues.append({
                    "type": "archivo_largo",
                    "severity": "media",
                    "message": f"Archivo largo ({lines} líneas)",
                    "value": lines
                })

            if not docstrings.get("module", False):
                issues.append({
                    "type": "sin_docstring_modulo",
                    "severity": "baja",
                    "message": "Falta docstring a nivel de módulo"
                })

            # Verificar docstrings en clases y funciones
            classes_without_doc = sum(1 for has_doc in docstrings.get("classes", {}).values() if not has_doc)
            funcs_without_doc = sum(1 for has_doc in docstrings.get("functions", {}).values() if not has_doc)

            if classes_without_doc > 0:
                issues.append({
                    "type": "clases_sin_docstring",
                    "severity": "baja",
                    "message": f"{classes_without_doc} clases sin docstring"
                })

            if funcs_without_doc > 0:
                issues.append({
                    "type": "funciones_sin_docstring",
                    "severity": "baja",
                    "message": f"{funcs_without_doc} funciones sin docstring"
                })

            if issues:
                debt_items.append({
                    "module": path,
                    "issues": issues,
                    "total_issues": len(issues),
                    "severity_score": sum(3 if i["severity"] == "alta" else
                                         2 if i["severity"] == "media" else 1
                                         for i in issues)
                })

        # Ordenar por severidad
        debt_items.sort(key=lambda x: x["severity_score"], reverse=True)
        return debt_items[:50]  # Limitar resultados

    def _find_optimizations(self, modules_data: List[Dict]) -> List[Dict]:
        """Identifica oportunidades de optimización específicas"""
        optimizations = []

        for module in modules_data:
            path = module.get("path", "")
            imports = module.get("imports", [])
            complexity = module.get("complexity", 0)
            functions = module.get("functions", [])
            lines = module.get("lines", 0)

            suggestions = []

            # Optimizaciones basadas en imports
            if len(imports) > 25:
                suggestions.append({
                    "type": "imports_excesivos",
                    "priority": "media",
                    "message": f"Muchos imports ({len(imports)})",
                    "suggestions": [
                        "Agrupar imports relacionados",
                        "Usar imports locales dentro de funciones",
                        "Eliminar imports no utilizados con herramientas como autoflake"
                    ]
                })

            # Optimizaciones de complejidad
            if complexity > 15 and len(functions) > 5:
                suggestions.append({
                    "type": "refactorizacion_complejidad",
                    "priority": "alta",
                    "message": f"Alta complejidad ({complexity}) con {len(functions)} funciones",
                    "suggestions": [
                        "Extraer métodos de funciones largas",
                        "Usar polimorfismo en lugar de if/else largos",
                        "Aplicar principios SOLID",
                        "Considerar usar patrones de diseño"
                    ]
                })

            # Optimizaciones de tamaño
            if lines > 300:
                suggestions.append({
                    "type": "modulo_demasiado_grande",
                    "priority": "media",
                    "message": f"Módulo muy grande ({lines} líneas)",
                    "suggestions": [
                        "Dividir en múltiples módulos",
                        "Agrupar funcionalidad relacionada en paquetes",
                        "Extraer clases a módulos separados"
                    ]
                })

            # Detectar funciones demasiado largas
            if functions and lines / len(functions) > 50:
                suggestions.append({
                    "type": "funciones_demasiado_largas",
                    "priority": "media",
                    "message": f"Funciones muy largas (promedio {lines/len(functions):.1f} líneas/función)",
                    "suggestions": [
                        "Refactorizar funciones > 50 líneas",
                        "Extraer lógica común a funciones helper",
                        "Usar comprehensions y generadores"
                    ]
                })

            if suggestions:
                optimizations.append({
                    "module": path,
                    "suggestions": suggestions,
                    "priority": "alta" if complexity > 20 else "media"
                })

        return optimizations[:30]  # Limitar resultados

    def _find_security_issues(self, modules_data: List[Dict]) -> List[Dict]:
        """Identifica posibles problemas de seguridad"""
        security_issues = []

        dangerous_patterns = [
            ("exec(", "Uso de exec() - Vulnerable a inyección de código", "alta"),
            ("eval(", "Uso de eval() - Vulnerable a inyección de código", "alta"),
            ("pickle.loads", "Deserialización insegura - Puede ejecutar código arbitrario", "alta"),
            ("subprocess.call(", "Ejecución de shell sin sanitizar", "alta"),
            ("subprocess.Popen(", "Ejecución de shell sin sanitizar", "alta"),
            ("os.system(", "Ejecución de comandos del sistema", "alta"),
            ("input()", "Entrada de usuario sin validar", "media"),
            ("open(", "Apertura de archivos sin validar ruta", "media"),
            ("yaml.load(", "Carga de YAML insegura (usar yaml.safe_load)", "alta"),
            ("marshal.loads", "Deserialización insegura", "alta"),
            ("sqlite3.execute(", "Posible inyección SQL (usar parámetros)", "alta"),
            ("flask.request.args.get", "Parámetros GET sin validar", "media"),
            ("django.forms.CharField", "Validación insuficiente", "media"),
            ("md5(", "Uso de hash MD5 inseguro", "media"),
            ("sha1(", "Uso de hash SHA1 inseguro", "media")
        ]

        for module in modules_data:
            path = module.get("path", "")
            if not path:
                continue

            try:
                content = self._read_file_fast(self.project_path / path)
            except:
                continue

            issues_found = []
            for pattern, description, severity in dangerous_patterns:
                if pattern in content:
                    # Encontrar línea específica
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if pattern in line and not line.strip().startswith('#'):
                            issues_found.append({
                                "pattern": pattern,
                                "description": description,
                                "severity": severity,
                                "line": i,
                                "code": line.strip()[:120]
                            })
                            break  # Solo primera ocurrencia por patrón

            if issues_found:
                security_issues.append({
                    "module": path,
                    "issues": issues_found,
                    "total_issues": len(issues_found),
                    "max_severity": max((i["severity"] for i in issues_found),
                                       key=lambda x: {"alta": 3, "media": 2, "baja": 1}[x])
                })

        # Ordenar por severidad
        security_issues.sort(key=lambda x: {"alta": 3, "media": 2, "baja": 1}[x["max_severity"]],
                           reverse=True)
        return security_issues[:20]  # Limitar resultados

    def _calculate_project_metrics(self, modules_data: List[Dict]) -> Dict:
        """Calcula métricas generales del proyecto"""
        if not modules_data:
            return {}

        total_size_kb = sum(m.get("file_size_kb", 0) for m in modules_data)
        total_lines = sum(m.get("lines", 0) for m in modules_data)

        # Calcular métricas de calidad
        modules_with_docstrings = sum(
            1 for m in modules_data
            if m.get("docstrings", {}).get("module", False)
        )

        modules_with_main = sum(1 for m in modules_data if m.get("has_main", False))
        modules_with_syntax_error = sum(1 for m in modules_data if m.get("syntax_error", False))

        # Calcular estadísticas de complejidad
        complexities = [m.get("complexity", 0) for m in modules_data]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0

        return {
            "total_size_kb": round(total_size_kb, 2),
            "total_lines_code": total_lines,
            "avg_module_size_kb": round(total_size_kb / len(modules_data), 2),
            "avg_lines_per_module": round(total_lines / len(modules_data), 2),
            "modules_with_docstrings": modules_with_docstrings,
            "modules_with_main_guard": modules_with_main,
            "modules_with_syntax_errors": modules_with_syntax_error,
            "docstring_coverage": round(modules_with_docstrings / len(modules_data) * 100, 2),
            "entry_points_count": len(self.context.entry_points),
            "test_files_count": self._count_test_files(),
            "avg_complexity": round(avg_complexity, 2),
            "max_complexity": max(complexities) if complexities else 0,
            "quality_score": self._calculate_quality_score(modules_data)
        }

    def _calculate_quality_score(self, modules_data: List[Dict]) -> float:
        """Calcula un score de calidad general (Configurable)"""
        if not modules_data:
            return 0.0

        weights = self.config["quality_weights"]
        thresholds = self.config["thresholds"]

        # Calcular puntuación máxima posible por módulo
        max_module_score = (
            weights["docstrings"] +
            weights["complexity_low"] + # Asumimos el mejor caso
            weights["size_small"] +     # Asumimos el mejor caso
            weights["has_main"] +
            weights["no_syntax_error"]
        )
        
        total_score = 0.0
        max_possible_total = len(modules_data) * max_module_score

        for module in modules_data:
            module_score = 0

            # Puntos por tener docstring
            if module.get("docstrings", {}).get("module", False):
                module_score += weights["docstrings"]

            # Puntos por complejidad baja
            complexity = module.get("complexity", 0)
            if complexity <= thresholds["complexity_low"]:
                module_score += weights["complexity_low"]
            elif complexity <= thresholds["complexity_medium"]:
                module_score += weights["complexity_medium"]
            elif complexity <= thresholds["complexity_high"]:
                module_score += weights["complexity_high"]

            # Puntos por tamaño adecuado
            lines = module.get("lines", 0)
            if lines <= thresholds["size_small"]:
                module_score += weights["size_small"]
            elif lines <= thresholds["size_medium"]:
                module_score += weights["size_medium"]

            # Puntos por tener main guard
            if module.get("has_main", False):
                module_score += weights["has_main"]

            # Puntos por no tener errores de sintaxis
            if not module.get("syntax_error", False):
                module_score += weights["no_syntax_error"]

            total_score += module_score

        # Normalizar a porcentaje
        quality_percentage = (total_score / max_possible_total) * 100 if max_possible_total > 0 else 0
        return round(quality_percentage, 1)

    def _count_test_files(self) -> int:
        """Cuenta archivos de test optimizado"""
        count = 0
        test_patterns = ["test_", "_test", "spec_", "_spec", "conftest"]

        for file in self.project_path.rglob("*.py"):
            filename = file.name.lower()
            if any(pattern in filename for pattern in test_patterns):
                count += 1
            elif "tests" in str(file.parent).lower():
                count += 1

        return count

    def _is_test_file(self, path: pathlib.Path) -> bool:
        """Determina si es archivo de tests (optimizado)"""
        filename = path.name.lower()
        test_patterns = ["test_", "_test", "spec_", "_spec", "conftest"]

        return (any(pattern in filename for pattern in test_patterns) or
                "tests" in str(path).lower() or
                "test" in path.parent.name.lower())

    # ==================== MÉTODOS DE EXTRACCIÓN ====================

    def _extract_functions(self, tree: ast.AST) -> List[str]:
        """Extrae nombres de funciones"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = node.name
                # Extraer argumentos
                args_count = len(node.args.args)
                if args_count > 0:
                    func_info = f"{func_info}({args_count} args)"
                functions.append(func_info)
        return functions

    def _extract_classes(self, tree: ast.AST) -> List[str]:
        """Extrae nombres de clases con herencia"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Incluir información de herencia
                bases = [self._get_base_name(base) for base in node.bases]
                inheritance = f"({', '.join(bases)})" if bases else ""
                classes.append(f"{node.name}{inheritance}")
        return classes

    def _get_base_name(self, node: ast.AST) -> str:
        """Obtiene nombre de clase base"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return ast.unparse(node)
        else:
            return "Unknown"

    def _check_docstrings(self, tree: ast.AST) -> Dict[str, Any]:
        """Verifica docstrings por elemento"""
        docstrings = {
            "module": False,
            "classes": {},
            "functions": {}
        }

        # Docstring del módulo
        if isinstance(tree, ast.Module):
            docstrings["module"] = ast.get_docstring(tree) is not None

        # Docstrings de clases y funciones
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                docstrings["classes"][node.name] = ast.get_docstring(node) is not None
            elif isinstance(node, ast.FunctionDef):
                docstrings["functions"][node.name] = ast.get_docstring(node) is not None

        return docstrings

    def _has_main_guard(self, tree: ast.AST) -> bool:
        """Verifica si el módulo tiene if __name__ == '__main__'"""
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                try:
                    # Verificar condición __name__ == '__main__'
                    if (isinstance(node.test, ast.Compare) and
                        isinstance(node.test.left, ast.Name) and
                        node.test.left.id == '__name__'):

                        for comparator in node.test.comparators:
                            if (isinstance(comparator, ast.Constant) and
                                comparator.value == '__main__'):
                                return True
                except:
                    continue
        return False

    # ==================== MÉTODOS DE GUARDADO ====================

    def _save_context_optimized(self, analyses: Dict) -> None:
        """Guarda el contexto optimizado"""
        try:
            # 1. Guardar JSON completo
            context_file = self.project_path / "project_context.json"
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(analyses, f, indent=2, ensure_ascii=False, default=str)

            # 2. Guardar resumen ejecutivo
            summary_file = self.project_path / "PROJECT_SUMMARY.md"
            self._generate_project_summary(analyses, summary_file)

            # 3. Guardar contexto para IA
            ai_context_file = self.project_path / "AI_CONTEXT.md"
            self._generate_ai_context(analyses, ai_context_file)

            # 4. Guardar estado incremental
            self._save_state()

            # 5. Guardar log de errores si hay
            if self.error_log:
                error_file = self.project_path / "analysis_errors.json"
                with open(error_file, 'w', encoding='utf-8') as f:
                    json.dump(self.error_log, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Resultados guardados:")
            print(f"   📄 {context_file}")
            print(f"   📋 {summary_file}")
            print(f"   🤖 {ai_context_file}")

        except Exception as e:
            print(f"⚠️ Error guardando resultados: {e}")

    def _generate_project_summary(self, analyses: Dict, output_path: pathlib.Path) -> None:
        """Genera resumen ejecutivo del proyecto"""
        structure = analyses.get("structure", {})
        complexity = analyses.get("complexity", {})
        metrics = analyses.get("metrics", {})
        dependencies = analyses.get("dependencies", {})

        summary_content = f"""# RESUMEN DEL PROYECTO - {self.context.project_name}
Fecha de análisis: {time.strftime('%Y-%m-%d %H:%M:%S')}
Versión del analizador: 2.0 (Optimizado)

## 📊 MÉTRICAS CLAVE
- **Total módulos**: {complexity.get('total_modules', 0):,}
- **Líneas de código**: {complexity.get('total_lines', 0):,}
- **Tamaño total**: {structure.get('size_stats', {}).get('total_size_mb', 0):.1f} MB
- **Complejidad promedio**: {complexity.get('average_complexity', 0):.1f}
- **Cobertura de docstrings**: {metrics.get('docstring_coverage', 0):.1f}%
- **Score de calidad**: {metrics.get('quality_score', 0):.1f}/100
- **Archivos de test**: {metrics.get('test_files_count', 0)}

## 📁 ESTRUCTURA
- **Archivos Python**: {structure.get('size_stats', {}).get('python_files', 0)}
- **Total archivos**: {structure.get('size_stats', {}).get('total_files', 0)}
- **Tipo de archivos principales**: {', '.join(list(structure.get('file_types', {}).keys())[:5])}

## 🚨 PROBLEMAS CRÍTICOS
"""

        # Agregar problemas de seguridad
        security = analyses.get("security", [])
        if security:
            summary_content += "\n### 🔒 Problemas de Seguridad:\n"
            high_security = [s for s in security if s.get("max_severity") == "alta"]
            for item in high_security[:3]:
                summary_content += f"- **{item['module']}**: {item['total_issues']} problemas críticos\n"

        # Agregar deuda técnica
        debt = analyses.get("debt", [])
        if debt:
            summary_content += "\n### 🏗️ Deuda Técnica Crítica:\n"
            high_debt = [d for d in debt if d.get("severity_score", 0) >= 5]
            for item in high_debt[:5]:
                summary_content += f"- **{item['module']}**: {item['total_issues']} issues (score: {item['severity_score']})\n"

        # Agregar dependencias circulares
        circular = dependencies.get("circular_dependencies", [])
        if circular:
            summary_content += "\n### 🔄 Dependencias Circulares:\n"
            for cycle in circular[:3]:
                summary_content += f"- {cycle}\n"

        # Agregar recomendaciones
        optimizations = analyses.get("optimizations", [])
        if optimizations:
            summary_content += "\n## 💡 RECOMENDACIONES PRINCIPALES\n"
            high_priority = [o for o in optimizations if o.get("priority") == "alta"]
            for opt in high_priority[:3]:
                summary_content += f"\n### {opt['module']}\n"
                for suggestion in opt['suggestions'][:2]:
                    summary_content += f"- {suggestion['message']}\n"

        summary_content += f"\n## 📈 DISTRIBUCIÓN DE COMPLEJIDAD\n"
        dist = complexity.get("complexity_distribution", {})
        for key, value in dist.items():
            percentage = (value / complexity.get('total_modules', 1)) * 100
            summary_content += f"- {key}: {value} módulos ({percentage:.1f}%)\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)

    def _generate_ai_context(self, analyses: Dict, output_path: pathlib.Path) -> None:
        """Genera contexto optimizado para IA"""
        structure = analyses.get("structure", {})
        entry_points = analyses.get("entry_points", [])
        patterns = analyses.get("patterns", {})
        complexity = analyses.get("complexity", {})
        dependencies = analyses.get("dependencies", {})

        context_content = f"""# CONTEXTO PARA IA - {self.context.project_name}
Generado automáticamente por ProjectAnalyzer v2.0 (Optimizado)

## 📁 ESTRUCTURA DEL PROYECTO

{structure.get('tree', 'No disponible')[:1200]}


## 🎯 PUNTOS DE ENTRADA
{chr(10).join(f'- `{ep}`' for ep in entry_points[:10])}
{'' if len(entry_points) <= 10 else f'\n... y {len(entry_points) - 10} más'}

## 🏗️ PATRONES DETECTADOS
"""

        # Listar patrones encontrados
        detected_patterns = []
        for pattern_name, pattern_data in patterns.items():
            if isinstance(pattern_data, dict) and pattern_data.get("detected"):
                confidence = pattern_data.get("confidence", 0)
                detected_patterns.append(f"- **{pattern_name.upper()}**: Detectado (confianza: {confidence:.0%})")

        if detected_patterns:
            context_content += "\n".join(detected_patterns)
        else:
            context_content += "\nNo se detectaron patrones de diseño claros."

        context_content += f"""
## 📈 COMPLEJIDAD Y MÉTRICAS
- **Módulos totales**: {complexity.get('total_modules', 0)}
- **Líneas de código**: {complexity.get('total_lines', 0):,}
- **Funciones**: {complexity.get('total_functions', 0)}
- **Clases**: {complexity.get('total_classes', 0)}
- **Complejidad promedio**: {complexity.get('average_complexity', 0):.1f}
- **Módulos más complejos**: {', '.join([m[0] for m in complexity.get('most_complex_modules', [])[:3]])}

## 🔗 DEPENDENCIAS PRINCIPALES
"""

        # Agregar dependencias principales
        third_party = dependencies.get("third_party", [])
        if third_party:
            # Agrupar por paquete base
            base_packages = {}
            for dep in third_party:
                base = dep.split('.')[0]
                base_packages[base] = base_packages.get(base, 0) + 1

            context_content += "\n### Third Party (más frecuentes):\n"
            for package, count in sorted(base_packages.items(), key=lambda x: x[1], reverse=True)[:15]:
                context_content += f"- `{package}` ({count} imports)\n"

        # Agregar recomendaciones principales
        optimizations = analyses.get("optimizations", [])
        if optimizations:
            context_content += "\n## 💡 RECOMENDACIONES DE OPTIMIZACIÓN\n"
            for opt in optimizations[:5]:
                context_content += f"\n### {opt['module']} (Prioridad: {opt['priority'].upper()})\n"
                for suggestion in opt['suggestions'][:2]:
                    context_content += f"- **{suggestion['type']}**: {suggestion['message']}\n"

        # Agregar estructura de dependencias
        graph_metrics = dependencies.get("graph_metrics", {})
        if graph_metrics:
            context_content += f"""
## 🕸️  ESTRUCTURA DE DEPENDENCIAS
- **Nodos**: {graph_metrics.get('nodes', 0)}
- **Aristas**: {graph_metrics.get('edges', 0)}
- **Densidad**: {graph_metrics.get('density', 0):.3f}
- **Grafo acíclico**: {'Sí' if graph_metrics.get('is_dag', False) else 'No'}
- **Componentes conectados**: {graph_metrics.get('weakly_connected_components', 0)}
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(context_content)

# ==================== FUNCIÓN PRINCIPAL ====================
def setup_logging(verbose: bool = False):
    """Configura el sistema de logging"""
    log_level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(logging.DEBUG)  # Capture all at logger level, filter at handlers

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch_formatter = logging.Formatter('%(message)s')
    ch.setFormatter(ch_formatter)

    # File Handler
    fh = logging.FileHandler('analysis.log', mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(fh_formatter)

    # Reset handlers
    logger.handlers = []
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.propagate = False

def main():
    """Función principal optimizada"""
    import sys
    import argparse
    import signal
    import time
    import logging
    import os
    import traceback

    # Configurar logger global
    global logger
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(
        description='Analizador de Proyectos Python (Optimizado)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s ./mi-proyecto
  %(prog)s ./mi-proyecto --workers 8
  %(prog)s ./mi-proyecto --no-cache
  %(prog)s ./mi-proyecto --timeout 300
        """
    )

    parser.add_argument('project_path', nargs='?', default='.',
                       help='Ruta al proyecto a analizar')
    parser.add_argument('--workers', '-w', type=int,
                       help='Número de workers paralelos (default: CPU count + 4)')
    parser.add_argument('--no-cache', action='store_true',
                       help='Deshabilitar cache de análisis incremental')
    parser.add_argument('--timeout', '-t', type=int, default=300,
                       help='Timeout total en segundos (default: 300)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mostrar información detallada (DEBUG)')
    parser.add_argument('--exclude', nargs="+", help="Patrones adicionales a excluir")

    args = parser.parse_args()

    # Configurar logging antes de nada
    setup_logging(args.verbose)

    if not os.path.exists(args.project_path):
        logger.error(f"❌ Error: La ruta '{args.project_path}' no existe")
        sys.exit(1)

    if not os.path.isdir(args.project_path):
        logger.error(f"❌ Error: '{args.project_path}' no es un directorio")
        sys.exit(1)

    logger.info(f"🚀 Iniciando análisis optimizado...")
    logger.info(f"📁 Proyecto: {os.path.basename(os.path.abspath(args.project_path))}")

    # Configurar timeout global
    signal.signal(signal.SIGALRM, lambda signum, frame:
                  print("\n⏰ Timeout global alcanzado") or sys.exit(1))
    signal.alarm(args.timeout)

    try:
        # Crear analizador
        analyzer = ProjectAnalyzer(
            project_path=args.project_path,
            max_workers=args.workers,
            exclude_patterns=args.exclude
        )

        # Deshabilitar cache si se solicita
        if args.no_cache:
            analyzer.ast_cache.clear()
            analyzer.file_cache.clear()
            analyzer._state = {"modules": {}, "timestamps": {}, "metadata": {}}

        # Ejecutar análisis
        start_time = time.time()
        results = analyzer.analyze()
        total_time = time.time() - start_time
        
        # Desactivar timeout
        signal.alarm(0)

        # Mostrar resumen final
        if results:
            logger.info(f"\n{'='*60}")
            logger.info(f"🎉 ANÁLISIS COMPLETADO EN {total_time:.1f} SEGUNDOS")
            logger.info(f"{'='*60}")

            metrics = results.get('metrics', {})
            complexity = results.get('complexity', {})

            print(f"   💡 Optimizaciones: {len(results.get('optimizations', []))} sugerencias")
            print(f"   🏆 Calidad: {metrics.get('quality_score', 0):.1f}/100")

            # Mostrar problemas críticos si existen
            high_security = [s for s in results.get('security', [])
                           if s.get('max_severity') == 'alta']
            if high_security:
                print(f"\n🚨 PROBLEMAS CRÍTICOS DETECTADOS:")
                for issue in high_security[:3]:
                    print(f"   - {issue['module']}: {issue['total_issues']} problemas")

            print(f"\n💾 Los resultados han sido guardados en el directorio del proyecto.")

        else:
            print("\n❌ No se pudieron obtener resultados del análisis")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⏹️  Análisis interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
