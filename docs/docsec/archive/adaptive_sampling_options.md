# Adaptive Sampling Options

The current implementation samples the Digital Elevation Model (DEM) at fixed intervals determined by the raster resolution. This ensures maximum detail but can generate an excessive number of points for long profiles over simple terrain (e.g., flat plains).

The following options propose methods to adapt the sampling density based on the complexity of the data (terrain roughness).

## Option 1: Visvalingam-Whyatt Simplification (Post-Processing)

**Concept:** Generate the full-resolution profile first (as currently done), then remove "unimportant" vertices that contribute least to the visual shape of the line.

-   **Pros:** Preserves the most critical features (peaks, valleys) while aggressively reducing point count. Geologically accurate.
-   **Cons:** Still requires initial high-density sampling (memory usage remains high during processing).
-   **Method:**
    1.  Sample uniform points at raster resolution.
    2.  Iteratively remove points that form the smallest triangular area with their neighbors.
    3.  Stop when the area error exceeds a user-defined threshold (e.g., `0.1m²`).

## Option 2: Vertical Error Tolerance (Ramer-Douglas-Peucker) (Post-Processing)

**Concept:** Similar to Option 1, but uses perpendicular distance to the trend line segment as the criteria.

-   **Pros:** Standard reliable algorithm (RDP). Control parameter (epsilon) is intuitive: "Ignore bumps smaller than X meters".
-   **Cons:** Post-processing only. Can slightly "clip" rounded hills into sharp peaks if epsilon is too high.
-   **Method:**
    1.  Sample uniform points.
    2.  Recursively divide the line. If all points between A and B are within `epsilon` distance of the line segment AB, keep only A and B.

## Option 3: Slope-Based Dynamic Sampling (Pre-Processing)

**Concept:** Vary the sampling interval *during* the sampling process based on the slope of the terrain.

-   **Pros:** Efficient. Doesn't generate thousands of points for flat lakes or plains.
-   **Cons:** More complex traversal logic. Risk of missing small features (a narrow ditch in a flat plain) if the "look-ahead" step is too large.
-   **Method:**
    1.  Start at `current_point`.
    2.  Check elevation at `current_point + min_step` and `current_point + max_step`.
    3.  Calculate slope.
    4.  If slope > threshold (steep), use `min_step` (high resolution).
    5.  If slope < threshold (flat), use `max_step` (low resolution).

## Recommendation

**Option 2 (RDP)** is generally the best balance for geological profiles. It guarantees that the simplified line never deviates from the "true" high-resolution data by more than the specified tolerance (e.g., 1 meter). This is critical for scientific accuracy.

**Option 3** is riskier because it assumes that checking two distant points is enough to determine "flatness", which might skip over a small but important geological feature (like a fault scarp) hidden in the middle of a "flat" step.
