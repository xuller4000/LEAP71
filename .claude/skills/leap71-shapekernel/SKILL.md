---
name: leap71-shapekernel
description: Wissensbasis zur LEAP 71 ShapeKernel (C#, PicoGK) mit vollständigem Quellcode, Doku und Beispielen. Verwenden, wenn Geometrie nach ShapeKernel-Konzepten konstruiert wird (BaseShapes wie Box, Zylinder, Pipe, Lens, Ring, Sphere, LatticePipe; LocalFrame und Frames; Line- und Surface-Modulations; Lattices; Implicits wie Gyroid; Splines; Voxel-Booleans), wenn ShapeKernel- oder PicoGK-Code geschrieben oder erklärt werden soll, oder wenn solche Konstruktionslogik in Autodesk Fusion (Python-API) nachgebaut werden soll.
---

# LEAP 71 ShapeKernel

Die ShapeKernel ist eine C#-Bibliothek von LEAP 71 auf Basis der Geometrie-Engine PicoGK. Sie baut komplexe Bauteile aus einfachen parametrischen Grundkörpern (BaseShapes) auf, die per Boolean und Offset kombiniert werden. Dieser Skill enthält das komplette Repo: Dokumentation, alle Quelldateien, alle Beispiele und alle Abbildungen.

## Wo was liegt

Alles unter `references/` und `assets/` in diesem Skill-Ordner. Lies nur die Datei, die du für die Aufgabe brauchst.

| Zweck | Datei |
|---|---|
| Überblick, Software-Stack | `references/README.md` |
| Setup und erster Task (Program.cs) | `references/README-GettingStarted.md` |
| Konzepte, Namensschema, alle BaseShapes | `references/README-ReadingDetails.md` |
| Alle öffentlichen Klassen und Signaturen mit Zeilennummern | `references/api-index.md` |
| Quellcode BaseShapes | `references/ShapeKernel/BaseShapes/*.cs` |
| Quellcode Frames, Modulations, Splines | `references/ShapeKernel/Frames`, `Modulations`, `Splines` |
| Voxel-, Lattice-, Export-Funktionen (`Sh.*`) | `references/ShapeKernel/Functions/*.cs` |
| Hilfsfunktionen (Vektoren, Splines, Messen, Implicits, Formeln) | `references/ShapeKernel/Utilities/*.cs` |
| Vorschau, Farben, MeshPainter | `references/ShapeKernel/Visualizations/*.cs` |
| Lauffähige Beispiele je BaseShape, Lattice, Implicit | `references/Examples/*.cs` |
| Abbildungen der Doku | `assets/*.jpg`, `assets/*.png` |
| Lizenz | `references/LICENSE` |

Vorgehen bei einer Aufgabe: zuerst `api-index.md` nach der Klasse durchsuchen, dann die Zeilen im Quelltext lesen, und für Verwendungsmuster das passende Beispiel in `Examples/` öffnen (z.B. `Ex_BasePipeShowCase.cs` für Pipes).

## Kernkonzepte

**Geometrietypen.** Voxels (Rasterfeld, Ausgabeformat für STL/CLI/VDB), Lattice (Kugeln und Balken, rund im Querschnitt), Implicit (Signed-Distance-Funktion über `IImplicit.fSignedDistance`). Fertige Formen entstehen, indem alles in ein Voxelfeld gerendert wird: `new Voxels(oLattice)`, `new Voxels(sdf, oBBox)`, `oShape.voxConstruct()`.

**LocalFrame.** Koordinatensystem aus Position plus lokalem x, y, z. Jeder BaseShape wird relativ zu einem LocalFrame gebaut, deshalb lässt er sich platzieren und drehen, ohne die Konstruktion zu ändern. Konstruktoren: `()`, `(vecPos)`, `(vecPos, vecLocalZ)`, `(vecPos, vecLocalZ, vecLocalX)`. Abfragen: `vecGetPosition/LocalX/LocalY/LocalZ`. Ableitungen: `oTranslate`, `oRotate`, `oInvert`.

**Frames.** Folge von LocalFrames entlang einer Spline (der Spine). Lokales z liegt tangential. Die Ausrichtung von x ergibt sich aus einem Zielvektor (`Vector3.UnitY`) oder einem Typ `Frames.EFrameType` (`CYLINDRICAL`, `SPHERICAL`, `Z`, `MIN_ROTATION`). Abfrage: `aFrames.oGetLocalFrame(fLengthRatio)`. Gerade Spine mit konstantem Frame: `new Frames(100, oConstFrame)`.

**Modulations.** Sie beschreiben, wie sich ein Maß entlang normierter Parameter 0..1 ändert. `LineModulation` ist 1D (konstant, Funktion `float f(float fRatio)`, oder Punktliste mit `ECoord`). `SurfaceModulation` ist 2D (konstant, Funktion `f(fPhi, fLengthRatio)`, aus einer LineModulation mit `ELine.FIRST/SECOND`, oder aus einem Bild). Auslesen mit `fGetModulation`. Modulations lassen sich mit `+`, `-` und Skalar `*` verknüpfen.

**Transformationen.** `SetTransformation(Vector3 f(Vector3))` verformt jeden Oberflächenpunkt im absoluten Koordinatensystem (bei Lattice-Shapes jeden Spine-Punkt). Modulation wirkt im Shape-Koordinatensystem, Transformation im globalen.

## BaseShapes

| Klasse | Rahmen | Maße über |
|---|---|---|
| `BaseSphere(oFrame, fRadius)` | LocalFrame | SurfaceModulation über phi, theta (`SetRadius`) |
| `BaseLens(...)` | LocalFrame | feste Radien innen und außen, Höhe oben und unten je SurfaceModulation (`SetHeight(lower, upper)`) |
| `BaseRing(oFrame, fRingRadius, fRadius)` | LocalFrame | SurfaceModulation über alpha, phi (`SetRadius`) |
| `BaseBox(oFrame, fLength, fWidth, fDepth)` oder `(aFrames, fWidth, fDepth)` oder `(BBox3)` | beides | zwei LineModulations (`SetWidth`, `SetDepth`) |
| `BaseCylinder(oFrame, fLength, fRadius)` oder `(aFrames, fRadius)` | beides | SurfaceModulation (`SetRadius`) |
| `BasePipe(...)` | beides | innen und außen je SurfaceModulation (`SetRadius(inner, outer)`) |
| `BasePipeSegment(...)` | beides | wie Pipe, plus Winkelbereich per LineModulation (`EMethod.START_END` oder `MID_RANGE`) |
| `BaseCone(oFrame, fLength, fStartRadius, fEndRadius)` | LocalFrame | linearer Radius, baut auf BaseCylinder |
| `BaseRevolve` | beides | Rotationskörper aus innen/außen LineModulation, `aGetFramesFromContour` |
| `LatticePipe(oFrame, fLength, fRadius)` oder `(aFrames, fRadius)` | beides | LineModulation, rund, auf Lattice-Basis (`latConstruct`) |
| `LatticeManifold` | beides | wie LatticePipe, plus Überhangwinkel für druckbare Tropfenform |
| `BaseLogoBox` | LocalFrame | Box mit Oberflächenmodulation (Logo/Relief) |

Auflösung: `SetLengthSteps`, `SetRadialSteps`, `SetPolarSteps`, `SetWidthSteps`, `SetDepthSteps`. Erzeugen: `voxConstruct()` (Voxels), `mshConstruct()` (Mesh), bei Lattice-Shapes `latConstruct()`. Punkt auf der Oberfläche: `vecGetSurfacePoint(ratio1, ratio2, ratio3)`.

## Splines und Hilfsmittel

`ControlPointSpline(aControlPoints, nDegree, EEnds)` ist eine B-Spline, `TangentialControlSpline` und `CylindricalControlSpline` bauen Spines aus Schritten, `ControlPointSurface` eine B-Spline-Fläche. Alle Splines implementieren `ISpline.aGetPoints(nSamples)`. Weiteres in `SplineOperations` (Reparametrisieren, Länge, Rotation, Verschieben), `VecOperations` (Zylinder-/Kugelkoordinaten, Drehen, Frame-Umrechnung), `Measure` (Volumen, Oberfläche, Schwerpunkt, Trägheitstensor), `CylUtility`/`RectUtility` (schnelle Zylinder, Kegel, Rohre, Boxen als Voxels), `Uf` (Übergänge, Zufall, Fibonacci-Punkte, Polygonradien).

## Voxel-Operationen und Export

Direkt auf `Voxels` (PicoGK): `voxOffset`, `voxSmoothen`, `voxOverOffset`, `voxShell`, `voxProjectZSlice`, `Voxels.voxCombineAll`, Boolean per `voxBoolAdd`/`voxBoolSubtract`/`voxBoolIntersect`. Die `Sh.*`-Wrapper (`Sh.voxUnion`, `Sh.voxSubtract`, `Sh.voxIntersect`, `Sh.voxIntersectImplicit`) sind teils als `[Obsolete]` markiert, dann die PicoGK-Variante nehmen (steht im Attribut). Lattice-Helfer: `Sh.latFromLine/Points/Edges/Grid/Beam`. Export: `Sh.ExportVoxelsToSTLFile`, `ExportMeshToSTLFile`, `ExportVoxelsToVDBFile`, `ExportVoxelsToCLIFile`, Pfad über `Sh.strGetExportPath(EExport, name)`. Vorschau im PicoGK-Viewer über `Sh.PreviewVoxels/Mesh/Lattice...` (siehe `ShPreviewFunctions_I/II.cs`).

## Namensschema (unbedingt einhalten, wenn Code erzeugt wird)

Präfix nach Datentyp: `f` float, `d` double, `i` int, `n` uint, `vec` Vector3, `a` Liste/Array, `s` Struct, `x` Interface, `o` sonstiges Objekt. Memberfelder mit `m_`. Geometrietypen: `lat` Lattice, `sdf` Implicit, `vox` Voxels, `msh` Mesh. Funktionen tragen den Präfix ihres Rückgabetyps (`voxUnion`, `vecRotate`, `aGetPoints`). Namespace `Leap71.ShapeKernel`, Beispiele in `Leap71.ShapeKernelExamples`.

## Typisches Programmgerüst

```csharp
using Leap71.ShapeKernel;
using PicoGK;

try { PicoGK.Library.Go(0.1f, Leap71.ShapeKernelExamples.BaseLensShowCase.Task, strOutputFolder); }
catch (Exception e) { Console.WriteLine(e.ToString()); }
```
Voxelgröße sinnvoll zwischen 0,05 und 1 mm. Ausgabeordner vorher anlegen. Jede Aufgabe ist eine `Task()`-Funktion.

## Umsetzung in Autodesk Fusion

Die ShapeKernel läuft nicht in Fusion, sie ist C# auf PicoGK. Fusion arbeitet mit B-Rep, nicht mit Voxeln. Beim Übertragen gilt:

- BaseCylinder, BaseBox, BasePipe, BaseSphere, BaseRing: Skizze plus Extrusion, Revolve oder Sweep. Die Spine einer Pipe wird zum Sweep-Pfad (Spline durch dieselben Punkte).
- LocalFrame: Konstruktionsebene oder Koordinatensystem, platziert über `Matrix3D` (Ursprung, x-, y-, z-Achse aus dem Frame).
- Modulations: Änderung des Querschnitts entlang der Länge wird zum Loft über mehrere Skizzen, deren Maße aus `fGetModulation(ratio)` berechnet werden, oder zu parametrischen Benutzerparametern.
- Boolean und Offset: `CombineFeatures` (Join, Cut, Intersect) und Offset-/Shell-Features. Voxel-Offsets sind nicht dasselbe wie B-Rep-Offsets bei scharfen Kanten.
- Lattices und Gyroid-Implicits: in Fusion nur mit hohem Aufwand (viele Körper, Vernetzung). Besser als Netz (Mesh) über STL importieren.
- Einheiten: ShapeKernel rechnet in mm, die Fusion-API intern in cm. Alle Längen beim Übertragen durch 10 teilen.

Eigene Konstruktionsrichtlinien des Nutzers haben Vorrang vor Beispielwerten aus den Beispielen.

## Lizenz

Apache License 2.0 (`references/LICENSE`). Urheber: LEAP 71. Bei Weitergabe von Quellcode Lizenz und Hinweise beibehalten.
