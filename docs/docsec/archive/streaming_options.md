# Streaming Processing Options for Large Sections

Processing extremely long cross-sections (e.g., >100km at high resolution) can exhaust available RAM if all points are held in memory before rendering. A streaming approach processes data in chunks.

## Option 1: Python Generators (Lazy Evaluation)

**Concept:** Replace list-based returns with Python iterators (`yield`). Data flows through the pipeline one point (or one segment) at a time.

-   **Pros:** Minimal memory footprint. Python native. Easy to implement for simple pipelines (Profile -> CSV).
-   **Cons:** Harder to use with libraries that expect full arrays (e.g., typical plotting libraries). Random access is impossible (cannot "look back" easily).
-   **Method:**
    -   `generate_profile` yields `(dist, elev)` tuples instead of returning a list.
    -   Exporters write lines to disk immediately upon receiving a tuple.
    -   **Bottleneck:** The QGIS native renderer still needs a geometry object. We would need to build "chunked" geometries (e.g., `LineString` per 10km) rather than one giant line.

## Option 2: Chunk-Based Processing (Block Processing)

**Concept:** Break the section line into fixed-length blocks (e.g., 1000 pixels or 10km chunks). Process and save each block independently.

-   **Pros:** Easier to debug. Parallelizable (each block is independent). Compatible with QGIS `QgsTask` for background processing.
-   **Cons:** "Edge effects" at chunk boundaries (need overlap for proper artifact handling). slightly more complex state management.
-   **Method:**
    1.  Divide section line into $N$ segments.
    2.  For each segment:
        -   Sample raster.
        -   Intersect geology.
        -   Write results to generic "Partitioned" files (e.g., `profile_part_001.csv`).
    3.  (Optional) Merge outputs at the end or load them as separate "virtual" layers.

## Option 3: Virtual Layer / Database Backed

**Concept:** Instead of processing to memory, write intermediate results immediately to a temporary spatial database (SQLite/GeoPackage) and query only what is needed for the current view (Rendering Window).

-   **Pros:** Extremely scalable. Handles "Infinite" length. Good for interactive browsing (LOD rendering becomes a database query: `SELECT * FROM profile WHERE x BETWEEN view_min AND view_max`).
-   **Cons:** High implementation overhead. Requires setting up a temp DB schema. Slower initial write speed (disk I/O).

## Recommendation

**Option 2 (Chunk-Based)** combined with **QgsTask** is the most robust integration for QGIS.
-   It prevents the UI from freezing (unlike simple generators run in the main thread).
-   It solves the memory issue by clearing the previous chunk from RAM after writing it to disk/DB.
-   It allows for a progress bar that genuinely reflects "Chunks Completed / Total Chunks".
