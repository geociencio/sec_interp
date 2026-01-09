# SecInterp User Guide

## 1. Introduction

Welcome to the SecInterp plugin! This guide will help you get started with creating geological cross-sections from your QGIS layers.

SecInterp allows you to:
- Create a topographic profile from a Digital Elevation Model (DEM).
- Project geological units from a polygon layer onto the profile.
- Project structural measurements (e.g., dip and strike) onto the profile.
- Project drillhole traces and geological intervals (sondajes) onto the section.
- **New (v2.6.0)**: Digitize geological interpretations directly on the section with the **Interpretation Tool**.
- **New (v2.6.0)**: Export your 2D interpretations as valid **3D Shapefiles (PolygonZ)**.
- **New (v2.6.0)**: Configure the plugin interface in 5 different languages.
- View an interactive preview with level-of-detail (LOD) optimization.
- Measure distances and gradients with automatic snapping to vertices.

## 2. The Main Window

The SecInterp dialog is divided into three main areas:
1.  **Sidebar Navigation (Left)**: Navigate between different modules: DEM, Drillholes, Geology, Structure, Settings, and Help.
2.  **Configuration Page (Center)**: Where you configure the parameters for the selected module.
3.  **Preview Panel (Right)**: An interactive canvas showing your cross-section in real-time.

@[INSERT IMAGE HERE: images/ui_main_dialog_v26.png]
*Figure 1: The redesigned v2.6.0 Main Window with Sidebar navigation.*

## 3. Step-by-Step Tutorial: Creating a Profile

### Step 1: Digital Elevation Model (DEM)
1.  Navigate to the **DEM** tab in the sidebar.
2.  **Raster Layer**: Select your Digital Elevation Model.
3.  **Vertical Exaggeration**: Adjust if you want to emphasize topography (e.g., 2.0x).

@[INSERT IMAGE HERE: images/guide_dem_setup.png]
*Figure 2: Digital Elevation Model configuration.*

### Step 2: Define Section Line
1.  Navigate to the **Section Line** tab.
2.  **Section Layer**: Select the vector line layer representing your section traces.
3.  **Buffer**: Set a buffer distance (e.g., 50m) to capture data around the line.
4.  Optionally, filter specific lines if your layer contains multiple traces.

@[INSERT IMAGE HERE: images/guide_section_setup.png]
*Figure 3: Section Line selection and buffer configuration.*

### Step 3: Adding Geological Data
1.  Navigate to the **Geology** tab.
2.  **Outcrop Layer**: Select the polygon layer containing your surface geology.
3.  **Geology Field**: Choose the field containing the unit codes or names.

### Step 4: Adding Drillhole Data
The **Drillholes** page allows you to project borehole data onto the section. This page is divided into three sub-tabs:

#### 1. Collars Tab
Configures the location of drillhole collars (start points).
- **Collar Layer**: Point layer with hole locations.
- **Hole ID**: Unique identifier for each drillhole.
- **Use Layer Geometry**: Keep checked to use the point layer's geometry for X/Y coordinates.
- **Elevation (Z)**: Optional field for collar elevation (if not using DEM).
- **Total Depth**: Optional field for maximum depth.

@[INSERT IMAGE HERE: images/guide_drillhole_collars.png]
*Figure 4a: Drillhole Collars configuration.*

#### 2. Survey Tab
Configures downhole survey data (deviation).
- **Survey Layer**: Table or layer with survey measurements.
- **Hole ID**: Field linking to the Collar ID.
- **Depth**: Distance down the hole.
- **Azimuth**: Direction (0-360).
- **Inclination**: Dip (-90 to 90).

@[INSERT IMAGE HERE: images/guide_drillhole_survey.png]
*Figure 4b: Drillhole Survey configuration.*

#### 3. Intervals Tab
Configures geological or attribute intervals.
- **Interval Layer**: Table or layer with logging data.
- **Hole ID**: Field linking to the Collar ID.
- **From / To**: Depth ranges for each interval.
- **Lithology**: Field containing the rock type or attribute to visualize.

@[INSERT IMAGE HERE: images/guide_drillhole_intervals.png]
*Figure 4c: Drillhole Intervals configuration.*

### Step 5: Generate Preview
1.  Click the **Preview** button (bottom right).
2.  The section will render in the right-hand panel. Use the mouse wheel to zoom and drag to pan.
3.  Use the **Layer Legend** (top right of preview) to toggle visibility of topography, drillholes, or geology.

## 4. New Features in v2.6.0

### 4.1 Interpretation Tool (Drawing)
The new **Interpretation Tool** allows you to draw geological polygons directly on the profile section.

1.  Enable the tool by clicking the **Pencil Icon** in the preview toolbar.
2.  **Drawing**: Left-click to add vertices.
3.  **Snapping**: The cursor will automatically snap to:
    - Topography surface.
    - Drillhole contacts.
    - Existing interpretation vertices.
4.  **Undo**: Right-click to remove the last vertex.
5.  **Finalize**: Double-click (or press Enter) to close the polygon.
6.  **Properties**: A dialog will appear to set the **Lithology**, **Formation**, and **Color** of the new polygon.

@[INSERT IMAGE HERE: images/guide_interpretation_tool.png]
*Figure 5: Digitizing a new geological unit using the Interpretation Tool.*

### 4.2 Exporting to 3D (PolygonZ)
SecInterp now bridges the gap between 2D sections and 3D modeling. This feature allows you to export your 2D interpretations as real 3D objects.

**Workflow:**
1.  Go to the **Settings** tab and check **"Enable 3D Interpretation Export"**.
2.  Use the **Save** button (not Export) to generate your data.
3.  The plugin will create a **PolygonZ** Shapefile in your output folder.
4.  Every vertex of your interpretation is projected into real-world 3D coordinates based on the section plane and surface elevation.

### 4.3 Settings Page
The **Settings** tab manages export configurations and advanced features. It is organized into three sub-tabs:

#### 1. Default Tab (Export Selection)
Control exactly what gets generated when you click **Save**.
- **Topographic Profile**: Exports the surface line (CSV/SHP).
- **Geological Profile**: Exports projected contacts (CSV/SHP).
- **Structural Data**: Exports projected structural measurements (CSV/SHP).
- **Drillhole Data**: Exports traces and interval cylinders (SHP).
- **Interpretations (2D)**: Exports your drawn polygons (SHP).

@[INSERT IMAGE HERE: images/guide_settings_default.png]
*Figure 6a: Default settings showing Export Selection.*

#### 2. Advanced Tab
- **Enable 3D Interpretation Export**: Toggles the generation of **PolygonZ** Shapefiles for your interpretations. This creates true 3D geometries based on the section plane.

@[INSERT IMAGE HERE: images/guide_settings_advanced.png]
*Figure 6b: Advanced settings with 3D Export feature.*

#### 3. Plugin Information Tab
Displays version information, credits, and contact details for SecInterp.

@[INSERT IMAGE HERE: images/guide_settings_info.png]
*Figure 6c: Plugin Information.*

## 5. Preview Panel & Tools
The right-hand panel acts as an interactive canvas for your cross-section. It includes a toolbar and specific controls to manage visualization and performance.

### 5.1 Toolbar Buttons
Located at the top of the preview panel:

- **Preview**: Triggers a refresh of the rendering based on the current configuration in the Settings/Data tabs.
- **Measure**: Activates the interactive ruler. Click on the canvas to measure distances and gradients.
- **Interpret**: Activates the digitization tool for drawing geological polygons completely.
- **Export (Image)**: Saves the **current view** as an image file (PNG, JPG, PDF, SVG). *Note: To export SHP/CSV data, use the main SAVE button.*

### 5.2 Visualization Controls (LOD)
These settings optimize performance for high-resolution datasets:

- **Max Points**: Manually limits the number of vertices rendered for profile lines. Lower values improve zoom/pan speed.
- **Auto**: When checked, the plugin automatically calculates the optimal `Max Points` based on your current window size and resolution.
- **Adaptive**: Enables intelligent sampling algorithm. It preserves key details in complex areas (steep topography, folds) while simplifying flat or linear sections.

### 5.3 Layer Visibility
Use the `Show **` checkboxes to toggle specific data layers on or off without reloading data:

- **Show Topography**: The topographic profile line derived from the DEM.
- **Show Geology**: Projected geological contacts from surface mapping.
- **Show Structures**: Structural measurements (dip/strike) projected onto the plane.
- **Show Drillholes**: Borehole traces and geological interval cylinders.
- **Show Interpretations**: Polygons and units digitized by the user.

### 5.4 Using the Tools

#### Measure Tool
- **Snap-to-Vertex**: Measurements automatically anchor to real data points (DEM or Drillholes).
- **Multi-Segment**: Click multiple times to measure a polyline path.
- **Result Panel**: Displays Total Distance (3D), Horizontal Distance, and Vertical Delta.

@[INSERT IMAGE HERE: images/guide_measure_tool.png]
*Figure 7: Measuring distance along a drillhole trace.*

#### Interpretation Tool
- **Draw**: Left-click to add vertices for a new geological unit.
- **Edit**: Vertices snap to existing lines to ensure topological consistency.
- **Finish**: Double-click to close the polygon and assign attributes (Lithology, Formation).

## 6. Closing & Saving

It is important to understand the difference between **Save** and **OK**:

### **"Save" Button (Export to Disk)**
Use this when you want to **share** your data or use it in other software.
- Generates physical files (Shapefiles, CSV) in your select **Output Folder**.
- Exports:
  - Topographic Profile (LineString)
  - Geological Contacts (Points)
  - Structural Data (Points with Dip/Strike)
  - Drillhole Traces and Intervals (3D Shapefiles)
  - **3D Interpretations** (PolygonZ, if enabled in Settings)

### **"OK" Button (Internal Persistence)**
Use this when you want to **save your progress** and close the dialog, but continue working in QGIS.
- Saves the **current state of the plugin** (selected layers, parameters, window size) into the QGIS Project configuration.
- Saves your **drawn interpretations** internally in the `.qgs` project file so they reappear when you reopen the plugin.
- Closes the window.

### **"Cancel" Button**
- Discards unsaved changes to parameters.
- Closes the window.
