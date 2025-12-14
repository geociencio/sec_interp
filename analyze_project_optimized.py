"""
analyze_project_optimized.py - Analizador de proyectos Python optimizado
Versión 2.1 - Correcciones y mejoras de estabilidad
"""

import os
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
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from collections import OrderedDict
from contextlib import contextmanager
import networkx as nx

# ==================== CONFIGURACIÓN ====================
DEBUG_MODE = False  # Cambiar a True para debug detallado

def debug_print(*args, **kwargs):
    """Print condicional para debug"""
    if DEBUG_MODE:
        print("[DEBUG]", *args, **kwargs)

# ==================== CACHE LRU CONCURRENTE ====================
class ConcurrentLRUCache:
    """Cache LRU thread-safe optimizado"""
    def __init__(self, maxsize: int = 256):
        self.cache = OrderedDict()
        self._lock = threading.RLock()
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any:
        """Obtener valor del cache de forma thread-safe"""
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None

    def set(self, key: str, value: Any) -> None:
        """Establecer valor en cache de forma thread-safe"""
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

# ==================== TRACKER DE PROGRESO MEJORADO ====================
class SmartProgressTracker:
    """Tracker de progreso inteligente con estimaciones adaptativas"""
    def __init__(self, total_files: int):
        self.total = total_files
        self.processed = 0
        self.start_time = time.time()
        self.file_times = []
        self._lock = threading.Lock()
        self.last_percent = 0

    def update(self, file_path: pathlib.Path, success: bool = True) -> None:
        """Actualizar progreso"""
        with self._lock:
            self.processed += 1

            # Mostrar progreso cada 5% o cada 10 archivos
            current_percent = (self.processed / self.total) * 100
            if (self.processed % 10 == 0 or
                current_percent - self.last_percent >= 5):
                self._display_progress()
                self.last_percent = current_percent

    def _display_progress(self) -> None:
        """Mostrar progreso de forma inteligente"""
        elapsed = time.time() - self.start_time
        percent = (self.processed / self.total) * 100 if self.total > 0 else 0

        # Estimación adaptativa
        if self.processed > 10:
            avg_time = elapsed / self.processed
            remaining = self.total - self.processed
            eta = remaining * avg_time

            # Formatear ETA legible
            if eta > 3600:
                eta_str = f"{eta/3600:.1f}h"
            elif eta > 60:
                eta_str = f"{eta/60:.1f}m"
            else:
                eta_str = f"{eta:.0f}s"
        else:
            eta_str = "calculando..."

        # Barra de progreso simple
        bar_length = 30
        filled = int(bar_length * percent / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(f"\r\033[K[{bar}] {percent:.1f}% | "
              f"{self.processed}/{self.total} | "
              f"⏱️ {elapsed:.0f}s | ETA: {eta_str}",
              end="", flush=True)

    def complete(self) -> Dict[str, Any]:
        """Completar tracker y retornar estadísticas"""
        elapsed = time.time() - self.start_time
        print()  # Nueva línea

        return {
            "total_files": self.total,
            "processed": self.processed,
            "elapsed_time": elapsed,
            "files_per_second": self.processed / elapsed if elapsed > 0 else 0,
            "success_rate": (self.processed / self.total) * 100 if self.total > 0 else 0
        }

# ==================== ANALIZADOR PRINCIPAL CORREGIDO ====================
class ProjectAnalyzer:
    def __init__(self, project_path: str, max_workers: int = None,
                 enable_cache: bool = True, quick_mode: bool = False):
        """
        Inicializa el analizador de proyectos

        Args:
            project_path: Ruta al proyecto a analizar
            max_workers: Número máximo de workers paralelos
            enable_cache: Habilitar cache de análisis incremental
            quick_mode: Modo rápido (análisis básico sin dependencias circulares)
        """
        self.project_path = pathlib.Path(project_path).resolve()
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.enable_cache = enable_cache
        self.quick_mode = quick_mode

        # Caches optimizados
        self.ast_cache = ConcurrentLRUCache(maxsize=512)
        self.file_cache = ConcurrentLRUCache(maxsize=256)

        # Grafo de dependencias
        self.import_graph = nx.DiGraph()

        # Estado para análisis incremental
        self.state_file = self.project_path / ".analyzer_state.json"
        self._state = {"modules": {}, "timestamps": {}, "metadata": {}}

        # Log de errores
        self.error_log = []

        # Estadísticas
        self.analysis_stats = {
            "modules_analyzed": 0,
            "modules_cached": 0,
            "errors": 0,
            "start_time": time.time()
        }

        # Cargar estado si existe y cache está habilitado
        if self.enable_cache:
            self._load_state()

    def _get_python_files_filtered(self) -> List[pathlib.Path]:
        """Obtiene archivos Python filtrando carpetas ignoradas"""
        python_files = []
        ignore_dirs = {
            '.git', '.venv', 'venv', 'env', '__pycache__', 
            '.pytest_cache', '.ruff_cache', '.mypy_cache', 
            'build', 'dist', 'node_modules', '.idea', '.vscode'
        }
        
        for root, dirs, files in os.walk(self.project_path):
            # Filtrar directorios in-place
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = pathlib.Path(root) / file
                    # Ignorar este mismo script 
                    if 'analyze_project' in file_path.name:
                        continue
                    python_files.append(file_path)
                    
        return sorted(python_files)

    # ==================== MÉTODO PRINCIPAL CORREGIDO ====================
    def analyze(self) -> Dict[str, Any]:
        """Ejecuta análisis completo optimizado"""
        print(f"🔍 Analizando proyecto: {self.project_path.name}")
        print(f"📁 Ruta: {self.project_path}")
        print(f"⚡ Workers: {self.max_workers}")
        print(f"🚀 Modo: {'RÁPIDO' if self.quick_mode else 'COMPLETO'}")
        print("-" * 50)

        try:
            # 1. Obtener archivos Python
            print("📂 Escaneando archivos...")
            python_files = self._get_python_files_filtered()

            if not python_files:
                print("❌ No se encontraron archivos Python para analizar")
                return {}

            print(f"📄 Encontrados {len(python_files)} archivos .py")

            # 2. Configurar tracker de progreso
            tracker = SmartProgressTracker(len(python_files))

            # 3. Análisis paralelo optimizado
            print("⚙️ Analizando módulos...")
            modules_data = []

            # Tamaño de batch adaptativo basado en número de archivos
            batch_size = min(100, max(10, len(python_files) // 10))

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Procesar en batches
                for i in range(0, len(python_files), batch_size):
                    batch = python_files[i:i + batch_size]

                    # Enviar batch al executor
                    futures = {}
                    for py_file in batch:
                        future = executor.submit(self._analyze_single_module_safe, py_file)
                        futures[future] = py_file

                    # Procesar resultados del batch
                    for future in as_completed(futures):
                        file_path = futures[future]
                        try:
                            # Timeout más corto para archivos pequeños
                            file_size = file_path.stat().st_size
                            timeout_seconds = 30 if file_size > 100000 else 15

                            module_data = future.result(timeout=timeout_seconds)

                            if module_data:
                                modules_data.append(module_data)
                                tracker.update(file_path, success=True)
                                self.analysis_stats["modules_analyzed"] += 1
                            else:
                                tracker.update(file_path, success=False)
                                self.analysis_stats["errors"] += 1

                        except TimeoutError:
                            print(f"\n⏰ Timeout procesando {file_path.name}")
                            self._log_error(file_path, "Timeout")
                            self.analysis_stats["errors"] += 1
                            tracker.update(file_path, success=False)
                        except Exception as e:
                            debug_print(f"Error en {file_path}: {type(e).__name__}")
                            self._log_error(file_path, str(e))
                            self.analysis_stats["errors"] += 1
                            tracker.update(file_path, success=False)

                    # Limpieza de memoria periódica
                    if i % (batch_size * 2) == 0:
                        gc.collect()

            # Estadísticas del análisis
            tracker_stats = tracker.complete()

            if not modules_data:
                print("❌ No se pudo analizar ningún módulo")
                return {}

            print(f"\n✅ Análisis de módulos completado")
            print(f"   ⏱️  Tiempo: {tracker_stats['elapsed_time']:.1f}s")
            print(f"   📈 Velocidad: {tracker_stats['files_per_second']:.1f} archivos/s")
            print(f"   ✅ Correctos: {self.analysis_stats['modules_analyzed']}")
            print(f"   ❌ Errores: {self.analysis_stats['errors']}")
            if self.enable_cache:
                print(f"   💾 Cacheados: {self.analysis_stats['modules_cached']}")

            # 4. Análisis posteriores
            print("\n📊 Procesando análisis posteriores...")
            analyses = self._run_post_analysis_optimized(modules_data)

            # 5. Guardar resultados
            print("\n💾 Guardando resultados...")
            self._save_results(analyses)

            # 6. Generar contexto para IA y Resumen
            print("\n🤖 Generando contexto para IA...")
            self._generate_ai_context(analyses)
            
            print("📊 Generando resumen del proyecto...")
            self._generate_project_summary(analyses)

            # 7. Calcular tiempo total
            total_time = time.time() - self.analysis_stats["start_time"]
            print(f"\n{'='*50}")
            print(f"🎉 ANÁLISIS COMPLETADO EN {total_time:.1f} SEGUNDOS")
            print(f"{'='*50}")

            return analyses

        except KeyboardInterrupt:
            print("\n\n⏹️  Análisis interrumpido por el usuario")
            return {}
        except Exception as e:
            print(f"\n❌ Error crítico durante el análisis: {e}")
            if DEBUG_MODE:
                traceback.print_exc()
            return {}

    def _analyze_single_module_safe(self, py_file: pathlib.Path) -> Optional[Dict]:
        """Analiza un módulo de forma segura (sin señales)"""
        rel_path = str(py_file.relative_to(self.project_path))

        try:
            # Verificar cache
            if self.enable_cache:
                file_mtime = py_file.stat().st_mtime
                cached_state = self._state["modules"].get(rel_path)

                if cached_state and self._state["timestamps"].get(rel_path, 0) >= file_mtime:
                    self.analysis_stats["modules_cached"] += 1
                    debug_print(f"Cache HIT: {rel_path}")
                    return cached_state

            # Leer contenido
            content = self._read_file_smart(py_file)
            if not content:
                return None

            # Análisis básico rápido
            lines = content.count('\n') + 1
            file_size_kb = py_file.stat().st_size / 1024

            # Parsear AST (con manejo de errores)
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                debug_print(f"Syntax error in {rel_path}: {e}")
                return {
                    "path": rel_path,
                    "lines": lines,
                    "functions": [],
                    "classes": [],
                    "imports": [],
                    "complexity": 0,
                    "docstrings": {"module": False, "classes": {}, "functions": {}},
                    "has_main": False,
                    "file_size_kb": file_size_kb,
                    "syntax_error": True,
                    "error_message": str(e)
                }
            except Exception as e:
                debug_print(f"AST parse error in {rel_path}: {e}")
                return None

            # Extraer información
            module_data = {
                "path": rel_path,
                "lines": lines,
                "functions": self._extract_functions_fast(tree),
                "classes": self._extract_classes_fast(tree),
                "imports": self._extract_imports_fast(tree),
                "complexity": self._calculate_complexity_fast(tree),
                "docstrings": self._check_docstrings_fast(tree),
                "has_main": self._has_main_guard_fast(tree),
                "file_size_kb": file_size_kb,
                "syntax_error": False
            }

            # Cachear si está habilitado
            if self.enable_cache:
                self._state["modules"][rel_path] = module_data
                self._state["timestamps"][rel_path] = py_file.stat().st_mtime
                self.ast_cache.set(rel_path, tree)

            return module_data

        except Exception as e:
            debug_print(f"Error analyzing {rel_path}: {type(e).__name__}: {e}")
            return None

    def _read_file_smart(self, path: pathlib.Path) -> str:
        """Lee archivos de forma inteligente con detección de encoding"""
        cache_key = str(path)
        cached = self.file_cache.get(cache_key)
        if cached:
            return cached

        try:
            # Detectar encoding
            rawdata = path.read_bytes()

            # Intentar diferentes encodings
            for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
                try:
                    content = rawdata.decode(encoding)
                    self.file_cache.set(cache_key, content)
                    return content
                except UnicodeDecodeError:
                    continue

            # Fallback: reemplazar caracteres inválidos
            content = rawdata.decode('utf-8', errors='replace')
            self.file_cache.set(cache_key, content)
            return content

        except Exception as e:
            debug_print(f"Error reading {path}: {e}")
            return ""

    def _extract_functions_fast(self, tree: ast.AST) -> List[str]:
        """Extrae funciones rápidamente"""
        return [node.name for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)]

    def _extract_classes_fast(self, tree: ast.AST) -> List[str]:
        """Extrae clases rápidamente"""
        return [node.name for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)]

    def _extract_imports_fast(self, tree: ast.AST) -> List[str]:
        """Extrae imports rápidamente"""
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.add(f"{module}.{alias.name}" if module else alias.name)
        return sorted(imports)

    def _calculate_complexity_fast(self, tree: ast.AST) -> int:
        """Calcula complejidad ciclomática simple"""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def _check_docstrings_fast(self, tree: ast.AST) -> Dict:
        """Verifica docstrings"""
        full_doc = ast.get_docstring(tree) is not None
        classes = {}
        functions = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes[node.name] = ast.get_docstring(node) is not None
            elif isinstance(node, ast.FunctionDef):
                functions[node.name] = ast.get_docstring(node) is not None
                
        return {
            "module": full_doc,
            "classes": classes,
            "functions": functions
        }

    def _has_main_guard_fast(self, tree: ast.AST) -> bool:
        """Verifica si tiene if __name__ == '__main__'"""
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                try:
                    if (isinstance(node.test, ast.Compare) and
                        isinstance(node.test.left, ast.Name) and
                        node.test.left.id == "__name__" and
                        isinstance(node.test.comparators[0], ast.Constant) and
                        node.test.comparators[0].value == "__main__"):
                        return True
                except:
                    pass
        return False

    def _run_post_analysis_optimized(self, modules_data: List[Dict]) -> Dict[str, Any]:
        """Ejecuta análisis posteriores optimizados"""
        analyses = {}

        # Análisis básicos (siempre se ejecutan)
        analyses["structure"] = self._analyze_structure_fast(modules_data)
        analyses["entry_points"] = self._find_entry_points_fast()
        analyses["complexity"] = self._analyze_complexity_fast(modules_data)
        analyses["metrics"] = self._calculate_metrics_fast(modules_data)

        # Análisis avanzados (opcionales en modo rápido)
        if not self.quick_mode:
            with ThreadPoolExecutor(max_workers=min(4, self.max_workers)) as executor:
                tasks = {
                    "dependencies": executor.submit(self._analyze_dependencies_fast, modules_data),
                    "patterns": executor.submit(self._detect_patterns_fast, modules_data),
                    "debt": executor.submit(self._find_technical_debt_fast, modules_data),
                    "optimizations": executor.submit(self._find_optimizations_fast, modules_data),
                    "security": executor.submit(self._find_security_issues_fast, modules_data),
                }

                for name, future in tasks.items():
                    try:
                        analyses[name] = future.result(timeout=60)
                    except Exception as e:
                        debug_print(f"Error in {name} analysis: {e}")
                        analyses[name] = {}

        return analyses

    def _save_results(self, analyses: Dict) -> None:
        """Guarda los resultados en JSON"""
        try:
            output_file = self.project_path / "analysis_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analyses, f, indent=2, ensure_ascii=False)
            print(f"   💾 {output_file.name}")
            
            # Guardar log de errores separadamente
            if self.error_log:
                error_file = self.project_path / "analysis_errors.json"
                with open(error_file, 'w', encoding='utf-8') as f:
                    json.dump(self.error_log, f, indent=2, ensure_ascii=False)
                print(f"   ⚠️  {error_file.name}")
                
            self._save_state()
        except Exception as e:
            print(f"⚠️  Error guardando resultados: {e}")

    # ==================== MÉTODOS RÁPIDOS ====================
    def _analyze_structure_fast(self, modules_data: List[Dict]) -> Dict:
        """Análisis rápido de estructura"""
        return {
            "modules_count": len(modules_data),
            "file_types": self._count_file_types_fast(),
            "size_stats": self._calculate_size_stats_fast(),
            "tree": self._generate_tree_fast()
        }

    def _generate_tree_fast(self) -> str:
        """Genera árbol de directorios rápidamente"""
        try:
            # Usar tree si está disponible
            result = subprocess.run(
                ["tree", "-I", "__pycache__|*.pyc|*.pyo|*.pycache|.git|.venv|venv|env",
                 "-a", "--noreport", "-L", "3"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return result.stdout[:1000]
        except:
            pass

        # Fallback simple
        tree_lines = []
        for root, dirs, files in os.walk(self.project_path):
            depth = root.replace(str(self.project_path), '').count(os.sep)
            if depth > 3:
                continue

            indent = "  " * depth
            tree_lines.append(f"{indent}{os.path.basename(root) or '.'}/")

            for file in sorted(files)[:5]:
                if file.endswith('.py'):
                    tree_lines.append(f"{indent}  📄 {file}")

        return "\n".join(tree_lines[:50])

    def _count_file_types_fast(self) -> Dict[str, int]:
        """Cuenta tipos de archivos rápidamente"""
        extensions = {}
        for file in self.project_path.rglob("*.*"):
            if file.is_file():
                ext = file.suffix.lower()
                if ext:
                    extensions[ext] = extensions.get(ext, 0) + 1

        return dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10])

    def _calculate_size_stats_fast(self) -> Dict[str, Any]:
        """Calcula estadísticas de tamaño rápidamente"""
        total_size = 0
        python_size = 0
        python_count = 0

        for file in self.project_path.rglob("*.py"):
            try:
                size = file.stat().st_size
                total_size += size
                python_size += size
                python_count += 1
            except:
                pass

        return {
            "python_files": python_count,
            "python_size_mb": round(python_size / (1024 * 1024), 2),
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }

    def _find_entry_points_fast(self) -> List[str]:
        """Detección rápida de puntos de entrada"""
        entry_points = set()
        patterns = ["main.py", "app.py", "__main__.py", "manage.py", "cli.py",
                   "run.py", "start.py", "server.py", "wsgi.py", "asgi.py"]

        for pattern in patterns:
            for file in self.project_path.rglob(pattern):
                if file.is_file() and not self._is_test_file(file):
                    entry_points.add(str(file.relative_to(self.project_path)))

        # Buscar archivos con if __name__ == "__main__"
        for module in self._state.get("modules", {}).values():
            if module.get("has_main", False):
                entry_points.add(module.get("path", ""))

        return sorted(entry_points)[:20]

    def _analyze_complexity_fast(self, modules_data: List[Dict]) -> Dict:
        """Análisis rápido de complejidad"""
        if not modules_data:
            return {}

        complexities = [m.get("complexity", 0) for m in modules_data]

        return {
            "total_modules": len(modules_data),
            "total_lines": sum(m.get("lines", 0) for m in modules_data),
            "average_complexity": round(sum(complexities) / len(complexities), 2),
            "max_complexity": max(complexities),
            "complex_modules": len([c for c in complexities if c > 15])
        }

    def _calculate_metrics_fast(self, modules_data: List[Dict]) -> Dict:
        """Cálculo rápido de métricas"""
        if not modules_data:
            return {}

        total_lines = sum(m.get("lines", 0) for m in modules_data)
        modules_with_docs = sum(1 for m in modules_data
                               if m.get("docstrings", {}).get("module", False))

        return {
            "total_modules": len(modules_data),
            "total_lines": total_lines,
            "modules_with_docstrings": modules_with_docs,
            "docstring_coverage": round(modules_with_docs / len(modules_data) * 100, 1),
            "quality_score": self._calculate_quality_score_fast(modules_data)
        }

    def _calculate_quality_score_fast(self, modules_data: List[Dict]) -> float:
        """Cálculo rápido del score de calidad"""
        if not modules_data:
            return 0.0

        score = 0
        max_score = len(modules_data) * 5

        for module in modules_data:
            # Docstring del módulo
            if module.get("docstrings", {}).get("module", False):
                score += 1

            # Complejidad baja
            if module.get("complexity", 0) <= 10:
                score += 1

            # Tamaño razonable
            if module.get("lines", 0) <= 300:
                score += 1

            # Sin errores de sintaxis
            if not module.get("syntax_error", False):
                score += 1

            # Tiene main guard
            if module.get("has_main", False):
                score += 1

        return round((score / max_score) * 100, 1)

    def _analyze_dependencies_fast(self, modules_data: List[Dict]) -> Dict:
        """Análisis rápido de dependencias"""
        dependencies = {
            "internal": [],
            "external": [],
            "third_party": [],
            "unique_imports": 0
        }

        all_imports = set()
        stdlib = {'os', 'sys', 'json', 'pathlib', 'typing', 'datetime', 're',
                 'collections', 'itertools', 'math', 'random'}

        for module in modules_data:
            for imp in module.get("imports", []):
                all_imports.add(imp)

        dependencies["unique_imports"] = len(all_imports)

        for imp in sorted(all_imports):
            if imp.startswith('.'):
                dependencies["internal"].append(imp)
            elif imp.split('.')[0] in stdlib:
                dependencies["external"].append(imp)
            else:
                dependencies["third_party"].append(imp)

        # Limitar resultados
        dependencies["third_party"] = dependencies["third_party"][:20]

        return dependencies

    def _detect_patterns_fast(self, modules_data: List[Dict]) -> Dict:
        """Detección rápida de patrones"""
        patterns = {
            "mvc": False,
            "repository": False,
            "factory": False,
            "singleton": False
        }

        # Detectar por nombres de carpetas
        folder_names = [d.name.lower() for d in self.project_path.iterdir() if d.is_dir()]
        if any(name in folder_names for name in ['controllers', 'models', 'views']):
            patterns["mvc"] = True

        # Contar apariciones en nombres de clases/métodos
        for module in modules_data:
            for cls in module.get("classes", []):
                cls_lower = cls.lower()
                if 'repository' in cls_lower or 'repo' in cls_lower:
                    patterns["repository"] = True
                if 'factory' in cls_lower:
                    patterns["factory"] = True
                if 'singleton' in cls_lower:
                    patterns["singleton"] = True

        return patterns

    def _find_technical_debt_fast(self, modules_data: List[Dict]) -> List[Dict]:
        """Identificación rápida de deuda técnica"""
        debt = []

        for module in modules_data:
            issues = []
            path = module.get("path", "")
            complexity = module.get("complexity", 0)
            lines = module.get("lines", 0)

            if complexity > 20:
                issues.append("Alta complejidad ciclomática")
            if lines > 500:
                issues.append("Archivo muy largo")
            if not module.get("docstrings", {}).get("module", False):
                issues.append("Falta docstring del módulo")

            if issues:
                debt.append({
                    "module": path,
                    "issues": issues,
                    "severity": "alta" if complexity > 20 or lines > 500 else "media"
                })

        return debt[:10]

    def _find_optimizations_fast(self, modules_data: List[Dict]) -> List[Dict]:
        """Identificación rápida de optimizaciones"""
        optimizations = []

        for module in modules_data:
            suggestions = []
            path = module.get("path", "")
            imports = module.get("imports", [])
            complexity = module.get("complexity", 0)

            if len(imports) > 20:
                suggestions.append("Muchos imports - considerar agrupar")
            if complexity > 15:
                suggestions.append("Alta complejidad - posible refactorización")

            if suggestions:
                optimizations.append({
                    "module": path,
                    "suggestions": suggestions,
                    "priority": "alta" if complexity > 20 else "media"
                })

        return optimizations[:10]

    def _find_security_issues_fast(self, modules_data: List[Dict]) -> List[Dict]:
        """Identificación rápida de problemas de seguridad"""
        security_issues = []
        dangerous_patterns = [
            ("exec(", "Uso de exec() peligroso"),
            ("eval(", "Uso de eval() peligroso"),
            ("pickle.loads", "Deserialización insegura"),
            ("subprocess.call(", "Ejecución de shell sin sanitizar"),
            ("os.system(", "Ejecución de comandos del sistema")
        ]

        for module in modules_data:
            path = module.get("path", "")
            if not path:
                continue

            try:
                content = self._read_file_smart(self.project_path / path)
                issues = []

                for pattern, description in dangerous_patterns:
                    if pattern in content:
                        issues.append(f"{description} ({pattern})")

                if issues:
                    security_issues.append({
                        "module": path,
                        "issues": issues,
                        "severity": "alta" if any(p in content for p in ["exec(", "eval(", "pickle.loads"]) else "media"
                    })
            except:
                continue

        return security_issues[:10]

    def _is_test_file(self, path: pathlib.Path) -> bool:
        """Determina si es archivo de tests"""
        filename = path.name.lower()
        return ("test_" in filename or "_test.py" in filename or
                "tests/" in str(path).lower())

    # ==================== MÉTODOS DE ESTADO ====================
    def _load_state(self) -> None:
        """Cargar estado de análisis previo"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self._state = json.load(f)
        except:
            self._state = {"modules": {}, "timestamps": {}, "metadata": {}}

    def _save_state(self) -> None:
        """Guardar estado para análisis incrementales"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self._state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            debug_print(f"Error saving state: {e}")

    def _log_error(self, file_path: pathlib.Path, error_msg: str) -> None:
        """Log de errores estructurado"""
        self.error_log.append({
            "timestamp": time.time(),
            "file": str(file_path),
            "error": error_msg[:200]
        })

    # ==================== GENERADOR DE CONTEXTO PARA IA ====================
    def _generate_ai_context(self, analyses: Dict) -> None:
        """Genera contexto optimizado para IA en formato Markdown"""
        try:
            ai_context_file = self.project_path / "AI_CONTEXT.md"

            with open(ai_context_file, 'w', encoding='utf-8') as f:
                f.write(self._build_ai_context_content(analyses))

            print(f"   🤖 {ai_context_file.name}")

        except Exception as e:
            print(f"⚠️  Error generando contexto AI: {e}")

    def _build_ai_context_content(self, analyses: Dict) -> str:
        """Construye el contenido del contexto para IA"""
        content = []

        # Cabecera
        content.append(f"# 🤖 CONTEXTO DEL PROYECTO PARA IA")
        content.append(f"**Proyecto:** `{self.project_path.name}`")
        content.append(f"**Fecha de análisis:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"**Modo de análisis:** {'RÁPIDO' if self.quick_mode else 'COMPLETO'}")
        content.append("---\n")

        # 1. Resumen Ejecutivo
        content.append("## 📊 RESUMEN EJECUTIVO")
        metrics = analyses.get("metrics", {})
        if metrics:
            content.append(f"- **Módulos:** {metrics.get('total_modules', 0)}")
            content.append(f"- **Líneas de código:** {metrics.get('total_lines', 0):,}")
            content.append(f"- **Score de calidad:** {metrics.get('quality_score', 0)}/100")
            content.append(f"- **Cobertura de docstrings:** {metrics.get('docstring_coverage', 0)}%")
        content.append("\n")

        # 2. Estructura del Proyecto
        content.append("## 📁 ESTRUCTURA DEL PROYECTO")
        structure = analyses.get("structure", {})
        if structure.get("tree"):
            content.append("```")
            content.append(structure.get("tree", ""))
            content.append("```")

        content.append(f"\n**Estadísticas:**")
        content.append(f"- Archivos Python: {structure.get('modules_count', 0)}")

        size_stats = structure.get("size_stats", {})
        if size_stats:
            content.append(f"- Tamaño total: {size_stats.get('total_size_mb', 0)} MB")
            content.append(f"- Tamaño código Python: {size_stats.get('python_size_mb', 0)} MB")
        content.append("\n")

        # 3. Puntos de Entrada
        entry_points = analyses.get("entry_points", [])
        if entry_points:
            content.append("## 🎯 PUNTOS DE ENTRADA")
            for ep in entry_points[:10]:
                content.append(f"- `{ep}`")
            if len(entry_points) > 10:
                content.append(f"- ... y {len(entry_points) - 10} más")
            content.append("\n")

        # 4. Complejidad del Proyecto
        complexity = analyses.get("complexity", {})
        if complexity:
            content.append("## 📈 COMPLEJIDAD DEL CÓDIGO")
            content.append(f"- **Complejidad promedio:** {complexity.get('average_complexity', 0):.1f}")
            content.append(f"- **Complejidad máxima:** {complexity.get('max_complexity', 0)}")
            content.append(f"- **Módulos complejos (>15):** {complexity.get('complex_modules', 0)}")
            content.append(f"- **Líneas totales:** {complexity.get('total_lines', 0):,}")
            content.append("\n")

        # 5. Dependencias
        dependencies = analyses.get("dependencies", {})
        if dependencies:
            content.append("## 🔗 DEPENDENCIAS")

            third_party = dependencies.get("third_party", [])
            if third_party:
                content.append("### 📦 Dependencias de Terceros")
                # Agrupar por paquete base
                packages = {}
                for dep in third_party:
                    base = dep.split('.')[0]
                    packages[base] = packages.get(base, 0) + 1

                for package, count in sorted(packages.items(), key=lambda x: x[1], reverse=True)[:15]:
                    content.append(f"- `{package}` ({count} usos)")

            content.append(f"\n**Total imports únicos:** {dependencies.get('unique_imports', 0)}")
            content.append("\n")

        # 6. Patrones de Diseño Detectados
        patterns = analyses.get("patterns", {})
        if patterns:
            content.append("## 🏗️ PATRONES DE DISEÑO")
            detected = []
            for pattern, detected_status in patterns.items():
                if detected_status:
                    detected.append(pattern)

            if detected:
                content.append("✅ **Patrones detectados:**")
                for pattern in detected:
                    content.append(f"- {pattern.upper()}")
            else:
                content.append("ℹ️ No se detectaron patrones de diseño claros.")
            content.append("\n")

        # 7. Problemas de Seguridad
        security = analyses.get("security", [])
        if security:
            content.append("## 🔒 PROBLEMAS DE SEGURIDAD")
            high_issues = [s for s in security if s.get("severity") == "alta"]
            medium_issues = [s for s in security if s.get("severity") == "media"]

            if high_issues:
                content.append("### 🚨 CRÍTICOS (Alta prioridad)")
                for issue in high_issues[:3]:
                    content.append(f"- **{issue['module']}**")
                    for item in issue.get("issues", [])[:2]:
                        content.append(f"  - {item}")

            if medium_issues:
                content.append("\n### ⚠️ MEDIOS (Revisar)")
                for issue in medium_issues[:2]:
                    content.append(f"- {issue['module']}: {len(issue.get('issues', []))} problemas")

            content.append(f"\n**Total problemas:** {len(security)}")
            content.append("\n")

        # 8. Deuda Técnica
        debt = analyses.get("debt", [])
        if debt:
            content.append("## 🏗️ DEUDA TÉCNICA")
            high_debt = [d for d in debt if d.get("severity") == "alta"]
            medium_debt = [d for d in debt if d.get("severity") == "media"]

            if high_debt:
                content.append("### 🔴 ALTA PRIORIDAD")
                for item in high_debt[:5]:
                    content.append(f"- **{item['module']}**")
                    for issue in item.get("issues", [])[:2]:
                        content.append(f"  - {issue}")

            if medium_debt:
                content.append("\n### 🟡 PRIORIDAD MEDIA")
                for item in medium_debt[:3]:
                    content.append(f"- {item['module']}: {len(item.get('issues', []))} issues")

            content.append(f"\n**Total módulos con deuda:** {len(debt)}")
            content.append("\n")

        # 9. Recomendaciones de Optimización
        optimizations = analyses.get("optimizations", [])
        if optimizations:
            content.append("## 💡 RECOMENDACIONES DE OPTIMIZACIÓN")
            high_priority = [o for o in optimizations if o.get("priority") == "alta"]
            medium_priority = [o for o in optimizations if o.get("priority") == "media"]

            if high_priority:
                content.append("### 🎯 ALTA PRIORIDAD")
                for opt in high_priority[:3]:
                    content.append(f"\n**{opt['module']}**")
                    for suggestion in opt.get("suggestions", [])[:2]:
                        content.append(f"- {suggestion}")

            if medium_priority:
                content.append("\n### 📝 PRIORIDAD MEDIA")
                for opt in medium_priority[:2]:
                    content.append(f"- {opt['module']}: {len(opt.get('suggestions', []))} sugerencias")

            content.append("\n")

        # 10. Consejos para IA
        content.append("## 🤖 CONSEJOS PARA ASISTENTES DE IA")
        content.append("""
### Al trabajar con este proyecto:
1. **Contexto Estructural:** Usa la estructura de directorios para entender la organización
2. **Puntos de Entrada:** Comienza por los módulos listados en puntos de entrada
3. **Dependencias:** Considera las dependencias de terceros al hacer sugerencias
4. **Patrones:** Respeta los patrones de diseño detectados al proponer cambios
5. **Seguridad:** Evita sugerir prácticas inseguras marcadas en el análisis

### Estilo de código recomendado:
- Sigue las convenciones de Python (PEP 8)
- Añade docstrings a nuevas funciones/clases
- Mantén la complejidad ciclomática baja (<15 por función)
- Usa type hints cuando sea apropiado
- Escribe tests para nuevo código
""")

        # 11. Información Técnica Detallada
        content.append("## 🔧 INFORMACIÓN TÉCNICA DETALLADA")

        # Tipos de archivos
        file_types = structure.get("file_types", {})
        if file_types:
            content.append("### Tipos de archivos principales:")
            for ext, count in list(file_types.items())[:5]:
                content.append(f"- `{ext}`: {count} archivos")

        # Métricas específicas
        if metrics:
            content.append("\n### Métricas específicas:")
            if "modules_with_docstrings" in metrics:
                content.append(f"- Módulos con docstrings: {metrics['modules_with_docstrings']}")

        # 12. Código de ejemplo (primeros módulos)
        content.append("\n## 📝 EJEMPLOS DE CÓDIGO")
        content.append("""
### Módulos principales del proyecto:
(Revisa los archivos .py para ejemplos concretos de implementación)

### Estructura típica de imports:
```python
# Dependencias estándar
import os
import sys
from typing import List, Dict

# Dependencias de terceros (comunes)
import requests
from flask import Flask

# Imports internos
from .utils import helper_function
from .models import BaseModel
Ejemplo de patrón detectado:
# Ejemplo de Singleton (si se detectó)
class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
""")
        
        return "\n".join(content)

    def _generate_project_summary(self, analyses: Dict) -> None:
        """Genera resumen del proyecto en Markdown"""
        try:
            summary_file = self.project_path / "PROJECT_SUMMARY.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(self._build_project_summary_content(analyses))
            print(f"   📋 {summary_file.name}")
        except Exception as e:
            print(f"⚠️  Error generando resumen: {e}")

    def _build_project_summary_content(self, analyses: Dict) -> str:
        """Construye el contenido del resumen del proyecto"""
        content = []
        metrics = analyses.get("metrics", {})
        complexity = analyses.get("complexity", {})
        structure = analyses.get("structure", {})
        
        content.append(f"# RESUMEN DEL PROYECTO - {self.project_path.name}")
        content.append(f"Fecha de análisis: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"Versión del analizador: 2.1 (Optimizado)")
        content.append("\n")

        # Métricas Clave
        content.append("## 📊 MÉTRICAS CLAVE")
        if metrics:
            content.append(f"- **Total módulos**: {metrics.get('total_modules', 0)}")
            content.append(f"- **Líneas de código**: {metrics.get('total_lines', 0):,}")
            content.append(f"- **Complejidad promedio**: {complexity.get('average_complexity', 0)}")
            content.append(f"- **Cobertura de docstrings**: {metrics.get('docstring_coverage', 0)}%")
            content.append(f"- **Score de calidad**: {metrics.get('quality_score', 0)}/100")
        
        size_stats = structure.get("size_stats", {})
        if size_stats:
             content.append(f"- **Tamaño total**: {size_stats.get('total_size_mb', 0)} MB")
        content.append("\n")

        # Estructura
        content.append("## 📁 ESTRUCTURA")
        content.append(f"- **Archivos Python**: {structure.get('python_files', 0)}")
        file_types = structure.get("file_types", {})
        top_types = ", ".join(list(file_types.keys())[:5])
        content.append(f"- **Tipo de archivos principales**: {top_types}")
        content.append("\n")

        # Problemas Críticos
        content.append("## 🚨 PROBLEMAS CRÍTICOS")
        
        security = analyses.get("security", [])
        high_sec = [s for s in security if s.get("severity") == "alta"]
        if high_sec:
            content.append("\n### 🔒 Problemas de Seguridad:")
            for issue in high_sec[:5]:
                content.append(f"- **{issue.get('module')}**: {len(issue.get('issues', []))} problemas críticos")
        
        debt = analyses.get("debt", [])
        high_debt = [d for d in debt if d.get("severity") == "alta"]
        if high_debt:
            content.append("\n### 🏗️ Deuda Técnica Crítica:")
            for item in high_debt[:5]:
                content.append(f"- **{item.get('module')}**: Requires Attention")

        if not high_sec and not high_debt:
             content.append("\nNo se detectaron problemas críticos graves.")
        content.append("\n")
        
        # Recomendaciones
        content.append("## 💡 RECOMENDACIONES PRINCIPALES")
        optimizations = analyses.get("optimizations", [])
        if optimizations:
            for opt in optimizations[:3]:
                content.append(f"\n### {opt.get('module')}")
                for sugg in opt.get("suggestions", []):
                    content.append(f"- {sugg}")
        else:
            content.append("\nNo hay recomendaciones urgentes.")

        return "\n".join(content)

# ==================== EJECUCIÓN PRINCIPAL ====================
if __name__ == "__main__":
    import argparse
    import sys
    
    # Configurar argumentos
    parser = argparse.ArgumentParser(description="Analizador de Proyectos Python Optimizado")
    parser.add_argument("path", nargs="?", default=".", help="Ruta al proyecto a analizar")
    parser.add_argument("--workers", "-w", type=int, help="Número de workers (hilos)")
    parser.add_argument("--fast", "-f", action="store_true", help="Modo rápido (análisis ligero)")
    parser.add_argument("--debug", "-d", action="store_true", help="Modo debug")
    parser.add_argument("--no-cache", action="store_true", help="Deshabilitar caché")
    
    args = parser.parse_args()
    
    # Configurar modo debug global
    if args.debug:
        DEBUG_MODE = True
        
    try:
        # Validar ruta
        project_path = pathlib.Path(args.path).resolve()
        if not project_path.exists():
            print(f"❌ Error: La ruta '{project_path}' no existe")
            sys.exit(1)
            
        # Iniciar analizador
        analyzer = ProjectAnalyzer(
            project_path=project_path,
            max_workers=args.workers,
            quick_mode=args.fast,
            enable_cache=not args.no_cache
        )
        
        # Ejecutar análisis
        analyzer.analyze()
        
    except KeyboardInterrupt:
        print("\n👋 Cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        if args.debug:
            traceback.print_exc()
