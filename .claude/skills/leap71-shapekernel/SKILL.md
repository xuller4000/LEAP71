---
name: leap71-shapekernel
description: Wissensbasis zur LEAP 71 ShapeKernel (C#, PicoGK) mit vollständigem Quellcode, Doku und Beispielen. Verwenden, wenn Geometrie nach ShapeKernel-Konzepten konstruiert wird (BaseShapes wie Box, Zylinder, Pipe, Lens, Ring, Sphere, LatticePipe; LocalFrame und Frames; Line- und Surface-Modulations; Lattices; Implicits wie Gyroid; Splines; Voxel-Booleans), wenn ShapeKernel- oder PicoGK-Code geschrieben oder erklärt werden soll, oder wenn solche Konstruktionslogik in Autodesk Fusion (Python-API) nachgebaut werden soll.
---

# LEAP 71 ShapeKernel

Die ShapeKernel ist eine C#-Bibliothek von LEAP 71 auf Basis der Geometrie-Engine PicoGK. Sie baut komplexe Bauteile aus einfachen parametrischen Grundkörpern (BaseShapes) auf, die per Boolean und Offset kombiniert werden. Diese Datei enthält das komplette Repo in einem Dokument: Dokumentation, alle Quelldateien, alle Beispiele und die Beschreibung aller Abbildungen.

## Aufbau dieser Datei

Alles steht in dieser einen Datei. Suche nach der Überschrift, um die passende Stelle zu finden.

1. Kernkonzepte, BaseShapes, Namensschema, Fusion-Hinweise (Kurzfassung, direkt unten)
2. Anhang A: README.md (Überblick)
3. Anhang B: README-GettingStarted.md
4. Anhang C: README-ReadingDetails.md (Konzepte und alle BaseShapes)
5. Anhang D: Abbildungen (Dateinamen, die in den Dokus referenziert werden, mit Bedeutung)
6. Anhang E: Quellcode `ShapeKernel/` (jede Datei unter eigener Überschrift `### ShapeKernel/<Ordner>/<Datei>.cs`)
7. Anhang F: Beispiele `Examples/` (`### Examples/<Datei>.cs`)
8. Anhang G: LICENSE (Apache 2.0)

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

---

## Anhang A: README.md

### Welcome to ShapeKernel



[Abbildung: shapekernelcreations.png]

*(1) All parts from LEAP 71 were created through Computational Engineering Models based on the ShapeKernel library and the PicoGK engine.*



The LEAP 71 ShapeKernel library bridges the low-level operations of a geometry kernel (in our case PicoGK) and the high-level functions that you want to use, when creating sophisticated engineering objects. It aims to simplify the process of generating geometric primitives that serve as the "atoms" of much more complex designs. For instance, a single heat exchanger part would consist of hundreds of such simple shapes  (called **BaseShapes**) that are logically and spatially combined by Boolean() and Offset() operations. 



[Abbildung: shapekernelexamples.jpg]

*(1) Examples of different BaseShapes.*



The ShapeKernel library is the foundation of the third layer of our software stack, which is the application-specific engineering layer. This layer holds algorithms that encode engineering knowledge and processes for certain kinds of objects, the actual **Computational Engineering Models** (CEMs). 



[Abbildung: softwarestack.jpg]

*(1) Software stack for Computational Engineering.*



Before diving into the details of what BaseShapes exist and how implicits and lattices can be rendered into voxels, let's get started with setting up the library and running an example task:

- [Tutorial 1: Getting Started](Documentation/README-GettingStarted.md)
- [The ShapeKernel — how does it work?](Documentation/README-ReadingDetails.md)

---

## Anhang B: README-GettingStarted.md

### Tutorial 1: ShapeKernel Setup and Running Example Tasks

#### Prep

The LEAP 71 ShapeKernel library [uses PicoGK as the foundational Geometry Engine](https://github.com/leap71/PicoGK). Before going through this tutorial, make sure you were able [to set up PicoGK and run the example project](https://picogk.org/doc/).



#### Including the ShapeKernel Library

At this point, your **Visual Studio (VS) project** [should look like this](https://github.com/leap71/PicoGK_Examples) and a contain a file named  `Program.cs`. 

As a next step, we are adding the ShapeKernel library. This can be done in two ways:

- Beginner
  - download the ShapeKernel source code as zip file from https://github.com/leap71/LEAP71_ShapeKernel/releases (you can pick the latest release available)
  - un-zip and copy the files into your VS project folder
- Pro
  - add ShapeKernel as a submodule, linking the Github repo: https://github.com/leap71/LEAP71_ShapeKernel



[Abbildung: vsproject.png]

*(1) Project structure in VS before and after adding the ShapeKernel library.*



#### Calling a New Task from Program.cs

You have run the `BooleanShowCase.Task` from the PicoGKExamples before. When the project is run and the PicoGK library is initialized, this **Task** function will be excuted. This means that the Task function is the entry point and all the code you want to run should be inside or called from within this function. 

Now, go into the Program.cs file and modify it to make it look like this by copying the code below:



```c#
using Leap71.ShapeKernel;
using PicoGK;

string strOutputFolder = "/Users/youruser/Documents/Examples";

try
{
    PicoGK.Library.Go(
        0.1f,
        Leap71.ShapeKernelExamples.BaseLensShowCase.Task,
        strOutputFolder
        );
}
catch (Exception e)
{
    Console.WriteLine("Failed to run Task.");
    Console.WriteLine(e.ToString());
}
```



We are changing four things here:

- Adding a dedicated output folder
- Changing the voxel size
- Calling an example task from the ShapeKernel library
- Wrapping a try-catch construct around the PicoGK library instantiation.



Per default, PicoGK will export STLs and write log files into your Documents folder. We recommend specifying a dedicated **output folder** (here `strOutputFolder`) for each project. Make sure, this folder already exists on your computer.

We are changing the **voxel size** from 0.5mm to 0.1mm to increase the resolution of the geometries that we are about to produce.

The ShapeKernel library comes with a number of example tasks that generate a few different variations of each BaseShape and showcase how implicits and lattices can be generated. In this case we are calling the `BaseLensShowCase.Task` which will generate a three variations of a type of BaseShape called BaseLens.

[Abbildung: baselenstask.png]

We are adding a try-catch construct around the PicoGK library instantiation in order to be able to read out the error message, should our code fail to run successfully. You can use this Program.cs as a template for all your projects, just update the output folder, pick an adequate voxel size and call the Task function that will be the entry point to your code.

Once you have run the first example successfully, feel free to go through the other Tasks, change the voxel size (sensible values are between 0.05mm and 1mm) and observe the impact. Using the [ShapeKernel documentation](README-ReadingDetails.md) you can dive into the code for the example tasks and start manipulating BaseShapes. Below is a list of example tasks to try out. You can find the code inside the Examples subfolder inside the ShapeKernel folder in your VS project.

- `Leap71.ShapeKernelExamples.BaseBoxShowCase.Task`
- `Leap71.ShapeKernelExamples.BaseCylinderShowCase.Task`
- `Leap71.ShapeKernelExamples.BaseLensShowCase.Task`
- `Leap71.ShapeKernelExamples.BasePipeShowCase.Task`
- `Leap71.ShapeKernelExamples.BasePipeSegmentShowCase.Task`
- `Leap71.ShapeKernelExamples.BaseRingShowCase.Task`
- `Leap71.ShapeKernelExamples.BaseSphereShowCase.Task`
- `Leap71.ShapeKernelExamples.BasicLattices.Task`
- `Leap71.ShapeKernelExamples.ImplicitGyroidSphere.Task`
- `Leap71.ShapeKernelExamples.LatticePipeShowCase.Task`
- `Leap71.ShapeKernelExamples.LatticeManifoldShowCase.Task`



[Abbildung: shapekernelexamples.jpg]

*(1) Examples of different BaseShapes.*

---

## Anhang C: README-ReadingDetails.md

### ShapeKernel Documentation

#### Nomenclature

Variable names typically contain a prefix that marks the data type of an object. This improves readability and makes developers aware of what kind of objects and classes they are dealing with. These are the commonly used data types:

- Floating point values start with f, e.g. `float fValue`
- Double precision floating point values start with d, e.g. `double dVolume`
- Integers start with i, e.g. `int iCounter`
- Unsigned Integers start with n, e.g. `uint nSamples`
- Vectors start with vec, e.g. `Vector3 vecPt`
- Lists / arrays start with a, e.g. `List<Vector3> aPoints`
- Structs start with s, e.g. `SProfile sProfile`
- Interfaces start with x, e.g. `ISpline xSpline`
- All other objects start with o, e.g. `InjectorElement oSwirler`

In addition to that, member variables inside a class are indicated this way:

- Member variable with m_, e.g. `float m_fMass`

There is also a convention for the common geometry data types:
- Lattices in a generic context are called `Lattice oLattice`, in a specific context they start with lat, e.g. `Lattice latPipes`
- Implicits in a generic context are called `IImplicit oImplicit`, in a specific context they start with sdf, e.g. `IImplicit sdfSphere`
- Voxels in a generic context are called `Voxels oVoxels`, in a specific context they start with vox, e.g. `Voxels voxMotor`

The same prefixes apply to functions that return an object of the above mentioned types. A function that returns a voxelfield would be called e.g. `voxUnion()`. A fuction that returns a vector would be called e.g. `vecRotate()`.

The ShapeKernel is implemented using the basic concepts of object-oriented programming (OOP), such as interfaces and inheritance from abstract parent classes. We recommend refreshing your memory regarding those principles as they will be just as useful for the engineering code.



#### Ways to Create Geometries

##### Voxels

Voxels describe a digital material distibution of an object within a regular 3D grid. You can picture it as a stack of black-and-white images, where a white pixel declares matter and a black pixel declares the absence of matter. Fields of Voxels are the most basic, and often native representation of the underlaying geometry kernels that we use. You will not create a field of Voxels by setting individual voxels, but by rendering other geometry data types into a field ("voxelizing"). Many subsequent functions (like `voxBoolean()`, `voxOffset()`, `voxSmoothen()`...) operate directly on Voxels. Inputs (e.g. STL files) will be rendered into voxels. Outputs (e.g. STL files, CLI slices, G-code or Image files...) are all derived from a voxelfield.



[Abbildung: geometryworkflow.jpg]

*(1) Workflow of creating Shapes.*



##### Lattice

Lattices are the most basic way of creating a new shape. Such a lattice is an empty bucket to start with and as you go, you add Nodes or Beams to this bucket. Finally, you can render the lattice into voxels. This field of Voxels will represent the accumulated sum of all nodes and beams that were contained within the lattice object. Lattice nodes are small spheres with a 3D position and a radius. Beams have two points in space that are connected via a conical cylinder. Each point is associated with a respective radius and the ends of the beam can either be rounded or flat-capped. Node-only lattices can be voxelized very efficiently. This is how you can use a Lattice object:

- Instatiate a new lattice:

  ```c#
  Lattice oLattice = new Lattice();
  ```

- Add a node:

  ```c#
  Vector3 vecPt0 = new Vector3(1, 5, 10);
  float fRadius0 = 10;
  oLattice.AddSphere(vecPt0, fRadius0);
  ```

- Add a flat-capped beam:

  ```c#
  Vector3 vecPt1 = new Vector3(5, 3, 0);
  float fRadius1 = 3;
  Vector3 vecPt2 = new Vector3(-3, 0, 7);
  float fRadius2 = 5;
  bool bRounded  = false;
  oLattice.AddBeam(vecPt1, fRadius1, vecPt2, fRadius2, bRounded);
  ```

- Add a rounded beam:

  ```c#
  bRounded = true;
  oLattice.AddBeam(vecPt1, fRadius1, vecPt2, fRadius2, bRounded);
  ```

- Render lattice into a voxelfield

  ```c#
  Voxels oVoxels = new Voxels(oLattice);
  ```

  

[Abbildung: lattices.jpg]

*(1) Node. (2) Variations of beams. (3) Lattice from multiple beams.*



##### Implicits

Implicits describe a shape via a signed-distance function (SDF). This function states for each point in space how far it is away from the surface of the object with a sign marking the inside or outside. Implicits are mainly useful for simple shapes and infill patterns such as gyroids. There are presets for common examples, but you can create a new implicit class that encapsulates your custom SDF. In contrary to the other geometry types, implicits are derived from an interface called `IImplicit`. Some SDFs can be periodic or un-bound. When rendering an inplicit into a voxelfield, your therefore need to either specifiy a bounding box or a bounding voxelfield to intersect with. This is how the code for these steps looks like:

- Use the presets to get SDFs for a sphere and a gyroid:

  ```c#
  IImplicit sdfSphere  = new ImplicitSphere(vecCentre, fRadius);
  IImplicit sdfPattern = new ImplicitGyroid(15, 3);
  ```

- Render an implicit into a new voxel field:

  ```c#
  BBox3 oBBox = new BBox3(
    1.5f * new Vector3(-fRadius, -fRadius, -fRadius), 
    1.5f * new Vector3(fRadius, fRadius, fRadius));
  Voxels voxSphere = new Voxels(sdfSphere, oBBox);
  ```

- Intersect a voxelfield with a 3D pattern (infill):

  ```c#
  Voxels voxGyroidSphere = Sh.voxIntersectImplicit(voxSphere, sdfPattern);
  ```

- Create a custom SDF using a class that implements the implicit interface:

  ```c#
  public class ImplicitSphere : IImplicit
  {
    protected Vector3	m_vecCentre;
    protected float		m_fRadius;
  
    public ImplicitSphere(Vector3 vecCentre, float fRadius)
    {
      m_vecCentre = vecCentre;
      m_fRadius	= fRadius;
    }
  
    public float fSignedDistance(in Vector3 vecPt)
    {
      return (vecPt - m_vecCentre).Length() - m_fRadius;
    }
  }
  ```



[Abbildung: implicits.jpg]

*(1) Sphere from GImplicit. (2) Gyroid-filled Sphere.*



##### Base Shapes

Base Shapes build the core of the Shape Kernel. They are geometric primitives that help you to generate more sophisticated shapes without interacting with the geometry data types directly. In traditional Computer-Aided Design (CAD), there are primitives like cylinders, spheres and boxes with dimensions that can be parametrised. The Shape Kernel uses primitives that are similar on their most basic level, but can be advanced in terms of complexity through **Frames** , **Modulations** and **Transformations**. In oder to understand how Base Shapes are used, we will introduce these three concepts first.



#### Local Frames and Frames

A **Local Frame** is a coordinate system with a position and three orthogonal axes (local x, local y and local z) that can be freely placed and rotated in space. Objects can be constructed with respect to this relative frame of reference rather than the absolute coordinate system. All Base Shapes are constructed with respect to a local frame, which makes it easy to orient and place them in space without having to change their internal construction logic. 


[Abbildung: localframe.jpg]

*(1) Cylinder constructed and placed with respect to the origin of the carthesian coordinate system ("absolute").*

*(2) Local Frame (red).*

*(3) Cylinder constructed and placed with respect to the Local Frame ("relative").*



This is how you can create a new Local Frame:

- Instantiate a Local Frame that is identical with the absolute coordinate system:

  ```c#
  LocalFrame oFrame = new LocalFrame();
  ```

- Instantiate a Local Frame that is translated against the absolute coordinate system:

  ```c#
  LocalFrame oFrame = new LocalFrame(new Vector3(2, 5, -3));
  ```

- Instantiate a Local Frame that has a custom local z direction:

  ```c#
  LocalFrame oFrame = new LocalFrame(new Vector3(2, 5, -3), new Vector3(0, 0, 1));
  LocalFrame oFrame = new LocalFrame(new Vector3(2, 5, -3), new Vector3(1, 0, 0));
  LocalFrame oFrame = new LocalFrame(new Vector3(2, 5, -3), new Vector3(1, 5, -2));
  ```

- Instantiate a Local Frame that has a custom local z and local x direction:

  ```c#
  LocalFrame oFrame = new LocalFrame(new Vector3(2, 5, -3), new Vector3(0, 0, 1), new Vector3(1, 0, 0));
  LocalFrame oFrame = new LocalFrame(new Vector3(2, 5, -3), new Vector3(0, 0, 1), new Vector3(0, 1, 0));
  LocalFrame oFrame = new LocalFrame(new Vector3(2, 5, -3), new Vector3(0, 0, 1), new Vector3(3, -5, 0));
  ```

- Query a Local Frame object for its position and local directions:

  ```c#
  Vector3 vecPos    = oFrame.vecGetPosition();
  Vector3 vecLocalX = oFrame.vecGetLocalX();
  Vector3 vecLocalY = oFrame.vecGetLocalY();
  Vector3 vecLocalZ = oFrame.vecGetLocalZ();
  ```

  

**Frames** are sequences of local frames along a spline in space. They are used to construct pipe-like Base Shapes that do not necessarily have a constant orientation, but evolve / twist along their spines. Within Frames, the local z of each local frame runs tangentially in the direction of the spline. The local x and local y directions lie in a perpendicular plane to that, however there remains a degree of freedom in what way these two vectors are rotated within that plane.

[Abbildung: frames2.jpg]

*(1) Cylinder constructed and placed with respect to the Local Frame ("no spine").*

*(2) Points on a 3D spline*.

*(3) Frames are the result of populating such a spline with a sequence of local frames. Frames are then used to construct a "spined" Base Shape.*



There are multiple options (application-specific) of how local x and local y can be oriented perpendicular to a given location along the spline. If a constant vector is defined as a target, all local x along the spline will be rotated such that they maximize their alignment with the target direction (only when the tangential direction of the spline falls together with the target direction, an deviating / smoothing strategy must be used). Once local z and local x are defined, local y follows automatically to complete a right-hand system. In addition to that, frames can also be designed to target a radial or spherial direction (which is not constant, but depends on the current position in space). You will find radially-targeted frames useful for many engineering objects that have a rotational symmetry, such as pipes, rocket chambers, motors... 

[Abbildung: frametypes.jpg]

*(1) Top view of a spline with significant z-range (that is not visible, but imagine the points as shifted stacks in z) and Y-targeted frames. All local x of all local frames along the spline are rotated to maximise alignment with the absolute y-axis. Note that only local x vectors are shown. Local z vectors are aligned with the spline tangents at each point.* 

*(2) X-targeted frames.*

*(3) Radially-targeted frames.*



Below are some examples of how to get started with Frames. `BasicSpline` is a class that retruns a predefined spline object.

- Create Y-targeted Frames from a spline:

  ```c#
  ISpline oSpline = new BasicSpline();
  Frames aFrames  = new Frames(oSpline.aGetPoints(), Vector3.UnitY);
  ```

- Create radially-targeted Frames from a spline:

  ```c#
  Frames aFrames = new Frames(oSpline.aGetPoints(), Frames.EFrameType.CYLINDRICAL);
  ```

- Create Frames along a straight line with constant target directions:

  ```c#
  LocalFrame oConstFrame = new LocalFrame(
    new Vector3(10, 30, 30), 
    new Vector3(0, 1, 0), 
    new Vector3(0, 0, 1));
  Frames aFrames = new Frames(100, oConstFrame);
  ```

- Query a Local Frame along the spine length:

  ```c#
  float fLengthRatio = 0.2f;
  LocalFrame oFrame = aFrames.oGetLocalFrame(fLengthRatio);
  ```

  

Some Base Shapes can only have a Local Frame, while other Base Shapes have the option to have Frames ("spined").



#### Line and Surface Modulations

All shapes feature a number of surfaces. A surface can be a 3D object, but it is described via two length dimensions. Think of each surface as a normalised 2D interval from 0 to 1. 

A **Line Modulation** is an object that tells a Base Shape how one of its specific dimensions (e.g. the width of a box) evolves across another dimension of a surface (e.g. along its length). Such a functional dependency can be created through different kinds of inputs as shown in the image below.

[Abbildung: linemodulations.jpg]

*(1) Constant Line Modulation that always returns the same value for each point between 0 and 1.* 

*(2) Functional Line Modulation that calculates the value based on a (continuous) delegate function, e.g. a sine wave.*

*(3) Line Modulation that interpolates between a discrete point list (e.g. a spline or measurement series).*



Here are some examples of how to create a new Line Modulation object:

- Instantiate a new Line Modulation based on a constant value:

  ```c#
  LineModulation oLineModulation = new LineModulation(5);
  ```

- Instantiate a new Line Modulation from a function:

  ```c#
  public float fGetWidthOverLengthRatio(float fLengthRatio)
  {
    float fWidth = 30 + 20 * fLengthRatio;
    return fWidth;
  }
  LineModulation oLineModulation = new LineModulation(fGetWidthOverLengthRatio);
  ```

- Instantiate a new Line Modulation from a discrete point list:

  ```c#
  LineModulation oLineModulation = new LineModulation(
    aBSplinePoints,
    LineModulation.ECoord.X,
    LineModulation.ECoord.Z);
  ```

- Query a Line Modulation object for the value at a given ratio:

  ```c#
  float fValue = oLineModulation.fGetModulation(fRatio);
  ```

  

A **Surface Modulation** is the 2D equivalent to the Line Modulation. It tells a Base Shape how one dimension (e.g. the radius of a cylinder) evolves across the two dimensions of a surface (e.g. the mantle surface of a cylinder has a polar and a length dimension). 

[Abbildung: surfacemodulations.jpg]

*(1) Constant Surface Modulation that always returns the same value for each two points between 0 and 1.* 

*(2) 1D functional Surface Modulation that is derived from a Line Modulation.*

*(3)  Functional Surface Modulation that calculates the value based on a (continuous) delegate function, e.g. different sine waves in each dimension .*



Modulation objects are intended to funnel all these different ways of describing a surface into a Base Shape. There are various types of Base Shapes. Depending on their respective topology, some use multiple Line Modulations, some use a Surface Modulation and some use a combination of the two. A modulation is a deformation that is related to the local, shape-specific coordinate system(s). Here are some examples of how to create a new Surface Modulation object:

- Instantiate a new Surface Modulation based on a constant value:

  ```c#
  SurfaceModulation oSurfaceModulation = new SurfaceModulation(5);
  ```

- Instantiate a new Surface Modulation from a function:

  ```c#
  public float fGetRadiusOverPhiLengthRatio(float fPhi, float fLengthRatio)
  {
     float fRadius = 30 + 20 * fLengthRatio + 5f * MathF.Cos(6f * fPhi);
     return fRadius;
  }
  SurfaceModulation oSurfaceModulation = new SurfaceModulation(fGetRadiusOverPhiLengthRatio);
  ```

- Instantiate a new Surface Modulation from a Line Modulation:

  ```c#
  SurfaceModulation oSurfModulation = new SurfaceModulation(oLineModulation);
  SurfaceModulation oSurfModulation = new SurfaceModulation(oLineModulation, SurfaceModulation.ELine.FIRST);
  SurfaceModulation oSurfModulation = new SurfaceModulation(oLineModulation, SurfaceModulation.ELine.SECOND);
  ```
  
- Query a Line Modulation object for the value at a given ratio:

  ```c#
  float fValue = oSurfaceModulation.fGetModulation(fRatio1, fRatio2);
  ```



#### Base Shapes

A **Base Sphere** has a Local Frame. Its radius can be described through a Surface Modulation across phi and theta (polar and azimuthal angles).[Abbildung: basespheres.jpg]

A **Base Lens** has a Local Frame. It has a constant inner and outer radius. The height distribution for the upper and the lower surface can be described via two independant Surface Modulations across phi (polar angle) and the radius ratio.

[Abbildung: baselenses.jpg]

A **Base Ring** has a LocalFrame. It has a constant ring radius. The ring surface can be described via a Surface Modulation across alpha (global polar angle) and phi (local polar angle).

[Abbildung: baserings.jpg]

A **Base Box** can either have a Local Frame or Frames. The width and depth can be described via two independant Line Modulations across the (spine) length ratio.

[Abbildung: baseboxes.jpg]

A **Base Cylinder** can either have a Local Frame or Frames. The radius can be described via a Surface Modulation across the (spine) length ratio.

[Abbildung: basecylinders.jpg]

A **Base Pipe** can either have a Local Frame or Frames. The inner radius and the outer radius can be described via two independant Surface Modulations across the (spine) length ratio.

[Abbildung: basepipes.jpg]

A **Base Pipe Segment** can either have a Local Frame or Frames. The inner radius and the outer radius can be described via two independant Surface Modulations across the (spine) length ratio. In addition to that, it lives on a polar section of a full circle. This section is described through two independant Line Modulations that can either define its start and end polar angles or its mid and (symmetrical) range polar angles across the (spine) length ratio. 

[Abbildung: basepipesegments.jpg]

A **Lattice Pipe** can either have a Local Frame or Frames. The radius can be described via a Line Modulation across the (spine) length ratio. This Base Shape explicitly uses Lattices as the underlaying geometry data type. Since all lattices have a round cross-section, the radius can only be modulated across the length, but not across phi (polar angle).

[Abbildung: latticepipes.jpg]

A **Lattice Manifold** can either have a Local Frame or Frames. The radius can be described via a Line Modulation across the (spine) length ratio. An overhang angle can be defined to dictate the teardrop-shape extension in positive z-direction. The extension can also be toggled for the negative z-direction, resulting in a rhombical cross-section.

[Abbildung: latticemanifolds.jpg]

##### 	

##### Transformations

In addition to Modulations and Frames, all Base Shapes have the option to pass a transformation as a delegate function. Such transformations have the format of `Vector3 vecGetTransformedPoint(Vector3 vecPt)`. 

In contrary to a modulation, a transformation is a deformation that is based on the absolute coordinate system. This way, a Base Shape can be manipulated independently of its topology. For all lattice-based Base Shapes, the specified transformation will apply to each point on the spine. For all other Base Shapes, the tranformation will apply to each point on the surface. Here are some examples:

- Global (linear) transformation of the entire shape:

  ```c#
  public Vector3 vecTransformPoint(Vector3 vecPt)
  {
    Vector3 vecNewPt = vecPt + new Vector3(30, 0, 50);
    return vecNewPt;
  }
  ```

- Local (non-linear) transformation:

  ```c#
  public Vector3 vecTransformPoint(Vector3 vecPt)
  {
    float fRadius = 50 + 20 * vecPt.Z;
    float fBogen  = 2f * MathF.PI * fRadius;
    float fAlpha  = 50f / fBogen * (vecPt.X);
    float fNewZ   = 1.0f * vecPt.Y;
    float fNewX   = fRadius * MathF.Cos(fAlpha);
    float fNewY   = fRadius * MathF.Sin(fAlpha);
    Vector3 vecNewPt = new Vector3(fNewX, fNewY, fNewZ);
    return vecNewPt;
  }
  ```



#### Getting Started

Here is the summary of how you can operate a Base Shape:

- Instantiate a Base Shape with a Local Frame:

  ```c#
  BaseSphere oShape   = new BaseSphere(oFrame, 10);
  BaseCylinder oShape = new BaseCylinder(oFrame, 50, 30);
  ```

- Instantiate a Base Shape with Frames:

  ```c#
  BaseCylinder oShape = new BaseCylinder(aFrames, 30);
  ```

- Set a Line Modulation:

  ```c#
  oShape.SetDepth(oLineModulation);
  oShape.SetDepth(new LineModulation(10));
  oShape.SetWidth(new LineModulation(fGetWidthOverLengthRatio));
  oShape.SetWidth(new LineModulation(aBSplinePoints, LineModulation.ECoord.X, LineModulation.ECoord.Z));
  ```

- Set a Surface Modulation:

  ```c#
  oShape.SetRadius(oSurfaceModulation);
  oShape.SetRadius(new SurfaceModulation(20));
  oShape.SetRadius(new SurfaceModulation(fGetRadiusOverPhiLengthRatio));
  oShape.SetRadius(new SurfaceModulation(oLineModulation));
  ```

- Set a Transformation:

  ```c#
  oShape.SetTransformation(vecGetTransformedPoint);
  ```

- Update the resolution / surface quality:

  ```c#
  oShape.SetLengthSteps(500);
  oShape.SetRadialSteps(500);
  oShape.SetPolarSteps(500);
  ```

- Render Base Shape into voxelfield:

  ```c#
  Voxels oVoxels = oShape.voxConstruct();
  ```



There are many more examples provided in source-code form in the **Examples** folder. The best way to get started is to tinker with simple shapes and enrich them with complexity step-by-step. Head over to the [introduction of setting up the ShapeKernel library and running your first example task!](README-GettingStarted.md)

[Abbildung: shapekernelexamples.jpg]

*(1) Examples of different BaseShapes.*

---

## Anhang D: Abbildungen

Bilddateien aus dem Repo (Ordner `Documentation/`). In den Anhängen A bis C sind sie als `[Abbildung: <Datei>]` markiert, die Bildunterschrift steht jeweils direkt darunter.

- `baseboxes.jpg`
- `basecylinders.jpg`
- `baselenses.jpg`
- `baselenstask.png`
- `basepipes.jpg`
- `basepipesegments.jpg`
- `baserings.jpg`
- `basespheres.jpg`
- `frames.jpg`
- `frames2.jpg`
- `frametypes.jpg`
- `geometryworkflow.jpg`
- `implicits.jpg`
- `latticemanifolds.jpg`
- `latticepipes.jpg`
- `lattices.jpg`
- `linemodulations.jpg`
- `localframe.jpg`
- `program.png`
- `shapekernelcreations.png`
- `shapekernelexamples.jpg`
- `softwarestack.jpg`
- `spinedcylinder.jpg`
- `spinedlengthmodulatedcylinder.jpg`
- `spinedpolarmodulatedcylinder.jpg`
- `surfacemodulations.jpg`
- `vsproject.png`

---

## Anhang E: Quellcode ShapeKernel

### ShapeKernel/BaseShapes/BaseBox.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class BaseBox : BaseShape, IMeshBaseShape,ISurfaceBaseShape
        {
            protected int               m_nLengthSteps;
            protected int               m_nWidthSteps;
            protected int               m_nDepthSteps;
            protected LineModulation    m_oWidthModulation;
            protected LineModulation    m_oDepthModulation;
            protected Frames            m_aFrames;

            /// <summary>
            /// Initialises a box based on a local frame and 3 dimensions.
            /// The shape has no spine.
            /// Width correlates to local x dimension.
            /// Depth correlates to local y dimension.
            /// </summary>
            public BaseBox(
                LocalFrame oFrame,
                float fLength = 20,
                float fWidth = 20,
                float fDepth = 20) : base()
            {
                m_aFrames = new Frames(fLength, oFrame);
                SetWidthSteps(5);
                SetDepthSteps(5);
                SetLengthSteps(5);

                m_oWidthModulation  = new LineModulation(fWidth);
                m_oDepthModulation  = new LineModulation(fDepth);
            }

            protected BaseBox() { }

            /// <summary>
            /// Initialises a box based on a spine (frames) and 2 dimensions.
            /// The spine replaces the length dimension.
            /// Width correlates to local x dimension.
            /// Depth correlates to local y dimension.
            /// </summary>
            public BaseBox(
                Frames aFrames,
                float fWidth = 20,
                float fDepth = 20) : base()
            {
                m_aFrames = aFrames;
                SetWidthSteps(5);
                SetDepthSteps(5);
                SetLengthSteps(500);

                m_oWidthModulation  = new LineModulation(fWidth);
                m_oDepthModulation  = new LineModulation(fDepth);
            }

            /// <summary>
            /// Initialises a box from a BBox3 object (e.g. of a voxel field).
            /// </summary>
            public BaseBox(BBox3 oBBox) : base()
            {
                float fWidth        = oBBox.vecSize().X;
                float fDepth        = oBBox.vecSize().Y;
                float fLength       = oBBox.vecSize().Z;

                Vector3 vecCentre   = oBBox.vecCenter();
                vecCentre.Z         = oBBox.vecMin.Z;
                LocalFrame oFrame   = new (vecCentre);

                m_aFrames = new Frames(fLength, oFrame);
                SetWidthSteps(5);
                SetDepthSteps(5);
                SetLengthSteps(5);

                m_oWidthModulation  = new LineModulation(fWidth);
                m_oDepthModulation  = new LineModulation(fDepth);
            }


            //settings
            public void SetWidth(LineModulation oModulation)
            {
                m_oWidthModulation = oModulation;
                SetWidthSteps(500);
                SetLengthSteps(500);
            }

            public void SetDepth(LineModulation oModulation)
            {
                m_oDepthModulation = oModulation;
                SetDepthSteps(500);
                SetLengthSteps(500);
            }

            public void SetWidthSteps(int nWidthSteps)
            {
                m_nWidthSteps = Math.Max(5, nWidthSteps);
            }

            public void SetDepthSteps(int nDepthSteps)
            {
                m_nDepthSteps = Math.Max(5, nDepthSteps);
            }

            public void SetLengthSteps(int nLengthSteps)
            {
                m_nLengthSteps = Math.Max(5, nLengthSteps);
            }


            //construction
            public override Voxels voxConstruct()
            {
                Mesh oMesh      = mshConstruct();
                Voxels oVoxels  = new Voxels(oMesh);
                return oVoxels;
            }

            public Mesh mshConstruct()
            {
                Mesh oMesh = new Mesh();
                AddTopSurface(ref oMesh, true);
                AddBottomSurface(ref oMesh);
                AddFrontSurface(ref oMesh, true);
                AddBackSurface(ref oMesh);
                AddRightSurface(ref oMesh, true);
                AddLeftSurface(ref oMesh);
                return oMesh;
            }

            //sides
            protected void AddTopSurface(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across width and depth
                int iLengthStep     = m_nLengthSteps - 1;
                float fLR           = fGetLengthRatioFromStep(iLengthStep);

                for (int iWidthStep = 1; iWidthStep < m_nWidthSteps; iWidthStep++)
                {
                    float fWidthRatio1 = fGetWidthRatioFromStep(iWidthStep - 1);
                    float fWidthRatio2 = fGetWidthRatioFromStep(iWidthStep);

                    for (int iDepthStep = 1; iDepthStep < m_nDepthSteps; iDepthStep++)
                    {
                        float fDepthRatio1 = fGetDepthRatioFromStep(iDepthStep - 1);
                        float fDepthRatio2 = fGetDepthRatioFromStep(iDepthStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fWidthRatio1, fDepthRatio1, fLR);
                        Vector3 vecPt1 = vecGetSurfacePoint(fWidthRatio1, fDepthRatio2, fLR);
                        Vector3 vecPt2 = vecGetSurfacePoint(fWidthRatio2, fDepthRatio2, fLR);
                        Vector3 vecPt3 = vecGetSurfacePoint(fWidthRatio2, fDepthRatio1, fLR);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            protected void AddBottomSurface(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across width and depth
                int iLengthStep     = 0;
                float fLR           = fGetLengthRatioFromStep(iLengthStep);

                for (int iWidthStep = 1; iWidthStep < m_nWidthSteps; iWidthStep++)
                {
                    float fWidthRatio1 = fGetWidthRatioFromStep(iWidthStep - 1);
                    float fWidthRatio2 = fGetWidthRatioFromStep(iWidthStep);

                    for (int iDepthStep = 1; iDepthStep < m_nDepthSteps; iDepthStep++)
                    {
                        float fDepthRatio1 = fGetDepthRatioFromStep(iDepthStep - 1);
                        float fDepthRatio2 = fGetDepthRatioFromStep(iDepthStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fWidthRatio1, fDepthRatio1, fLR);
                        Vector3 vecPt1 = vecGetSurfacePoint(fWidthRatio1, fDepthRatio2, fLR);
                        Vector3 vecPt2 = vecGetSurfacePoint(fWidthRatio2, fDepthRatio2, fLR);
                        Vector3 vecPt3 = vecGetSurfacePoint(fWidthRatio2, fDepthRatio1, fLR);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            protected void AddFrontSurface(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across length and depth
                int iWidthStep      = 0;
                float fWidthRatio   = fGetWidthRatioFromStep(iWidthStep);

                for (int iLengthStep = 1; iLengthStep < m_nLengthSteps; iLengthStep++)
                {
                    float fLR1 = fGetLengthRatioFromStep(iLengthStep - 1);
                    float fLR2 = fGetLengthRatioFromStep(iLengthStep);

                    for (int iDepthStep = 1; iDepthStep < m_nDepthSteps; iDepthStep++)
                    {
                        float fDepthRatio1 = fGetDepthRatioFromStep(iDepthStep - 1);
                        float fDepthRatio2 = fGetDepthRatioFromStep(iDepthStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fWidthRatio, fDepthRatio1, fLR1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fWidthRatio, fDepthRatio2, fLR1);
                        Vector3 vecPt2 = vecGetSurfacePoint(fWidthRatio, fDepthRatio2, fLR2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fWidthRatio, fDepthRatio1, fLR2);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            protected void AddBackSurface(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across length and depth
                int iWidthStep      = (int)m_nWidthSteps - 1;
                float fWidthRatio   = fGetWidthRatioFromStep(iWidthStep);

                for (int iLengthStep = 1; iLengthStep < m_nLengthSteps; iLengthStep++)
                {
                    float fLR1 = fGetLengthRatioFromStep(iLengthStep - 1);
                    float fLR2 = fGetLengthRatioFromStep(iLengthStep);

                    for (int iDepthStep = 1; iDepthStep < m_nDepthSteps; iDepthStep++)
                    {
                        float fDepthRatio1 = fGetDepthRatioFromStep(iDepthStep - 1);
                        float fDepthRatio2 = fGetDepthRatioFromStep(iDepthStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fWidthRatio, fDepthRatio1, fLR1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fWidthRatio, fDepthRatio2, fLR1);
                        Vector3 vecPt2 = vecGetSurfacePoint(fWidthRatio, fDepthRatio2, fLR2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fWidthRatio, fDepthRatio1, fLR2);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            protected void AddLeftSurface(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across length and width
                int iDepthStep      = 0;
                float fDepthRatio   = fGetDepthRatioFromStep(iDepthStep);

                for (int iLengthStep = 1; iLengthStep < m_nLengthSteps; iLengthStep++)
                {
                    float fLR1 = fGetLengthRatioFromStep(iLengthStep - 1);
                    float fLR2 = fGetLengthRatioFromStep(iLengthStep);

                    for (int iWidthStep = 1; iWidthStep < m_nWidthSteps; iWidthStep++)
                    {
                        float fWidthRatio1 = fGetWidthRatioFromStep(iWidthStep - 1);
                        float fWidthRatio2 = fGetWidthRatioFromStep(iWidthStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fWidthRatio1, fDepthRatio, fLR1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fWidthRatio2, fDepthRatio, fLR1);
                        Vector3 vecPt2 = vecGetSurfacePoint(fWidthRatio2, fDepthRatio, fLR2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fWidthRatio1, fDepthRatio, fLR2);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            protected void AddRightSurface(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across length and width
                int iDepthStep      = (int)m_nDepthSteps - 1;
                float fDepthRatio   = fGetDepthRatioFromStep(iDepthStep);

                for (int iLengthStep = 1; iLengthStep < m_nLengthSteps; iLengthStep++)
                {
                    float fLR1 = fGetLengthRatioFromStep(iLengthStep - 1);
                    float fLR2 = fGetLengthRatioFromStep(iLengthStep);

                    for (int iWidthStep = 1; iWidthStep < m_nWidthSteps; iWidthStep++)
                    {
                        float fWidthRatio1 = fGetWidthRatioFromStep(iWidthStep - 1);
                        float fWidthRatio2 = fGetWidthRatioFromStep(iWidthStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fWidthRatio1, fDepthRatio, fLR1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fWidthRatio2, fDepthRatio, fLR1);
                        Vector3 vecPt2 = vecGetSurfacePoint(fWidthRatio2, fDepthRatio, fLR2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fWidthRatio1, fDepthRatio, fLR2);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            //step conversions
            protected float fGetDepthRatioFromStep(int iDepthStep)
            {
                //from -1 to +1
                float fDepthRatio   = (1f) / (m_nDepthSteps - 1f) * (iDepthStep);
                fDepthRatio         = 2f * fDepthRatio - 1f;
                return fDepthRatio;
            }

            protected float fGetWidthRatioFromStep(int iWidthStep)
            {
                //from -1 to +1
                float fWidthRatio   = (1f) / (m_nWidthSteps - 1f) * (iWidthStep);
                fWidthRatio         = 2f * fWidthRatio - 1f;
                return fWidthRatio;
            }

            protected float fGetLengthRatioFromStep(int iLengthStep)
            {
                //from 0 to +1
                float fLR = (1f) / (m_nLengthSteps - 1f) * (iLengthStep);
                return fLR;
            }

            /// <summary>
            /// Returns a point on the shape surface if one of the ratios is at the limit.
            /// Returns a point inside the shape if all ratios are within the limits.
            /// Width ratio goes from -1 to 1.
            /// Depth ratio goes from -1 to 1.
            /// Length ratio goes from 0 to 1.
            /// </summary>
            public virtual Vector3 vecGetSurfacePoint(float fWidthRatio, float fDepthRatio, float fLR)
            {
                Vector3 vecSpinePos = m_aFrames.vecGetSpineAlongLength(fLR);
                Vector3 vecLocalX   = m_aFrames.vecGetLocalXAlongLength(fLR);
                Vector3 vecLocalY   = m_aFrames.vecGetLocalYAlongLength(fLR);

                float fX            = 0.5f * fWidthRatio * fGetWidth(fLR);
                float fY            = 0.5f * fDepthRatio * fGetDepth(fLR);
                Vector3 vecPt       = vecSpinePos + fX * vecLocalX + fY * vecLocalY;

                return m_fnTrafo(vecPt);;
            }

            protected float fGetDepth(float fLR)
            {
                float fDepth = m_oDepthModulation.fGetModulation(fLR);
                return fDepth;
            }

            protected float fGetWidth(float fLR)
            {
                float fWidth = m_oWidthModulation.fGetModulation(fLR);
                return fWidth;
            }
        }
    }
}
```

### ShapeKernel/BaseShapes/BaseCone.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using PicoGK;


namespace Leap71
{
	namespace ShapeKernel
	{
		public class BaseCone : BaseShape
        {
			protected BaseCylinder	m_oCyl;
			protected float			m_fStartRadius;
			protected float			m_fEndRadius;

			/// <summary>
			/// Simple cone shape with a linear radius distribution between start and end radius.
			/// Derived from BaseCylinder.
			/// </summary>
			public BaseCone(LocalFrame oFrame, float fLength, float fStartRadius, float fEndRadius)
			{
				m_fStartRadius	= fStartRadius;
				m_fEndRadius	= fEndRadius;
				m_oCyl			= new BaseCylinder(oFrame, fLength);
				m_oCyl.SetRadius(new SurfaceModulation(fGetLinearRadius));
			}

			protected float fGetLinearRadius(float fPhi, float fLengthRatio)
			{
				fLengthRatio = float.Clamp(fLengthRatio, 0f, 1f);
				return m_fStartRadius + fLengthRatio * (m_fEndRadius - m_fStartRadius);
			}

			public override Voxels voxConstruct()
			{
				m_oCyl.SetTransformation(m_fnTrafo);
                return m_oCyl.voxConstruct();
            }

			public BaseCylinder oGetBaseCylinder()
			{
				return m_oCyl;
			}
		}
	}
}
```

### ShapeKernel/BaseShapes/BaseCylinder.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class BaseCylinder : BaseShape, IMeshBaseShape, ISurfaceBaseShape
        {
            protected uint              m_nLengthSteps;
            protected uint              m_nPolarSteps;
            protected uint              m_nRadialSteps;
            protected SurfaceModulation m_oRadiusModulation;
            protected Frames            m_aFrames;

            /// <summary>
            /// Initialises a cylinder based on a local frame and 2 dimensions.
            /// The shape has no spine.
            /// </summary>
            public BaseCylinder(
                LocalFrame oFrame,
                float fLength = 20,
                float fRadius = 10) : base()
            {
                m_aFrames = new Frames(fLength, oFrame);
                SetPolarSteps(360);
                SetRadialSteps(5);
                SetLengthSteps(5);

                m_oRadiusModulation = new SurfaceModulation(fRadius);
            }

            /// <summary>
            /// Initialises a cylinder based on a spine (frames) and 1 dimension.
            /// The spine replaces the length dimension.
            /// </summary>
            public BaseCylinder(
                Frames aFrames,
                float fRadius = 10) : base()
            {
                m_aFrames = aFrames;
                SetPolarSteps(360);
                SetRadialSteps(5);
                SetLengthSteps(500);

                m_oRadiusModulation = new SurfaceModulation(fRadius);
            }


            //settings
            public void SetRadius(SurfaceModulation oModulation)
            {
                m_oRadiusModulation = oModulation;
                SetLengthSteps(500);
            }

            public void SetRadialSteps(uint nRadialSteps)
            {
                m_nRadialSteps = Math.Max(5, nRadialSteps);
            }

            public void SetPolarSteps(uint nPolarSteps)
            {
                m_nPolarSteps = Math.Max(5, nPolarSteps);
            }

            public void SetLengthSteps(uint nLengthSteps)
            {
                m_nLengthSteps = Math.Max(5, nLengthSteps);
            }


            //construction
            public override Voxels voxConstruct()
            {
                Mesh oMesh      = mshConstruct();
                Voxels oVoxels  = new Voxels(oMesh);
                return oVoxels;
            }

            public Mesh mshConstruct()
            {
                Mesh oMesh = new Mesh();
                AddTopSurface(ref oMesh);
                AddOuterMantle(ref oMesh);
                AddBottomSurface(ref oMesh);
                return oMesh;
            }


            //sides
            protected void AddTopSurface(ref Mesh oMesh)
            {
                //iterate across phi and radius
                int iLengthStep     = (int)m_nLengthSteps - 1;
                float fLengthRatio  = fGetLengthRatioFromStep(iLengthStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhiRatio1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhiRatio2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iRadiusStep = 1; iRadiusStep < m_nRadialSteps; iRadiusStep++)
                    {
                        float fRadiusRatio1 = fGetRadiusRatioFromStep(iRadiusStep - 1);
                        float fRadiusRatio2 = fGetRadiusRatioFromStep(iRadiusStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio, fPhiRatio1, fRadiusRatio1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio, fPhiRatio1, fRadiusRatio2);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio, fPhiRatio2, fRadiusRatio2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio, fPhiRatio2, fRadiusRatio1);
                        oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                        oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                    }
                }
            }

            protected void AddBottomSurface(ref Mesh oMesh)
            {
                //iterate across phi and radius
                int iLengthStep     = 0;
                float fLengthRatio  = fGetLengthRatioFromStep(iLengthStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhiRatio1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhiRatio2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iRadiusStep = 1; iRadiusStep < m_nRadialSteps; iRadiusStep++)
                    {
                        float fRadiusRatio1 = fGetRadiusRatioFromStep(iRadiusStep - 1);
                        float fRadiusRatio2 = fGetRadiusRatioFromStep(iRadiusStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio, fPhiRatio1, fRadiusRatio1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio, fPhiRatio1, fRadiusRatio2);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio, fPhiRatio2, fRadiusRatio2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio, fPhiRatio2, fRadiusRatio1);
                        oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                        oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                    }
                }
            }

            protected void AddOuterMantle(ref Mesh oMesh)
            {
                //iterate across phi and length
                int iRadiusStep     = (int)m_nRadialSteps - 1;
                float fRadiusRatio  = fGetRadiusRatioFromStep(iRadiusStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhiRatio1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhiRatio2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iLengthStep = 1; iLengthStep < m_nLengthSteps; iLengthStep++)
                    {
                        float fLengthRatio1 = fGetLengthRatioFromStep(iLengthStep - 1);
                        float fLengthRatio2 = fGetLengthRatioFromStep(iLengthStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio1, fPhiRatio1, fRadiusRatio);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio2, fPhiRatio1, fRadiusRatio);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio2, fPhiRatio2, fRadiusRatio);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio1, fPhiRatio2, fRadiusRatio);
                        oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                        oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                    }
                }
            }


            //step conversions
            protected float fGetRadiusRatioFromStep(int iRadiusStep)
            {
                float fRadiusRatio = (1f) / (m_nRadialSteps - 1) * (iRadiusStep);
                return fRadiusRatio;
            }

            protected float fGetPhiRatioFromStep(int iPhiStep)
            {
                float fPhi = (1f) / (m_nPolarSteps - 1) * (iPhiStep);
                return fPhi;
            }

            protected float fGetLengthRatioFromStep(int iLengthStep)
            {
                float fLengthRatio = (1f) / (m_nLengthSteps - 1) * (iLengthStep);
                return fLengthRatio;
            }

            /// <summary>
            /// Returns a point on the shape surface if one of the ratios is at the limit.
            /// Returns a point inside the shape if all ratios are within the limits.
            /// All ratios go from 0 to 1.
            /// </summary>
            public Vector3 vecGetSurfacePoint(float fLengthRatio, float fPhiRatio, float fRadiusRatio)
            {
                float fPhi = 2f * MathF.PI * fPhiRatio;

                Vector3 vecSpinePos = m_aFrames.vecGetSpineAlongLength(fLengthRatio);
                Vector3 vecLocalX   = m_aFrames.vecGetLocalXAlongLength(fLengthRatio);
                Vector3 vecLocalY   = m_aFrames.vecGetLocalYAlongLength(fLengthRatio);

                float fRadius       = fRadiusRatio * fGetRadius(fPhi, fLengthRatio);

                float fX = fRadius * MathF.Cos(fPhi);
                float fY = fRadius * MathF.Sin(fPhi);
                Vector3 vecPt = vecSpinePos + fX * vecLocalX + fY * vecLocalY;

                return m_fnTrafo(vecPt);
            }

            protected float fGetRadius(float fPhi, float fLengthRatio)
            {
                float fRadius = m_oRadiusModulation.fGetModulation(fPhi, fLengthRatio);
                return fRadius;
            }
        }
    }
}
```

### ShapeKernel/BaseShapes/BaseLens.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class BaseLens : BaseShape, IMeshBaseShape, ISurfaceBaseShape
        {
            protected uint              m_nRadialSteps;
            protected uint              m_nPolarSteps;
            protected uint              m_nHeightSteps;
            protected float             m_fInnerRadius;
            protected float             m_fOuterRadius;
            protected SurfaceModulation m_oUpperModulation;
            protected SurfaceModulation m_oLowerModulation;
            protected LocalFrame        m_oFrame;

            /// <summary>
            /// Initialises a lense based on a local frame and 2 dimensions.
            /// For the radial dimension, an inner and an outer radius can be specified.
            /// The shape has no spine.
            /// </summary>
            public BaseLens(
                LocalFrame oFrame,
                float fHeight,
                float fInnerRadius,
                float fOuterRadius) : base()
            {
                m_oFrame = oFrame;
                SetRadialSteps(5);
                SetPolarSteps(360);
                SetHeightSteps(5);

                m_fInnerRadius      = fInnerRadius;
                m_fOuterRadius      = fOuterRadius;
                m_oLowerModulation  = new SurfaceModulation(0);
                m_oUpperModulation  = new SurfaceModulation(fHeight);
            }


            //settings
            public void SetHeight(SurfaceModulation oLowerModulation, SurfaceModulation oUpperModulation)
            {
                m_oLowerModulation = oLowerModulation;
                m_oUpperModulation = oUpperModulation;
                SetRadialSteps(500);
            }

            public void SetRadialSteps(uint nRadialSteps)
            {
                m_nRadialSteps = Math.Max(5, nRadialSteps);
            }

            public void SetPolarSteps(uint nPolarSteps)
            {
                m_nPolarSteps = Math.Max(5, nPolarSteps);
            }

            public void SetHeightSteps(uint nHeightSteps)
            {
                m_nHeightSteps = Math.Max(5, nHeightSteps);
            }


            //construction
            public override Voxels voxConstruct()
            {
                Mesh oMesh      = mshConstruct();
                Voxels oVoxels  = new Voxels(oMesh);
                return oVoxels;
            }

            public Mesh mshConstruct()
            {
                Mesh oMesh = new Mesh();
                AddTopSurface(ref oMesh);
                AddBottomSurface(ref oMesh, true);
                AddInnerMantle(ref oMesh);
                AddOuterMantle(ref oMesh, true);
                return oMesh;
            }


            //sides
            protected void AddTopSurface(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across phi and radius
                float fHeightRatio = 1f;

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhiRatio1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhiRatio2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iRadiusStep = 1; iRadiusStep < m_nRadialSteps; iRadiusStep++)
                    {
                        float fRadiusRatio1 = fGetRadiusRatioFromStep(iRadiusStep - 1);
                        float fRadiusRatio2 = fGetRadiusRatioFromStep(iRadiusStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fHeightRatio, fPhiRatio1, fRadiusRatio1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fHeightRatio, fPhiRatio1, fRadiusRatio2);
                        Vector3 vecPt2 = vecGetSurfacePoint(fHeightRatio, fPhiRatio2, fRadiusRatio2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fHeightRatio, fPhiRatio2, fRadiusRatio1);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            protected void AddBottomSurface(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across phi and radius
                float fHeightRatio = 0f;

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhiRatio1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhiRatio2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iRadiusStep = 1; iRadiusStep < m_nRadialSteps; iRadiusStep++)
                    {
                        float fRadiusRatio1 = fGetRadiusRatioFromStep(iRadiusStep - 1);
                        float fRadiusRatio2 = fGetRadiusRatioFromStep(iRadiusStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fHeightRatio, fPhiRatio1, fRadiusRatio1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fHeightRatio, fPhiRatio1, fRadiusRatio2);
                        Vector3 vecPt2 = vecGetSurfacePoint(fHeightRatio, fPhiRatio2, fRadiusRatio2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fHeightRatio, fPhiRatio2, fRadiusRatio1);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            protected void AddInnerMantle(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across phi and height
                int iRadiusStep = 0;
                float fRadiusRatio = fGetRadiusRatioFromStep(iRadiusStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhiRatio1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhiRatio2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iHeightStep = 1; iHeightStep < m_nHeightSteps; iHeightStep++)
                    {
                        float fHeightRatio1 = fGetHeightRatioFromStep(iHeightStep - 1);
                        float fHeightRatio2 = fGetHeightRatioFromStep(iHeightStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fHeightRatio1, fPhiRatio1, fRadiusRatio);
                        Vector3 vecPt1 = vecGetSurfacePoint(fHeightRatio2, fPhiRatio1, fRadiusRatio);
                        Vector3 vecPt2 = vecGetSurfacePoint(fHeightRatio2, fPhiRatio2, fRadiusRatio);
                        Vector3 vecPt3 = vecGetSurfacePoint(fHeightRatio1, fPhiRatio2, fRadiusRatio);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            protected void AddOuterMantle(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across phi and height
                int iRadiusStep     = (int)m_nRadialSteps - 1;
                float fRadiusRatio  = fGetRadiusRatioFromStep(iRadiusStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhiRatio1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhiRatio2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iHeightStep = 1; iHeightStep < m_nHeightSteps; iHeightStep++)
                    {
                        float fHeightRatio1 = fGetHeightRatioFromStep(iHeightStep - 1);
                        float fHeightRatio2 = fGetHeightRatioFromStep(iHeightStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fHeightRatio1, fPhiRatio1, fRadiusRatio);
                        Vector3 vecPt1 = vecGetSurfacePoint(fHeightRatio2, fPhiRatio1, fRadiusRatio);
                        Vector3 vecPt2 = vecGetSurfacePoint(fHeightRatio2, fPhiRatio2, fRadiusRatio);
                        Vector3 vecPt3 = vecGetSurfacePoint(fHeightRatio1, fPhiRatio2, fRadiusRatio);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }


            //step conversions
            protected float fGetRadiusRatioFromStep(int iRadiusStep)
            {
                float fRadiusRatio = (1f) / (m_nRadialSteps - 1) * (iRadiusStep);
                return fRadiusRatio;
            }

            protected float fGetPhiRatioFromStep(int iPhiStep)
            {
                float fPhi = (1f) / (m_nPolarSteps - 1) * (iPhiStep);
                return fPhi;
            }

            protected float fGetHeightRatioFromStep(int iHeightStep)
            {
                float fHeightRatio = (1f) / (m_nHeightSteps - 1) * (iHeightStep);
                return fHeightRatio;
            }

            /// <summary>
            /// Returns a point on the shape surface if one of the ratios is at the limit.
            /// Returns a point inside the shape if all ratios are within the limits.
            /// All ratios go from 0 to 1.
            /// </summary>
            public Vector3 vecGetSurfacePoint(float fHeightRatio, float fPhiRatio, float fRadiusRatio)
            {
                float fPhi      = 2f * MathF.PI * fPhiRatio;
                float fRadius   = (m_fOuterRadius - m_fInnerRadius) * fRadiusRatio + m_fInnerRadius;

                float fZ = fGetHeight(fHeightRatio, fPhi, fRadiusRatio);
                float fX = fRadius * MathF.Cos(fPhi);
                float fY = fRadius * MathF.Sin(fPhi);

                Vector3 vecPt = m_oFrame.vecGetPosition()
                    + fX * m_oFrame.vecGetLocalX()
                    + fY * m_oFrame.vecGetLocalY()
                    + fZ * m_oFrame.vecGetLocalZ();

                return m_fnTrafo(vecPt);
            }

            protected float fGetHeight(float fHeightRatio, float fPhi, float fRadiusRatio)
            {
                float fLowerHeight  = m_oLowerModulation.fGetModulation(fPhi, fRadiusRatio);
                float fUpperHeight  = m_oUpperModulation.fGetModulation(fPhi, fRadiusRatio);
                float fHeight       = fLowerHeight + fHeightRatio * (fUpperHeight - fLowerHeight);
                return fHeight;
            }
        }
    }
}
```

### ShapeKernel/BaseShapes/BaseLogoBox.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        using static SurfaceModulation;

        public class BaseLogoBox : BaseBox
        {
            protected SurfaceModulation m_oTopModulation;

            /// <summary>
            /// Initialises a box based on a local frame and 3 dimensions.
            /// The top surface of the box will be modulated according to the specified image.
            /// The mapping functions describes the relationship between grayscale pixel values and physical modulation value.
            /// The shape has no spine.
            /// Width correlates to local x dimension.
            /// Depth correlates to local y dimension.
            /// </summary>
            public BaseLogoBox( LocalFrame  oFrame,
                                float       fLength,
                                float       fRefWidth,
                                Image       oImage,
                                MappingFunc oMappingFunc) : base()
            {
                m_aFrames           = new Frames(fLength, oFrame);
                int iImageWidth     = oImage.nWidth;
                int iImageHeight    = oImage.nHeight;
                SetWidthSteps(iImageWidth);
                SetDepthSteps(iImageHeight);
                SetLengthSteps(5);

                float fWidth        = fRefWidth;
                float fDepth        = (float)iImageHeight / (float)iImageWidth * fRefWidth;

                m_oWidthModulation  = new LineModulation(fWidth);
                m_oDepthModulation  = new LineModulation(fDepth);
                m_oTopModulation    = new SurfaceModulation(oImage, oMappingFunc);
            }

            public float fGetWidth()
            {
                return m_oWidthModulation.m_fConstValue;
            }

            public float fGetDepth()
            {
                return m_oDepthModulation.m_fConstValue;
            }

            public override Vector3 vecGetSurfacePoint( float fWidthRatio,
                                                        float fDepthRatio,
                                                        float fLengthRatio)
            {
                Vector3 vecSpinePos = m_aFrames.vecGetSpineAlongLength(fLengthRatio);
                Vector3 vecLocalX   = m_aFrames.vecGetLocalXAlongLength(fLengthRatio);
                Vector3 vecLocalY   = m_aFrames.vecGetLocalYAlongLength(fLengthRatio);
                Vector3 vecLocalZ   = m_aFrames.vecGetLocalZAlongLength(fLengthRatio);

                float fX            = 0.5f * fWidthRatio * fGetWidth(fLengthRatio);
                float fY            = 0.5f * fDepthRatio * fGetDepth(fLengthRatio);
                Vector3 vecPt       = vecSpinePos + fX * vecLocalX + fY * vecLocalY;

                //top surface modulation
                if (MathF.Abs(fLengthRatio - 1f) < 0.0003f)
                {
                    float fImageWidthRatio  = 1f - (0.5f + 0.5f * fWidthRatio);
                    float fImageHeightRatio = 1f - (0.5f + 0.5f * fDepthRatio);
                    float dZ                = m_oTopModulation.fGetModulation(fImageWidthRatio, fImageHeightRatio);
                    vecPt += dZ * vecLocalZ;
                }

                return m_fnTrafo(vecPt);
            }
        }
    }
}
```

### ShapeKernel/BaseShapes/BasePipe.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class BasePipe : BaseShape, IMeshBaseShape, ISurfaceBaseShape
        {
            protected uint              m_nLengthSteps;
            protected uint              m_nPolarSteps;
            protected uint              m_nRadialSteps;
            protected SurfaceModulation m_oOuterRadiusModulation;
            protected SurfaceModulation m_oInnerRadiusModulation;
            protected Frames            m_aFrames;

            /// <summary>
            /// Initialises a pipe based on a local frame and 2 dimensions.
            /// For the radial dimension, an inner and an outer radius can be specified.
            /// The shape has no spine.
            /// </summary>
            public BasePipe(
                LocalFrame oFrame,
                float fLength = 20,
                float fInnerRadius = 10,
                float fOuterRadius = 20) : base()
            {
                m_aFrames = new Frames(fLength, oFrame);
                SetPolarSteps(360);
                SetRadialSteps(5);
                SetLengthSteps(5);

                m_oInnerRadiusModulation = new SurfaceModulation(fInnerRadius);
                m_oOuterRadiusModulation = new SurfaceModulation(fOuterRadius);
            }

            /// <summary>
            /// Initialises a pipe based on a spine (frames) and 1 dimension.
            /// For the radial dimension, an inner and an outer radius can be specified.
            /// The spine replaces the length dimension.
            /// </summary>
            public BasePipe(
                Frames aFrames,
                float fInnerRadius = 10,
                float fOuterRadius = 20) : base()
            {
                m_aFrames = aFrames;
                SetPolarSteps(360);
                SetRadialSteps(5);
                SetLengthSteps(500);

                m_oInnerRadiusModulation = new SurfaceModulation(fInnerRadius);
                m_oOuterRadiusModulation = new SurfaceModulation(fOuterRadius);
            }


            //settings
            public void SetRadius(SurfaceModulation oInnerRadiusOverCylinder, SurfaceModulation oOuterRadiusOverCylinder)
            {
                m_oInnerRadiusModulation = oInnerRadiusOverCylinder;
                m_oOuterRadiusModulation = oOuterRadiusOverCylinder;
                SetLengthSteps(500);
            }

            public void SetRadialSteps(uint nRadialSteps)
            {
                m_nRadialSteps = Math.Max(5, nRadialSteps);
            }

            public void SetPolarSteps(uint nPolarSteps)
            {
                m_nPolarSteps = Math.Max(5, nPolarSteps);
            }

            public void SetLengthSteps(uint nLengthSteps)
            {
                m_nLengthSteps = Math.Max(5, nLengthSteps);
            }


            //construction
            public override Voxels voxConstruct()
            {
                Mesh oMesh      = mshConstruct();
                Voxels oVoxels  = new Voxels(oMesh);
                return oVoxels;
            }

            public virtual Mesh mshConstruct()
            {
                Mesh oMesh = new Mesh();
                AddTopSurface(ref oMesh);
                AddBottomSurface(ref oMesh, true);
                AddInnerMantle(ref oMesh);
                AddOuterMantle(ref oMesh, true);
                return oMesh;
            }


            //sides
            protected void AddTopSurface(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across phi and radius
                int iLengthStep     = (int)m_nLengthSteps - 1;
                float fLengthRatio  = fGetLengthRatioFromStep(iLengthStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhiRatio1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhiRatio2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iRadiusStep = 1; iRadiusStep < m_nRadialSteps; iRadiusStep++)
                    {
                        float fRadiusRatio1 = fGetRadiusRatioFromStep(iRadiusStep - 1);
                        float fRadiusRatio2 = fGetRadiusRatioFromStep(iRadiusStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio, fPhiRatio1, fRadiusRatio1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio, fPhiRatio1, fRadiusRatio2);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio, fPhiRatio2, fRadiusRatio2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio, fPhiRatio2, fRadiusRatio1);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            protected void AddBottomSurface(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across phi and radius
                int iLengthStep     = 0;
                float fLengthRatio  = fGetLengthRatioFromStep(iLengthStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhiRatio1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhiRatio2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iRadiusStep = 1; iRadiusStep < m_nRadialSteps; iRadiusStep++)
                    {
                        float fRadiusRatio1 = fGetRadiusRatioFromStep(iRadiusStep - 1);
                        float fRadiusRatio2 = fGetRadiusRatioFromStep(iRadiusStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio, fPhiRatio1, fRadiusRatio1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio, fPhiRatio1, fRadiusRatio2);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio, fPhiRatio2, fRadiusRatio2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio, fPhiRatio2, fRadiusRatio1);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            protected void AddOuterMantle(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across phi and length
                int iRadiusStep     = (int)m_nRadialSteps - 1;
                float fRadiusRatio  = fGetRadiusRatioFromStep(iRadiusStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhiRatio1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhiRatio2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iLengthStep = 1; iLengthStep < m_nLengthSteps; iLengthStep++)
                    {
                        float fLengthRatio1 = fGetLengthRatioFromStep(iLengthStep - 1);
                        float fLengthRatio2 = fGetLengthRatioFromStep(iLengthStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio1, fPhiRatio1, fRadiusRatio);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio2, fPhiRatio1, fRadiusRatio);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio2, fPhiRatio2, fRadiusRatio);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio1, fPhiRatio2, fRadiusRatio);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            protected void AddInnerMantle(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across phi and length
                int iRadiusStep     = 0;
                float fRadiusRatio  = fGetRadiusRatioFromStep(iRadiusStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhiRatio1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhiRatio2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iLengthStep = 1; iLengthStep < m_nLengthSteps; iLengthStep++)
                    {
                        float fLengthRatio1 = fGetLengthRatioFromStep(iLengthStep - 1);
                        float fLengthRatio2 = fGetLengthRatioFromStep(iLengthStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio1, fPhiRatio1, fRadiusRatio);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio2, fPhiRatio1, fRadiusRatio);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio2, fPhiRatio2, fRadiusRatio);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio1, fPhiRatio2, fRadiusRatio);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }


            //step conversions
            protected float fGetRadiusRatioFromStep(int iRadiusStep)
            {
                float fRadiusRatio = (1f) / (m_nRadialSteps - 1f) * (iRadiusStep);
                return fRadiusRatio;
            }

            protected float fGetPhiRatioFromStep(int iPhiStep)
            {
                float fPhiRatio = (1f) / (m_nPolarSteps - 1f) * (iPhiStep);
                return fPhiRatio;
            }

            protected float fGetLengthRatioFromStep(int iLengthStep)
            {
                float fLengthRatio = (1f) / (m_nLengthSteps - 1f) * (iLengthStep);
                return fLengthRatio;
            }

            /// <summary>
            /// Returns a point on the shape surface if one of the ratios is at the limit.
            /// Returns a point inside the shape if all ratios are within the limits.
            /// All ratios go from 0 to 1.
            /// </summary>
            public virtual Vector3 vecGetSurfacePoint(float fLengthRatio, float fPhiRatio, float fRadiusRatio)
            {
                Vector3 vecSpinePos = m_aFrames.vecGetSpineAlongLength(fLengthRatio);
                Vector3 vecLocalX   = m_aFrames.vecGetLocalXAlongLength(fLengthRatio);
                Vector3 vecLocalY   = m_aFrames.vecGetLocalYAlongLength(fLengthRatio);

                float fPhi          = (2f * MathF.PI) * fPhiRatio;

                float fOuterRadius  = fGetOuterRadius(fPhi, fLengthRatio);
                float fInnerRadius  = fGetInnerRadius(fPhi, fLengthRatio);
                float fRadius       = fRadiusRatio * (fOuterRadius - fInnerRadius) + fInnerRadius;

                float fX            = fRadius * MathF.Cos(fPhi);
                float fY            = fRadius * MathF.Sin(fPhi);
                Vector3 vecPt       = vecSpinePos + fX * vecLocalX + fY * vecLocalY;
                return m_fnTrafo(vecPt);
            }

            protected float fGetInnerRadius(float fPhi, float fLengthRatio)
            {
                float fRadius = m_oInnerRadiusModulation.fGetModulation(fPhi, fLengthRatio);
                return fRadius;
            }

            protected float fGetOuterRadius(float fPhi, float fLengthRatio)
            {
                float fRadius = m_oOuterRadiusModulation.fGetModulation(fPhi, fLengthRatio);
                return fRadius;
            }
        }
    }
}
```

### ShapeKernel/BaseShapes/BasePipeSegment.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class BasePipeSegment : BasePipe
        {
            public enum EMethod         { START_END, MID_RANGE };
            protected EMethod           m_eMethod;
            protected LineModulation    m_oRangeModulation;
            protected LineModulation    m_oMidModulation;

            /// <summary>
            /// Initialises a pipe segment based on a local frame and 3 dimensions.
            /// For the radial dimension, an inner and an outer radius can be specified.
            /// The circumferential dimension is defined via two line modulation.
            /// The shape has no spine.
            /// </summary>
            public BasePipeSegment(
                LocalFrame      oFrame,
                float           fLength,
                float           fInnerRadius,
                float           fOuterRadius,
                LineModulation  oStartOrMidModulation,
                LineModulation  oEndOrRangeModulation,
                EMethod         eMethod) : base(oFrame, fLength, fInnerRadius, fOuterRadius)
            {
                m_eMethod = eMethod;
                if (m_eMethod == EMethod.START_END)
                {
                    m_oMidModulation    = 0.5f * (oStartOrMidModulation + oEndOrRangeModulation);
                    m_oRangeModulation  = oEndOrRangeModulation - oStartOrMidModulation;
                }
                else
                {
                    m_oMidModulation    = oStartOrMidModulation;
                    m_oRangeModulation  = oEndOrRangeModulation;
                }
            }

            /// <summary>
            /// Initialises a pipe segment based on a spine (frames) and 2 dimension.
            /// For the radial dimension, an inner and an outer radius can be specified.
            /// The circumferential dimension is defined via two line modulation.
            /// The spine replaces the length dimension.
            /// </summary>
            public BasePipeSegment(
                Frames          aFrames,
                float           fInnerRadius,
                float           fOuterRadius,
                LineModulation  oStartOrMidModulation,
                LineModulation  oEndOrRangeModulation,
                EMethod         eMethod) : base(aFrames, fInnerRadius, fOuterRadius)
            {
                m_eMethod = eMethod;
                if (m_eMethod == EMethod.START_END)
                {
                    m_oMidModulation    = 0.5f * (oStartOrMidModulation + oEndOrRangeModulation);
                    m_oRangeModulation  = oEndOrRangeModulation - oStartOrMidModulation;
                }
                else
                {
                    m_oMidModulation    = oStartOrMidModulation;
                    m_oRangeModulation  = oEndOrRangeModulation;
                }
            }


            //construction
            public override Mesh mshConstruct()
            {
                Mesh oMesh = new Mesh();
                AddTopSurface(ref oMesh);
                AddBottomSurface(ref oMesh, true);
                AddInnerMantle(ref oMesh);
                AddOuterMantle(ref oMesh, true);
                AddStartSurface(ref oMesh);
                AddEndSurface(ref oMesh, true);
                return oMesh;
            }


            //sides
            protected void AddStartSurface(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across length and radius
                int iPhiStep    = 0;
                float fPhiRatio = fGetPhiRatioFromStep(iPhiStep);

                for (int iLengthStep = 1; iLengthStep < m_nLengthSteps; iLengthStep++)
                {
                    float fLengthRatio1 = fGetLengthRatioFromStep(iLengthStep - 1);
                    float fLengthRatio2 = fGetLengthRatioFromStep(iLengthStep);

                    for (int iRadiusStep = 1; iRadiusStep < m_nRadialSteps; iRadiusStep++)
                    {
                        float fRadiusRatio1 = fGetRadiusRatioFromStep(iRadiusStep - 1);
                        float fRadiusRatio2 = fGetRadiusRatioFromStep(iRadiusStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio1, fPhiRatio, fRadiusRatio1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio1, fPhiRatio, fRadiusRatio2);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio2, fPhiRatio, fRadiusRatio2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio2, fPhiRatio, fRadiusRatio1);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            protected void AddEndSurface(ref Mesh oMesh, bool bFlip = false)
            {
                //iterate across length and radius
                int iPhiStep    = (int)m_nPolarSteps - 1;
                float fPhiRatio = fGetPhiRatioFromStep(iPhiStep);

                for (int iLengthStep = 1; iLengthStep < m_nLengthSteps; iLengthStep++)
                {
                    float fLengthRatio1 = fGetLengthRatioFromStep(iLengthStep - 1);
                    float fLengthRatio2 = fGetLengthRatioFromStep(iLengthStep);

                    for (int iRadiusStep = 1; iRadiusStep < m_nRadialSteps; iRadiusStep++)
                    {
                        float fRadiusRatio1 = fGetRadiusRatioFromStep(iRadiusStep - 1);
                        float fRadiusRatio2 = fGetRadiusRatioFromStep(iRadiusStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio1, fPhiRatio, fRadiusRatio1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio1, fPhiRatio, fRadiusRatio2);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio2, fPhiRatio, fRadiusRatio2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio2, fPhiRatio, fRadiusRatio1);

                        if (bFlip == false)
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                        }
                        else
                        {
                            oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                            oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                        }
                    }
                }
            }

            /// <summary>
            /// Returns a point on the shape surface if one of the ratios is at the limit.
            /// Returns a point inside the shape if all ratios are within the limits.
            /// All ratios go from 0 to 1.
            /// </summary>
            public override Vector3 vecGetSurfacePoint(float fLengthRatio, float fPhiRatio, float fRadiusRatio)
            {
                Vector3 vecSpinePos = m_aFrames.vecGetSpineAlongLength(fLengthRatio);
                Vector3 vecLocalX   = m_aFrames.vecGetLocalXAlongLength(fLengthRatio);
                Vector3 vecLocalY   = m_aFrames.vecGetLocalYAlongLength(fLengthRatio);

                float fPhiRange     = fGetEndPhi(fLengthRatio) - fGetStartPhi(fLengthRatio);
                float fPhi          = m_oMidModulation.fGetModulation(fLengthRatio) + (fPhiRatio - 0.5f) * m_oRangeModulation.fGetModulation(fLengthRatio);

                float fOuterRadius  = fGetOuterRadius(fPhi, fLengthRatio);
                float fInnerRadius  = fGetInnerRadius(fPhi, fLengthRatio);
                float fRadius       = fRadiusRatio * (fOuterRadius - fInnerRadius) + fInnerRadius;

                float fX            = fRadius * MathF.Cos(fPhi);
                float fY            = fRadius * MathF.Sin(fPhi);
                Vector3 vecPt       = vecSpinePos + fX * vecLocalX + fY * vecLocalY;

                return m_fnTrafo(vecPt);
            }

            protected float fGetEndPhi(float fLengthRatio)
            {
                float fMid      = m_oMidModulation.fGetModulation(fLengthRatio);
                float fRange    = m_oRangeModulation.fGetModulation(fLengthRatio);
                float fPhi      = fMid + 0.5f * fRange;
                return fPhi;
            }

            protected float fGetStartPhi(float fLengthRatio)
            {
                float fMid      = m_oMidModulation.fGetModulation(fLengthRatio);
                float fRange    = m_oRangeModulation.fGetModulation(fLengthRatio);
                float fPhi      = fMid - 0.5f * fRange;
                return fPhi;
            }
        }
    }
}
```

### ShapeKernel/BaseShapes/BaseRevolve.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class BaseRevolve : BaseShape
        {
            protected uint           m_nLengthSteps;
            protected uint           m_nPolarSteps;
            protected uint           m_nRadialSteps;
            protected Frames         m_aFrames;
            protected LocalFrame     m_oFrame;
            protected LineModulation m_oOuterRadiusModulation;
            protected LineModulation m_oInnerRadiusModulation;


            /// <summary>
            /// Base shape that has always a spine.
            /// Inward and Outward radius are counted positive from the spine away.
            /// Can only rotate around the Z-axis.
            /// </summary>
            public BaseRevolve(
                LocalFrame  oFrame,
                Frames      aFrames,
                float       fInwardRadius   = 3,
                float       fOutwardRadius  = 3)
            {
                m_oFrame                 = oFrame;
                SetRadialSteps(100);
                SetPolarSteps(360);
                SetLengthSteps(500);
                m_oOuterRadiusModulation = new LineModulation(fOutwardRadius);
                m_oInnerRadiusModulation = new LineModulation(fInwardRadius);
                m_aFrames                = aFrames;
            }

            public void SetRadius(LineModulation oInnerRadiusOverCylinder, LineModulation oOuterRadiusOverCylinder)
            {
                m_oInnerRadiusModulation = oInnerRadiusOverCylinder;
                m_oOuterRadiusModulation = oOuterRadiusOverCylinder;
            }

            public void SetRadialSteps(uint nRadialSteps)
            {
                m_nRadialSteps = Math.Max(5, nRadialSteps);
            }

            public void SetPolarSteps(uint nPolarSteps)
            {
                m_nPolarSteps = Math.Max(5, nPolarSteps);
            }

            public void SetLengthSteps(uint nLengthSteps)
            {
                m_nLengthSteps = Math.Max(5, nLengthSteps);
            }

            protected float fGetInnerRadius(float fLengthRatio)
            {
                float fRadius = m_oInnerRadiusModulation.fGetModulation(fLengthRatio);
                return fRadius;
            }

            protected float fGetOuterRadius(float fLengthRatio)
            {
                float fRadius = m_oOuterRadiusModulation.fGetModulation(fLengthRatio);
                return fRadius;
            }

            //construction
            public override Voxels voxConstruct()
            {
                Mesh oMesh = mshConstruct();
                return new Voxels(oMesh);
            }

            public Mesh mshConstruct()
            {
                Mesh oMesh = new Mesh();
                AddTopSurface(ref oMesh);
                AddInnerMantle(ref oMesh);
                AddOuterMantle(ref oMesh);
                AddBottomSurface(ref oMesh);
                return oMesh;
            }

            protected void AddTopSurface(ref Mesh oMesh)
            {
                //iterate across phi and radius
                int iLengthStep = (int)m_nLengthSteps - 1;
                float fLengthRatio = fGetLengthRatioFromStep(iLengthStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhi1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhi2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iRadiusStep = 1; iRadiusStep < m_nRadialSteps; iRadiusStep++)
                    {
                        float fRadiusRatio1 = fGetRadiusRatioFromStep(iRadiusStep - 1);
                        float fRadiusRatio2 = fGetRadiusRatioFromStep(iRadiusStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio, fPhi1, fRadiusRatio1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio, fPhi1, fRadiusRatio2);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio, fPhi2, fRadiusRatio2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio, fPhi2, fRadiusRatio1);
                        oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                        oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                    }
                }
            }

            protected void AddBottomSurface(ref Mesh oMesh)
            {
                //iterate across phi and radius
                int iLengthStep = 0;
                float fLengthRatio = fGetLengthRatioFromStep(iLengthStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhi1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhi2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iRadiusStep = 1; iRadiusStep < m_nRadialSteps; iRadiusStep++)
                    {
                        float fRadiusRatio1 = fGetRadiusRatioFromStep(iRadiusStep - 1);
                        float fRadiusRatio2 = fGetRadiusRatioFromStep(iRadiusStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio, fPhi1, fRadiusRatio1);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio, fPhi1, fRadiusRatio2);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio, fPhi2, fRadiusRatio2);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio, fPhi2, fRadiusRatio1);
                        oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                        oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                    }
                }
            }

            protected void AddOuterMantle(ref Mesh oMesh)
            {
                //iterate across phi and length
                int iRadiusStep = (int)m_nRadialSteps - 1;
                float fRadiusRatio = fGetRadiusRatioFromStep(iRadiusStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhi1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhi2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iLengthStep = 1; iLengthStep < m_nLengthSteps; iLengthStep++)
                    {
                        float fLengthRatio1 = fGetLengthRatioFromStep(iLengthStep - 1);
                        float fLengthRatio2 = fGetLengthRatioFromStep(iLengthStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio1, fPhi1, fRadiusRatio);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio2, fPhi1, fRadiusRatio);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio2, fPhi2, fRadiusRatio);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio1, fPhi2, fRadiusRatio);
                        oMesh.nAddTriangle(vecPt0, vecPt2, vecPt1);
                        oMesh.nAddTriangle(vecPt0, vecPt3, vecPt2);
                    }
                }
            }

            protected void AddInnerMantle(ref Mesh oMesh)
            {
                //iterate across phi and length
                int iRadiusStep = 0;
                float fRadiusRatio = fGetRadiusRatioFromStep(iRadiusStep);

                for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                {
                    float fPhi1 = fGetPhiRatioFromStep(iPhiStep - 1);
                    float fPhi2 = fGetPhiRatioFromStep(iPhiStep);

                    for (int iLengthStep = 1; iLengthStep < m_nLengthSteps; iLengthStep++)
                    {
                        float fLengthRatio1 = fGetLengthRatioFromStep(iLengthStep - 1);
                        float fLengthRatio2 = fGetLengthRatioFromStep(iLengthStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fLengthRatio1, fPhi1, fRadiusRatio);
                        Vector3 vecPt1 = vecGetSurfacePoint(fLengthRatio2, fPhi1, fRadiusRatio);
                        Vector3 vecPt2 = vecGetSurfacePoint(fLengthRatio2, fPhi2, fRadiusRatio);
                        Vector3 vecPt3 = vecGetSurfacePoint(fLengthRatio1, fPhi2, fRadiusRatio);
                        oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                        oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                    }
                }
            }


            //step conversions
            protected float fGetRadiusRatioFromStep(int iRadiusStep)
            {
                float fRadiusRatio = (1f) / (m_nRadialSteps - 1) * (iRadiusStep);
                return fRadiusRatio;
            }

            protected float fGetPhiRatioFromStep(int iPhiStep)
            {
                float fPhiRatio = (1f) / (m_nPolarSteps - 1) * (iPhiStep);
                return fPhiRatio;
            }

            protected float fGetLengthRatioFromStep(int iLengthStep)
            {
                float fLengthRatio = (1f) / (m_nLengthSteps - 1) * (iLengthStep);
                return fLengthRatio;
            }


            public Vector3 vecGetSurfacePoint(float fLengthRatio, float fPhiRatio, float fRadiusRatio)
            {
                Vector3 vecSpinePos     = vecGetSpineAlongLength(fLengthRatio);
                Vector3 vecLocalX       = vecGetLocalXAlongLength(fLengthRatio);
                Vector3 vecLocalY       = vecGetLocalYAlongLength(fLengthRatio);

                float fPhi              = (2f * MathF.PI) * fPhiRatio;

                float fOutwardRadius    = fGetOuterRadius(fLengthRatio);
                float fInwardRadius     = -fGetInnerRadius(fLengthRatio);
                float fRadius           = fRadiusRatio * (fOutwardRadius - fInwardRadius) + fInwardRadius;

                Vector3 vecPt           = vecSpinePos + fRadius * vecLocalX;
                vecPt                   = VecOperations.vecRotateAroundAxis(vecPt, fPhi, m_oFrame.vecGetLocalZ(), m_oFrame.vecGetPosition());

                return m_fnTrafo(vecPt);
            }

            public Vector3 vecGetSpineAlongLength(float fLengthRatio)
            {
                Vector3 vecVector = m_aFrames.vecGetSpineAlongLength(fLengthRatio);
                return vecVector;
            }

            protected Vector3 vecGetLocalXAlongLength(float fLengthRatio)
            {
                Vector3 vecVector = m_aFrames.vecGetLocalXAlongLength(fLengthRatio);
                return vecVector;
            }

            protected Vector3 vecGetLocalYAlongLength(float fLengthRatio)
            {
                Vector3 vecVector = m_aFrames.vecGetLocalYAlongLength(fLengthRatio);
                return vecVector;
            }

            //access
            public Vector3 vecGetOuterSurfacePoint(float fPhi, float fLengthRatio)
            {
                return vecGetSurfacePoint(fLengthRatio, fPhi / (2f * MathF.PI), 1f);
            }

            public Vector3 vecGetInnerSurfacePoint(float fPhi, float fLengthRatio)
            {
                return vecGetSurfacePoint(fLengthRatio, fPhi / (2f * MathF.PI), 0f);
            }

            public static Frames aGetFramesFromContour(GenericContour oContour, LocalFrame? oFrame = null)
            {
                if (oFrame == null)
                {
                    oFrame = new LocalFrame();
                }

                uint nSamples           = 500;
                List<Vector3> aPoints   = new List<Vector3>();
                for (int i = 0; i < nSamples; i++)
                {
                    float fLR       = 1f / (nSamples - 1f) * i;
                    float fZ        = fLR * oContour.m_fTotalLength;
                    float fRadius   = oContour.m_oModulation.fGetModulation(fLR);
                    Vector3 vecRel  = new Vector3(fRadius, 0, fZ);
                    Vector3 vecPt   = VecOperations.vecTranslatePointOntoFrame(oFrame, vecRel);
                    aPoints.Add(vecPt);
                }
                Frames aFrames = new Frames(aPoints, Frames.EFrameType.CYLINDRICAL, 0.5f);
                return aFrames;
            }
        }
    }
}
```

### ShapeKernel/BaseShapes/BaseRing.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;
using PicoGK.Numerics;

namespace Leap71
{
    namespace ShapeKernel
    {
        public class BaseRing : BaseShape, IMeshBaseShape, ISurfaceBaseShape
        {
            protected uint              m_nPolarSteps;
            protected uint              m_nRadialSteps;
            protected float             m_fRingRadius;
            protected SurfaceModulation m_oRadiusModulation;
            protected LocalFrame        m_oFrame;

            /// <summary>
            /// Initialises a torus-ring based on a local frame and 2 dimensions.
            /// The shape has no spine.
            /// </summary>
            public BaseRing(LocalFrame oFrame, float fRingRadius = 50, float fRadius = 5) : base()
            {
                SetRadialSteps(360);
                SetPolarSteps(360);

                m_oFrame            = oFrame;
                m_fRingRadius       = fRingRadius;
                m_oRadiusModulation = new SurfaceModulation(fRadius);
            }

            //settings
            public void SetRadius(SurfaceModulation oModulation)
            {
                m_oRadiusModulation = oModulation;
            }

            public void SetRadialSteps(uint nRadialSteps)
            {
                m_nRadialSteps = Math.Max(5, nRadialSteps);
            }

            public void SetPolarSteps(uint nPolarSteps)
            {
                m_nPolarSteps = Math.Max(5, nPolarSteps);
            }


            //construction
            public override Voxels voxConstruct()
            {
                Mesh oMesh      = mshConstruct();
                Voxels oVoxels  = new Voxels(oMesh);
                return oVoxels;
            }

            public Mesh mshConstruct()
            {
                Mesh oMesh          = new Mesh();
                float fRadiusRatio  = 1f;
                for (int iAlphaStep = 0; iAlphaStep < m_nRadialSteps; iAlphaStep++)
                {
                    int iLowerIndex = iAlphaStep - 1;
                    if (iLowerIndex < 0)
                    {
                        iLowerIndex += (int)m_nRadialSteps;
                    }
                    float fAlphaRatio1 = fGetAlphaRatioFromStep(iLowerIndex);   
                    float fAlphaRatio2 = fGetAlphaRatioFromStep(iAlphaStep);

                    for (int iPhiStep = 1; iPhiStep < m_nPolarSteps; iPhiStep++)
                    {
                        float fPhiRatio1 = fGetPhiRatioFromStep(iPhiStep - 1);
                        float fPhiRatio2 = fGetPhiRatioFromStep(iPhiStep);

                        Vector3 vec0 = vecGetSurfacePoint(fAlphaRatio1, fPhiRatio1, fRadiusRatio);
                        Vector3 vec1 = vecGetSurfacePoint(fAlphaRatio2, fPhiRatio1, fRadiusRatio);
                        Vector3 vec2 = vecGetSurfacePoint(fAlphaRatio2, fPhiRatio2, fRadiusRatio);
                        Vector3 vec3 = vecGetSurfacePoint(fAlphaRatio1, fPhiRatio2, fRadiusRatio);

                        oMesh.nAddTriangle(vec0, vec1, vec2);
                        oMesh.nAddTriangle(vec0, vec2, vec3);
                    }
                }
                return oMesh;
            }


            //step conversions
            protected float fGetAlphaRatioFromStep(int iAlphaStep)
            {
                float fAlpha = (1f) / (m_nRadialSteps - 1) * (iAlphaStep);
                return fAlpha;
            }

            protected float fGetPhiRatioFromStep(int iPhiStep)
            {
                float fPhi = (1f) / (m_nPolarSteps - 1) * (iPhiStep);
                return fPhi;
            }

            /// <summary>
            /// Returns a point on the shape surface if radius ratio = 1.
            /// Returns a point inside the shape if all ratios are within the limits.
            /// All ratios go from 0 to 1.
            /// </summary>
            public Vector3 vecGetSurfacePoint(float fAlphaRatio, float fPhiRatio, float fRadiusRatio)
            {
                float fAlpha    = 2f * MathF.PI * fAlphaRatio;
                float fPhi      = 2f * MathF.PI * fPhiRatio;

                float fX        = m_fRingRadius * MathF.Cos(fAlpha);
                float fY        = m_fRingRadius * MathF.Sin(fAlpha);

                Vector3 vecSpine    =
                    m_oFrame.vecGetPosition() +
                    fX * m_oFrame.vecGetLocalX() +
                    fY * m_oFrame.vecGetLocalY();

                Vector3 vecCentre   = m_oFrame.vecGetPosition();

                Vector3 vecLocalX   = (vecSpine - vecCentre);
                vecLocalX           = vecLocalX.vecSafeNormalized();
                Vector3 vecLocalY   = m_oFrame.vecGetLocalZ();
                Vector3 vecLocalZ   = Vector3.Cross(vecLocalY, vecLocalX);

                float fRadius       = fRadiusRatio * fGetRadius(fPhi, fAlpha);

                float fLocalX       = fRadius * MathF.Cos(fPhi);
                float fLocalY       = fRadius * MathF.Sin(fPhi);
                Vector3 vecPt       = vecSpine + fLocalX * vecLocalX + fLocalY * vecLocalY;

                return m_fnTrafo(vecPt);
            }

            protected float fGetRadius(float fPhi, float fLengthRatio)
            {
                float fRadius = m_oRadiusModulation.fGetModulation(fPhi, fLengthRatio);
                return fRadius;
            }
        }
    }
}
```

### ShapeKernel/BaseShapes/BaseShape.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public interface ISurfaceBaseShape
        {
            public Vector3 vecGetSurfacePoint(float fRatio1, float fRatio2, float fRatio3);
        }

        public interface ISpineBaseShape
        {
            public Vector3 vecGetSpinePoint(float fRatio1);
        }

        public interface IMeshBaseShape
        {
            public Mesh mshConstruct();
        }

        public interface ILatticeBaseShape
        {
            public Lattice latConstruct();
        }

        public abstract class BaseShape
        {
            public BaseShape() { }

            /// <summary>
            /// Set a transformation to the shape that will be applies point-wise during construction.
            /// </summary>
            public void SetTransformation(fnVertexTransformation fnTrafo)
            {
                m_fnTrafo = fnTrafo;
            }

            public delegate Vector3 fnVertexTransformation(Vector3 vecPt);

            protected fnVertexTransformation m_fnTrafo = vecNoTransform;

            public static Vector3 vecNoTransform(Vector3 vecPt)
            {
                return vecPt;
            }

            //construction
            public abstract Voxels voxConstruct();
        }
    }
}
```

### ShapeKernel/BaseShapes/BaseSphere.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class BaseSphere : BaseShape, IMeshBaseShape, ISurfaceBaseShape
        {
            protected uint              m_nAzimuthalSteps;
            protected uint              m_nPolarSteps;
            protected SurfaceModulation m_oRadiusModulation;
            protected LocalFrame        m_oFrame;

            /// <summary>
            /// Initialises a sphere based on a local frame and 1 dimensions.
            /// The shape has no spine.
            /// </summary>
            public BaseSphere(LocalFrame oFrame, float fRadius = 10) : base()
            {
                //phi is the azimuthal angle
                //theta is the polar angle
                SetAzimuthalSteps(360);
                SetPolarSteps(180);
                m_oFrame            = oFrame;
                m_oRadiusModulation = new SurfaceModulation(fRadius);
            }


            //settings
            public void SetRadius(SurfaceModulation oModulation)
            {
                m_oRadiusModulation = oModulation;
            }

            public void SetAzimuthalSteps(uint nAzimuthalSteps)
            {
                m_nAzimuthalSteps = nAzimuthalSteps;
            }

            public void SetPolarSteps(uint nPolarSteps)
            {
                m_nPolarSteps = nPolarSteps;
            }


            //construction
            public override Voxels voxConstruct()
            {
                Mesh oMesh      = mshConstruct();
                Voxels oVoxels  = new Voxels(oMesh);
                return oVoxels;
            }

            public Mesh mshConstruct()
            {
                Mesh oMesh          = new Mesh();
                float fRadiusRatio  = 1f;
                for (int iThetaStep = 1; iThetaStep < m_nAzimuthalSteps; iThetaStep++)
                {
                    float fThetaRatio1 = (1f) / (m_nAzimuthalSteps - 1) * (iThetaStep - 1);
                    float fThetaRatio2 = (1f) / (m_nAzimuthalSteps - 1) * (iThetaStep);

                    for (int iPhiStep = 0; iPhiStep < m_nPolarSteps; iPhiStep++)
                    {
                        float fPhiRatio1 = (1f) / (m_nPolarSteps - 1) * (iPhiStep - 1);
                        float fPhiRatio2 = (1f) / (m_nPolarSteps - 1) * (iPhiStep);

                        Vector3 vecPt0 = vecGetSurfacePoint(fPhiRatio1, fThetaRatio1, fRadiusRatio);
                        Vector3 vecPt1 = vecGetSurfacePoint(fPhiRatio1, fThetaRatio2, fRadiusRatio);
                        Vector3 vecPt2 = vecGetSurfacePoint(fPhiRatio2, fThetaRatio2, fRadiusRatio);
                        Vector3 vecPt3 = vecGetSurfacePoint(fPhiRatio2, fThetaRatio1, fRadiusRatio);
                        oMesh.nAddTriangle(vecPt0, vecPt1, vecPt2);
                        oMesh.nAddTriangle(vecPt0, vecPt2, vecPt3);
                    }
                }
                return oMesh;
            }

            protected float fGetRadius(float fPhi, float fLengthRatio)
            {
                float fRadius = m_oRadiusModulation.fGetModulation(fPhi, fLengthRatio);
                return fRadius;
            }

            /// <summary>
            /// Returns a point on the shape surface if radius ratio = 1.
            /// Returns a point inside the shape if all ratios are within the limits.
            /// All ratios go from 0 to 1.
            /// </summary>
            public Vector3 vecGetSurfacePoint(float fPhiRatio, float fThetaRatio, float fRadiusRatio)
            {
                float fTheta    = 1f * MathF.PI * fThetaRatio;
                float fPhi      = 2f * MathF.PI * fPhiRatio;

                Vector3 vecPos  = m_oFrame.vecGetPosition();
                float fRadius   = fRadiusRatio * fGetRadius(fPhi, fTheta);
                float fX        = fRadius * MathF.Cos(fPhi) * MathF.Sin(fTheta);
                float fY        = fRadius * MathF.Sin(fPhi) * MathF.Sin(fTheta);
                float fZ        = fRadius * MathF.Cos(fTheta);
                Vector3 vecPt   = vecPos
                    + fX * m_oFrame.vecGetLocalX()
                    + fY * m_oFrame.vecGetLocalY()
                    + fZ * m_oFrame.vecGetLocalZ();

                return m_fnTrafo(vecPt);
            }
        }
    }
}
```

### ShapeKernel/BaseShapes/LatticeManifold.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;
using PicoGK.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class LatticeManifold : LatticePipe
        {
            protected float m_fMaxPrintableRadius;
            protected float m_fLimitAngle;
            protected bool  m_bExtendBothSides;

            /// <summary>
            /// Initialises a manifold pipe from lattices based on a local frame and 2 dimensions.
            /// The overhang angle dictates the tear-drop shape of the pipe's cross-section.
            /// The tear-drop extension can be toggled for both directions (+z and -z).
            /// The shape has no spine.
            /// </summary>
            public LatticeManifold(
                LocalFrame  oFrame,
                float       fLength,
                float       fRadius             = 10f,
                float       fMaxOverhangAngle   = 45f,
                bool        bExtendBothSides    = false,
                float       fMinPrintableRadius = 0.1f
                ) : base(oFrame, fLength, fRadius)
            {
                m_fMaxPrintableRadius   = fMinPrintableRadius;
                m_fLimitAngle           = fMaxOverhangAngle;
                m_bExtendBothSides      = bExtendBothSides;
                SetLengthSteps(100);
            }

            /// <summary>
            /// Initialises a manifold pipe from lattices based on a spine (frames) and 1 dimension.
            /// The spine replaces the length dimension.
            /// The overhang angle dictates the tear-drop shape of the pipe's cross-section.
            /// The tear-drop extension can be toggled for both directions (+z and -z).
            /// </summary>
            public LatticeManifold(
                Frames      aFrames,
                float       fRadius             = 10f,
                float       fMaxOverhangAngle   = 45f,
                bool        bExtendBothSides    = false,
                float       fMinPrintableRadius = 0.1f
                ) : base(aFrames, fRadius)
            {
                m_fMaxPrintableRadius   = fMinPrintableRadius;
                m_fLimitAngle           = fMaxOverhangAngle;
                m_bExtendBothSides      = bExtendBothSides;
                SetLengthSteps(500);
            }

            protected float fGetRadius(float fLengthRatio, Vector3 vecDir)
            {
                float fRadius = fGetRadius(fLengthRatio);
                return fRadius;
            }

            public override Lattice latConstruct()
            {
                Lattice oLattice        = new Lattice();
                for (int iZStep = 0; iZStep < m_nLengthSteps; iZStep++)
                {
                    float fLengthRatio  = 1f / m_nLengthSteps * (iZStep);
                    Vector3 vecPt       = vecGetSpinePoint(fLengthRatio);
                    float fBeam         = fGetRadius(fLengthRatio);

                    //add round pipe point
                    oLattice.AddBeam(vecPt, fBeam, vecPt, fBeam);

                    //add tips
                    AddTip(ref oLattice, vecPt, fBeam, true);
                    if (m_bExtendBothSides == true)
                    {
                        AddTip(ref oLattice, vecPt, fBeam, false);
                    }
                }
                return oLattice;
            }

            protected void AddTip(ref Lattice oLattice, Vector3 vecPt, float fBeam, bool bZPositive = true)
            {
                //teardrop shape calculations:
                //https://de.wikipedia.org/wiki/Kreissegment

                float fHalfAlpha        = 90f - m_fLimitAngle;
                float fR                = fBeam;
                float fH                = fR * (1 - MathF.Cos(fHalfAlpha / 180f * MathF.PI));
                float fS                = 2f * fR * MathF.Sin(fHalfAlpha / 180f * MathF.PI);
                float fTipLength        = MathF.Tan(fHalfAlpha / 180f * MathF.PI) * (0.5f * fS - m_fMaxPrintableRadius);

                if (bZPositive == true)
                {
                    Vector3 vecMidSehne = vecPt + (fR - fH) * Vector3.UnitZ;
                    Vector3 vecTip      = vecMidSehne + fTipLength * Vector3.UnitZ;
                    oLattice.AddBeam(vecMidSehne, 0.5f * fS, vecTip, m_fMaxPrintableRadius, false);
                }
                else
                {
                    Vector3 vecMidSehne = vecPt - (fR - fH) * Vector3.UnitZ;
                    Vector3 vecTip      = vecMidSehne - fTipLength * Vector3.UnitZ;
                    oLattice.AddBeam(vecMidSehne, 0.5f * fS, vecTip, m_fMaxPrintableRadius, false);
                }
            }

            protected static float fGetOverhangAngleDegFromVector(Vector3 vecDir)
            {
                vecDir                  = vecDir.vecSafeNormalized();
                float fConnectionAngle  = VecOperations.fGetAngleBetween(vecDir, -Vector3.UnitZ);
                float fDegAngle         = fConnectionAngle / MathF.PI * 180f;
                return fDegAngle;
            }
        }
    }
}
```

### ShapeKernel/BaseShapes/LatticePipe.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class LatticePipe : BaseShape, ILatticeBaseShape, ISpineBaseShape
        {
            protected LineModulation m_oRadiusModulation;
            protected uint           m_nLengthSteps;
            protected Frames         m_aFrames;

            /// <summary>
            /// Initialises a round pipe from lattices based on a local frame and 2 dimensions.
            /// The shape has no spine.
            /// </summary>
            public LatticePipe(LocalFrame oFrame, float fLength, float fRadius = 10f) : base()
            {
                m_aFrames           = new Frames(fLength, oFrame);
                SetLengthSteps(100);

                m_oRadiusModulation = new LineModulation(fRadius);
            }

            /// <summary>
            /// Initialises a round pipe from lattices based on a spine (frames) and 1 dimension.
            /// The spine replaces the length dimension.
            /// </summary>
            public LatticePipe(Frames aFrames, float fRadius = 10f) : base()
            {
                m_aFrames           = aFrames;
                SetLengthSteps(500);

                m_oRadiusModulation = new LineModulation(fRadius);
            }


            //settings
            public void SetRadius(LineModulation oModulation)
            {
                m_oRadiusModulation = oModulation;
            }

            public void SetLengthSteps(uint nLengthSteps)
            {
                m_nLengthSteps = nLengthSteps;
            }


            //construction
            public override Voxels voxConstruct()
            {
                Lattice oLattice = latConstruct();
                Voxels oVoxels   = new Voxels(oLattice);
                return oVoxels;
            }

            public virtual Lattice latConstruct()
            {
                Lattice oLattice = new Lattice();
                for (int iZStep = 1; iZStep < m_nLengthSteps; iZStep++)
                {
                    float fLengthRatio0 = 1f / m_nLengthSteps * (iZStep - 1);
                    float fLengthRatio1 = 1f / m_nLengthSteps * (iZStep);

                    Vector3 vecPt0 = vecGetSpinePoint(fLengthRatio0);
                    Vector3 vecPt1 = vecGetSpinePoint(fLengthRatio1);

                    float fBeam0 = fGetRadius(fLengthRatio0);
                    float fBeam1 = fGetRadius(fLengthRatio1);

                    oLattice.AddBeam(vecPt0, fBeam0, vecPt1, fBeam1);
                }
                return oLattice;
            }

            /// <summary>
            /// Returns the centre axis position along the pipe. 
            /// </summary>
            public Vector3 vecGetSpinePoint(float fLengthRatio)
            {
                return m_fnTrafo(m_aFrames.vecGetSpineAlongLength(fLengthRatio));
            }

            protected float fGetRadius(float fLengthRatio)
            {
                return m_oRadiusModulation.fGetModulation(fLengthRatio);
            }
        }
    }
}
```

### ShapeKernel/Frames/Frames.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class Frames : ISpline
        {
            public enum EFrameType { CYLINDRICAL, SPHERICAL, Z, MIN_ROTATION };

            protected Vector3       m_vecTargetX;
            protected List<Vector3> m_aPoints;
            protected List<Vector3> m_aLocalX;
            protected List<Vector3> m_aLocalY;
            protected List<Vector3> m_aLocalZ;
            protected Vector3?      m_vecLastLocalX;

            protected Frames() { }
            
            /// <summary>
            /// Extrudes a const local frame along a straight line.
            /// </summary>
            public Frames(
                float       fLength,
                LocalFrame  oConstLocalFrame,
                float       fReparametrisationSpacing = 1f)
            {
                Vector3 vecStart    = oConstLocalFrame.vecGetPosition();
                Vector3 vecDir      = oConstLocalFrame.vecGetLocalZ();
                Vector3 vecEnd      = vecStart + fLength * vecDir;

                List<Vector3> aPoints = new List<Vector3>() { vecStart, vecEnd };
                m_aPoints = SplineOperations.aGetReparametrizedSpline(aPoints, fReparametrisationSpacing);

                m_aLocalX = new List<Vector3>();
                m_aLocalY = new List<Vector3>();
                m_aLocalZ = new List<Vector3>();
                for (int i = 0; i < m_aPoints.Count; i++)
                {
                    m_aLocalZ.Add(oConstLocalFrame.vecGetLocalZ());
                    m_aLocalX.Add(oConstLocalFrame.vecGetLocalX());
                    m_aLocalY.Add(oConstLocalFrame.vecGetLocalY());
                }
            }

            /// <summary>
            /// Extrudes a const local frame along a spline.
            /// </summary>
            public Frames(
                List<Vector3>   aPoints,
                LocalFrame      oConstLocalFrame,
                float           fReparametrisationSpacing = 1f)
            {
                m_aPoints = SplineOperations.aGetReparametrizedSpline(aPoints, fReparametrisationSpacing);

                m_aLocalX = new List<Vector3>();
                m_aLocalY = new List<Vector3>();
                m_aLocalZ = new List<Vector3>();
                for (int i = 0; i < m_aPoints.Count; i++)
                {
                    m_aLocalZ.Add(oConstLocalFrame.vecGetLocalZ());
                    m_aLocalX.Add(oConstLocalFrame.vecGetLocalX());
                    m_aLocalY.Add(oConstLocalFrame.vecGetLocalY());
                }
            }

            /// <summary>
            /// Aligns local frames along a spline for localZ and a const target direction for localX.
            /// </summary>
            public Frames(
                List<Vector3>   aPoints,
                Vector3         vecTargetX,
                float           fReparametrisationSpacing = 1f)
            {
                vecTargetX = vecTargetX.Normalize();

                m_aPoints = SplineOperations.aGetReparametrizedSpline(aPoints, fReparametrisationSpacing);
                m_aLocalZ = aGetTangentDirections();

                m_aLocalX = new List<Vector3>();
                for (int i = 0; i < m_aPoints.Count; i += 1)
                {
                    Vector3 vecPt = m_aPoints[i];
                    Vector3 vecLocalZ = m_aLocalZ[i];
                    Vector3 vecLocalX = vecAlignWithTargetX(vecLocalZ, vecTargetX);
                    m_aLocalX.Add(vecLocalX);
                }

                //fill in localY using convention
                m_aLocalY = new List<Vector3>();
                for (int i = 0; i < m_aPoints.Count; i++)
                {
                    Vector3 vecLocalY = LocalFrame.vecGetLocalY(m_aLocalZ[i], m_aLocalX[i]);
                    m_aLocalY.Add(vecLocalY);
                }

                //post processing
                uint nSamples = (uint)m_aPoints.Count;
                m_aPoints = SplineOperations.aGetNURBSpline(m_aPoints, nSamples);
                m_aLocalX = SplineOperations.aGetNURBSpline(m_aLocalX, nSamples);
                m_aLocalY = SplineOperations.aGetNURBSpline(m_aLocalY, nSamples);
                m_aLocalZ = SplineOperations.aGetNURBSpline(m_aLocalZ, nSamples);
            }

            /// <summary>
            /// Aligns local frames along a spline for localZ and a const target direction for localX,
            /// and optionally removes 180-degree frame flips.
            /// </summary>
            public Frames(
                List<Vector3>   aPoints,
                Vector3         vecTargetX,
                bool            bEnsureFrameContinuity,
                float           fReparametrisationSpacing = 1f)
                : this(aPoints, vecTargetX, fReparametrisationSpacing)
            {
                if (bEnsureFrameContinuity)
                {
                    EnsureFrameContinuity();
                }
            }

            /// <summary>
            /// Aligns local frames along a spline for localZ and a coord-system-dependant target direction for localX.
            /// </summary>
            public Frames(
                List<Vector3>   aPoints,
                EFrameType      eFrameType,
                float           fReparametrisationSpacing = 1f)
            {
                m_aPoints = SplineOperations.aGetReparametrizedSpline(aPoints, fReparametrisationSpacing);
                m_aLocalZ = aGetTangentDirections();

                m_aLocalX = new List<Vector3>();
                for (int i = 0; i < m_aPoints.Count; i += 1)
                {
                    Vector3 vecPt       = m_aPoints[i];
                    Vector3 vecLocalZ   = m_aLocalZ[i];
                    Vector3 vecLocalX   = vecAlignWithFramesType(vecPt, vecLocalZ, eFrameType);
                    m_aLocalX.Add(vecLocalX);
                }

                //fill in localY using convention
                m_aLocalY = new List<Vector3>();
                for (int i = 0; i < m_aPoints.Count; i++)
                {
                    Vector3 vecLocalY   = LocalFrame.vecGetLocalY(m_aLocalZ[i], m_aLocalX[i]);
                    m_aLocalY.Add(vecLocalY);
                }
            }

            /// <summary>
            /// Aligns local frames along a spline and optionally removes 180-degree frame flips.
            /// Existing constructors retain their original behaviour.
            /// </summary>
            public Frames(
                List<Vector3>   aPoints,
                EFrameType      eFrameType,
                bool            bEnsureFrameContinuity,
                float           fReparametrisationSpacing = 1f)
                : this(aPoints, eFrameType, fReparametrisationSpacing)
            {
                if (bEnsureFrameContinuity)
                {
                    EnsureFrameContinuity();
                }
            }

            public void ApplyToFrame(LocalFrame oFrame)
            {
                for (int i = 0; i < m_aPoints.Count; i += 1)
                {
                    m_aPoints[i]        = m_aPoints[i].vecPtWorld(oFrame);
                    m_aLocalX[i]        = m_aLocalX[i].vecDirWorld(oFrame);
                    m_aLocalY[i]        = m_aLocalY[i].vecDirWorld(oFrame);
                    m_aLocalZ[i]        = m_aLocalZ[i].vecDirWorld(oFrame);
                }
            }

            //utility
            /// <summary>
            /// Densifies the frame field and removes equivalent 180-degree local-X flips.
            /// </summary>
            protected void EnsureFrameContinuity()
            {
                const uint nSamples = 500;

                List<Vector3> aPoints = new List<Vector3>();
                List<Vector3> aLocalX = new List<Vector3>();
                List<Vector3> aLocalZ = new List<Vector3>();

                for (int i = 0; i < nSamples; i += 1)
                {
                    float fLR = i / (nSamples - 1f);
                    LocalFrame oFrame = oGetLocalFrame(fLR);

                    Vector3 vecLocalX = oFrame.vecGetLocalX();
                    if (aLocalX.Count > 0 && Vector3.Dot(aLocalX[^1], vecLocalX) < 0f)
                    {
                        vecLocalX = -vecLocalX;
                    }

                    aPoints.Add(oFrame.vecGetPosition());
                    aLocalX.Add(vecLocalX);
                    aLocalZ.Add(oFrame.vecGetLocalZ());
                }

                m_aPoints = aPoints;
                m_aLocalX = aLocalX;
                m_aLocalZ = aLocalZ;
                m_aLocalY = new List<Vector3>();

                for (int i = 0; i < m_aPoints.Count; i += 1)
                {
                    Vector3 vecLocalY = LocalFrame.vecGetLocalY(m_aLocalZ[i], m_aLocalX[i]);
                    m_aLocalY.Add(vecLocalY);
                }
            }

            protected Vector3 vecAlignWithFramesType(Vector3 vecPt, Vector3 vecLocalZ, EFrameType eFrameType)
            {
                if (eFrameType == EFrameType.MIN_ROTATION)
                {
                    /////////////////////////////////
                    //minimize rotation
                    if (m_vecLastLocalX == null)
                    {
                        Vector3 vecTargetX      = vecGetTargetX(vecPt, EFrameType.Z);
                        Vector3 vecDummyLocalX  = vecAlignWithTargetX(vecLocalZ, vecTargetX);
                        m_vecLastLocalX         = vecDummyLocalX;
                    }
                    Vector3 vecLocalX   = vecAlignWithTargetX(vecLocalZ, (Vector3)m_vecLastLocalX);
                    m_vecLastLocalX     = vecLocalX;
                    return vecLocalX;
                    /////////////////////////////////
                }
                else
                {
                    Vector3 vecTargetX  = vecGetTargetX(vecPt, eFrameType);
                    Vector3 vecLocalX   = vecAlignWithTargetX(vecLocalZ, vecTargetX);
                    return vecLocalX;
                }
            }

            public static Vector3 vecAlignWithTargetX(Vector3 vecLocalZ, Vector3 vecTargetX)
            {
                Vector3 vecInitLocalX   = VecOperations.vecGetOrthogonalDir(vecLocalZ);
                Vector3 vecInitLocalY   = Vector3.Cross(vecInitLocalX, vecLocalZ);
                float fMaxDotProduct    = MathF.Abs(Vector3.Dot(vecInitLocalX, vecTargetX));
                Vector3 vecFinalLocalX  = vecInitLocalX;

                for (float dAngle = 0; dAngle < 180f; dAngle += 0.01f)
                {
                    float fPhi              = (2 * MathF.PI) / 360f * dAngle;
                    Vector3 vecNewLocalX    = MathF.Cos(fPhi) * vecInitLocalX + MathF.Sin(fPhi) * vecInitLocalY;
                    float fDotProduct       = MathF.Abs(Vector3.Dot(vecNewLocalX, vecTargetX));
                    if (fDotProduct > fMaxDotProduct)
                    {
                        vecFinalLocalX      = vecNewLocalX;
                        fMaxDotProduct      = fDotProduct;
                    }
                }
                vecFinalLocalX          = VecOperations.vecFlipForAlignment(vecFinalLocalX, vecTargetX);
                vecFinalLocalX          = vecFinalLocalX.Normalize();
                return vecFinalLocalX;
            }

            public static Vector3 vecGetTargetX(Vector3 vecPt, EFrameType eFrameType)
            {
                if (eFrameType == EFrameType.CYLINDRICAL)
                {
                    Vector3 vecRadial   = new Vector3(vecPt.X, vecPt.Y, 0);
                    vecRadial           = vecRadial.Normalize();
                    return vecRadial;
                }
                else if (eFrameType == EFrameType.SPHERICAL)
                {
                    Vector3 vecRadial   = new Vector3(vecPt.X, vecPt.Y, vecPt.Z);
                    vecRadial           = vecRadial.Normalize();
                    return vecRadial;
                }
                else
                {
                    return Vector3.UnitZ;
                }
            }

            protected List<Vector3> aGetTangentDirections()
            {
                List<Vector3> aTangents = new List<Vector3>();
                for (int i = 1; i < m_aPoints.Count - 1; i++)
                {
                    Vector3 vecLocalZ   = m_aPoints[i] - m_aPoints[i - 1];
                    vecLocalZ           = vecLocalZ.Normalize();
                    aTangents.Add(vecLocalZ);
                }

                //add continuous start and end
                aTangents.Insert(0, aTangents[0]);
                aTangents.Add(aTangents[^1]);
                return aTangents;
            }


            //access
            public Vector3 vecGetSpineAlongLength(float fLengthRatio)
            {
                fLengthRatio    = float.Clamp(fLengthRatio, 0f, 1f);
                float fStep     = fLengthRatio * (m_aPoints.Count - 1);

                int iLowerStep  = (int)Math.Min(fStep, m_aPoints.Count - 1);
                int iUpperStep  = (int)Math.Min(fStep + 1, m_aPoints.Count - 1);
                float dS        = fStep - iLowerStep;

                Vector3 vecLowerVector = m_aPoints[iLowerStep];
                Vector3 vecUpperVector = m_aPoints[iUpperStep];

                Vector3 vecVector = vecLowerVector + dS * (vecUpperVector - vecLowerVector);
                return vecVector;
            }

            public Vector3 vecGetLocalXAlongLength(float fLengthRatio)
            {
                fLengthRatio    = float.Clamp(fLengthRatio, 0f, 1f);
                float fStep     = fLengthRatio * (m_aPoints.Count - 1);

                int iLowerStep  = (int)Math.Min(fStep, m_aPoints.Count - 1);
                int iUpperStep  = (int)Math.Min(fStep + 1, m_aPoints.Count - 1);
                float dS        = fStep - iLowerStep;

                Vector3 vecLowerVector = m_aLocalX[iLowerStep];
                Vector3 vecUpperVector = m_aLocalX[iUpperStep];

                Vector3 vecVector = vecLowerVector + dS * (vecUpperVector - vecLowerVector);
                return vecVector;
            }

            public Vector3 vecGetLocalYAlongLength(float fLengthRatio)
            {
                fLengthRatio    = float.Clamp(fLengthRatio, 0f, 1f);
                float fStep     = fLengthRatio * (m_aPoints.Count - 1);

                int iLowerStep  = (int)Math.Min(fStep, m_aPoints.Count - 1);
                int iUpperStep  = (int)Math.Min(fStep + 1, m_aPoints.Count - 1);
                float dS        = fStep - iLowerStep;

                Vector3 vecLowerVector = m_aLocalY[iLowerStep];
                Vector3 vecUpperVector = m_aLocalY[iUpperStep];

                Vector3 vecVector = vecLowerVector + dS * (vecUpperVector - vecLowerVector);
                return vecVector;
            }

            public Vector3 vecGetLocalZAlongLength(float fLengthRatio)
            {
                fLengthRatio    = float.Clamp(fLengthRatio, 0f, 1f);
                float fStep     = fLengthRatio * (m_aPoints.Count - 1);

                int iLowerStep  = (int)Math.Min(fStep, m_aPoints.Count - 1);
                int iUpperStep  = (int)Math.Min(fStep + 1, m_aPoints.Count - 1);
                float dS        = fStep - iLowerStep;

                Vector3 vecLowerVector = m_aLocalZ[iLowerStep];
                Vector3 vecUpperVector = m_aLocalZ[iUpperStep];

                Vector3 vecVector = vecLowerVector + dS * (vecUpperVector - vecLowerVector);
                return vecVector;
            }

            public LocalFrame oGetLocalFrame(float fLengthRatio)
            {
                Vector3 vecPos      = vecGetSpineAlongLength(fLengthRatio);
                Vector3 vecLocalX   = vecGetLocalXAlongLength(fLengthRatio);
                Vector3 vecLocalZ   = vecGetLocalZAlongLength(fLengthRatio);
                LocalFrame oFrame   = new LocalFrame(vecPos, vecLocalZ, vecLocalX);
                return oFrame;
            }

            public List<Vector3> aGetPoints()
            {
                return m_aPoints;
            }

            public List<Vector3> aGetPoints(uint nSamples)
            {
                return SplineOperations.aGetReparametrizedSpline(m_aPoints, nSamples);
            }
        }
    }
}
```

### ShapeKernel/Frames/LocalFrame.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK.Shapes;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class LocalFrame
        {
            protected Vector3 m_vecPosition;
            protected Vector3 m_vecLocalX;
            protected Vector3 m_vecLocalY;
            protected Vector3 m_vecLocalZ;

            /// <summary>
            /// Creates a local frame with default values.
            /// The position will be the origin.
            /// Local x = absolute x direction.
            /// Local y = absolute y direction.
            /// Local z = absolute z direction.
            /// </summary>
            public LocalFrame()
            {
                //default values
                m_vecPosition = new Vector3();
                m_vecLocalZ = Vector3.UnitZ;
                m_vecLocalX = Vector3.UnitX;
                m_vecLocalY = vecGetLocalY(m_vecLocalZ, m_vecLocalX);
            }

            /// <summary>
            /// Creates a local frame with the same axes as the specified base frame, but with a new position.
            /// </summary>
            public LocalFrame(LocalFrame oBaseFrame, Vector3 vecNewPos)
            {
                m_vecPosition = vecNewPos;
                m_vecLocalZ = oBaseFrame.vecGetLocalZ();
                m_vecLocalX = oBaseFrame.vecGetLocalX();
                m_vecLocalY = oBaseFrame.vecGetLocalY();
            }

            /// <summary>
            /// Creates a local frame with the specified position and default axes.
            /// Local x = absolute x direction.
            /// Local y = absolute y direction.
            /// Local z = absolute z direction.
            /// </summary>
            public LocalFrame(Vector3 vecPos)
            {
                m_vecPosition = vecPos;
                m_vecLocalZ = Vector3.UnitZ;
                m_vecLocalX = Vector3.UnitX;
                m_vecLocalY = vecGetLocalY(m_vecLocalZ, m_vecLocalX);
            }

            /// <summary>
            /// Creates a local frame with the specified position and local z.
            /// Local x will be chosen as an arbitary orthogonal direction to local z.
            /// Local y will complement local x and local z for a right-hand system.
            /// </summary>
            public LocalFrame(Vector3 vecPos, Vector3 vecLocalZ)
            {
                //normalize inputs
                if (vecLocalZ.LengthSquared() == 0)
                {
                    throw new Exception("Local Z Coordinate has a length of Zero!");
                }
                vecLocalZ /= vecLocalZ.Length();

                m_vecPosition = vecPos;
                m_vecLocalZ = vecLocalZ;
                m_vecLocalX = VecOperations.vecGetOrthogonalDir(m_vecLocalZ);
                m_vecLocalY = vecGetLocalY(m_vecLocalZ, m_vecLocalX);
            }

            /// <summary>
            /// Creates a local frame with the specified position and local z and local x.
            /// Local y will complement local x and local z for a right-hand system.
            /// </summary>
            public LocalFrame(Vector3 vecPos, Vector3 vecLocalZ, Vector3 vecLocalX)
            {
                //normalize inputs
                if (vecLocalZ.LengthSquared() == 0)
                {
                    throw new Exception("Local Z Coordinate has a length of Zero!");
                }
                if (vecLocalX.LengthSquared() == 0)
                {
                    throw new Exception("Local X Coordinate has a length of Zero!");
                }
                vecLocalZ /= vecLocalZ.Length();
                vecLocalX /= vecLocalX.Length();

                m_vecPosition = vecPos;
                m_vecLocalZ = vecLocalZ;
                m_vecLocalX = vecLocalX;
                m_vecLocalY = vecGetLocalY(m_vecLocalZ, m_vecLocalX);
            }


            //access functions
            public Vector3 vecGetPosition()
            {
                return m_vecPosition;
            }

            public Vector3 vecGetLocalX()
            {
                return m_vecLocalX;
            }

            public Vector3 vecGetLocalY()
            {
                return m_vecLocalY;
            }

            public Vector3 vecGetLocalZ()
            {
                return m_vecLocalZ;
            }

            [Obsolete("Avoid since the function rotates and doesn't truly invert")]
            /// <summary>
            /// Returns a local frame that is flipped compared to the specified local frame.
            /// The position remains constant.
            /// The booleans toogle which local axes whould be inverted.
            /// </summary>
            public LocalFrame oInvert(bool bMirrorZ, bool bMirrorX)
            {
                Vector3 vecNewLocalZ = vecGetLocalZ();
                Vector3 vecNewLocalX = vecGetLocalX();
                if (bMirrorZ)
                {
                    vecNewLocalZ = -vecGetLocalZ();
                }
                if (bMirrorX)
                {
                    vecNewLocalX = -vecGetLocalX();
                }

                LocalFrame oNewFrame = new (vecGetPosition(), vecNewLocalZ, vecNewLocalX);
                return oNewFrame;
            }

            /// <summary>
            /// Returns a local frame that is translates in position compared to the specified local frame.
            /// The axes remain constant.
            /// </summary>
            public LocalFrame oTranslate(Vector3 vecTranslate)
            {
                Vector3 vecNewPosition  = vecGetPosition() + vecTranslate;
                LocalFrame oNewFrame    = new (vecNewPosition, vecGetLocalZ(), vecGetLocalX());
                return oNewFrame;
            }

            /// <summary>
            /// Returns a local frame that is rotated compared to the specified local frame.
            /// The position remains constant.
            /// All local axes are rotated around the specified axis by angle phi in rad.
            /// </summary>
            public LocalFrame oRotate(float dPhi, Vector3 vecAxis)
            {
                Vector3 vecNewLocalX = VecOperations.vecRotateAroundAxis(vecGetLocalX(), dPhi, vecAxis);
                Vector3 vecNewLocalZ = VecOperations.vecRotateAroundAxis(vecGetLocalZ(), dPhi, vecAxis);
                LocalFrame oNewFrame = new (vecGetPosition(), vecNewLocalZ, vecNewLocalX);
                return oNewFrame;
            }

            /// <summary>
            /// Returns a local frame that is flipped compared to the specified local frame.
            /// The position remains constant.
            /// The booleans toogle which local axes whould be inverted.
            /// </summary>
            public static LocalFrame oGetInvertFrame(LocalFrame oFrame, bool bMirrorZ, bool bMirrorX)
            {
                Vector3 vecNewLocalZ = oFrame.vecGetLocalZ();
                Vector3 vecNewLocalX = oFrame.vecGetLocalX();
                if (bMirrorZ)
                {
                    vecNewLocalZ = -oFrame.vecGetLocalZ();
                }
                if (bMirrorX)
                {
                    vecNewLocalX = -oFrame.vecGetLocalX();
                }

                LocalFrame oNewFrame = new LocalFrame(oFrame.vecGetPosition(), vecNewLocalZ, vecNewLocalX);
                return oNewFrame;
            }

            /// <summary>
            /// Returns a local frame that is translates in position compared to the specified local frame.
            /// The axes remain constant.
            /// </summary>
            public static LocalFrame oGetTranslatedFrame(LocalFrame oFrame, Vector3 vecTranslate)
            {
                Vector3 vecNewPosition  = oFrame.vecGetPosition() + vecTranslate;
                LocalFrame oNewFrame    = new LocalFrame(vecNewPosition, oFrame.vecGetLocalZ(), oFrame.vecGetLocalX());
                return oNewFrame;
            }

            /// <summary>
            /// Returns a local frame that is rotated compared to the specified local frame.
            /// The position remains constant.
            /// All local axes are rotated around the specified axis by angle phi in rad.
            /// </summary>
            public static LocalFrame oGetRotatedFrame(LocalFrame oFrame, float dPhi, Vector3 vecAxis)
            {
                Vector3 vecNewLocalX = VecOperations.vecRotateAroundAxis(oFrame.vecGetLocalX(), dPhi, vecAxis);
                Vector3 vecNewLocalZ = VecOperations.vecRotateAroundAxis(oFrame.vecGetLocalZ(), dPhi, vecAxis);
                LocalFrame oNewFrame = new LocalFrame(oFrame.vecGetPosition(), vecNewLocalZ, vecNewLocalX);
                return oNewFrame;
            }

            /// <summary>
            /// Compliments local z and local x according to a right-hand system.
            /// </summary>
            public static Vector3 vecGetLocalY(Vector3 vecLocalZ, Vector3 vecLocalX)
            {
                Vector3 vecLocalY = Vector3.Cross(vecLocalZ, vecLocalX);
                return vecLocalY;
            }

            public static implicit operator Frame3d(LocalFrame oFrame)
            {
                return new (    oFrame.vecGetPosition(),
                                oFrame.vecGetLocalZ(),
                                oFrame.vecGetLocalX());
            }

            public static implicit operator LocalFrame(Frame3d frm)
            {
                return new LocalFrame(  frm.vecPos,
                                        frm.vecLz,
                                        frm.vecLx);
            }
        }
    }
}
```

### ShapeKernel/Functions/ShBasicFunctions.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//

using PicoGK;

namespace Leap71
{
    namespace ShapeKernel
    {
        public partial class Sh
        {
            [Obsolete("Use PicoGK.Voxels.voxOffset instead")]
            public static Voxels voxOffset(Voxels vox, float fDistInMM)
                => vox.voxOffset(fDistInMM);
            
            [Obsolete("Use PicoGK.Voxels.voxSmoothen instead")]
            public static Voxels voxSmoothen(Voxels vox, float fSmoothInMM)
                => vox.voxSmoothen(fSmoothInMM);

            [Obsolete("Use PicoGK.Voxels.voxOverOffset instead")]
            public static Voxels voxOverOffset( Voxels vox, 
                                                float fInitialDistInMM, 
                                                float fFinalDistInMM)
                => vox.voxOverOffset(fInitialDistInMM, fFinalDistInMM);

            [Obsolete("Use PicoGK.Voxels.voxProjectZSlice instead")]
            public static Voxels voxExtrudeZSlice(Voxels vox, float fStartHeight, float fEndHeight)
                => vox.voxProjectZSlice(fStartHeight, fEndHeight);

            [Obsolete("Use PicoGK.Voxels.voxBoolAdd instead")]
            public static Voxels voxUnion(Voxels vox1, Voxels vox2)
                => vox1.voxBoolAdd(vox2);

            [Obsolete("Use PicoGK.Voxels.voxBoolSubtract instead")]
            public static Voxels voxSubtract(in Voxels vox1, Voxels vox2)
                => vox1.voxBoolSubtract(vox2);

            [Obsolete("Use PicoGK.Voxels.voxBoolIntersect instead")]
            public static Voxels voxIntersect(Voxels vox1, Voxels vox2)
                => vox1.voxBoolIntersect(vox2);

            [Obsolete("Use PicoGK.Voxels.voxIntersectImplicit instead")]
            public static Voxels voxIntersectImplicit(Voxels vox, IImplicit sdfObject)
                => vox.voxIntersectImplicit(sdfObject);
        }
    }
}
```

### ShapeKernel/Functions/ShCombinedFunctions.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public partial class Sh
        {
            [Obsolete("Use PicoGK.Voxels.voxShell instead")]
            public static Voxels voxShell(  Voxels vox, 
                                            float fNegOffset, 
                                            float fPosOffset, 
                                            float fSmooth = 0f)
                => vox.voxShell(fNegOffset, fPosOffset, fSmooth);

            [Obsolete("Use PicoGK.Voxels.voxCombineAll instead")]
            public static Voxels voxUnion(List<Voxels> aVoxelList)
                => Voxels.voxCombineAll(aVoxelList);
        }
    }
}
```

### ShapeKernel/Functions/ShExportFunctions.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public partial class Sh
        {
            public static void ExportMeshToSTLFile(Mesh oMesh, string strFilePath)
            {
                try
                {
                    oMesh.SaveToStlFile(strFilePath);
                    Library.Log($"STL Export: {strFilePath} exported.");
                }
                catch (Exception e)
                {
                    Library.Log("Could not save STL: " + e.Message);
                }
            }

            public static void ExportVoxelsToSTLFile(Voxels oVoxels, string strFilePath)
            {
                Mesh oMesh = new Mesh(oVoxels);
                ExportMeshToSTLFile(oMesh, strFilePath);
            }

            public static void ExportVoxelsToVDBFile(Voxels oVoxels, string strFilePath)
            {
                try
                {
                    oVoxels.SaveToVdbFile(strFilePath);
                    Library.Log($"VDB Export: {strFilePath} exported.");
                }
                catch (Exception e)
                {
                    Library.Log("Could not save VDB: " + e.Message);
                }
            }

            public static void ExportVoxelsToCLIFile(Voxels oVoxels, string strFilePath)
            {
                try
                {
                    oVoxels.SaveToCliFile(strFilePath);
                    Library.Log($"CLI Export: {strFilePath} exported.");
                }
                catch (Exception e)
                {
                    Library.Log("Could not save CLI: " + e.Message);
                }
            }

            public enum EExport { STL, TGA, PNG, CSV, VDB, CLI };
            public static string strGetExportPath(EExport eExport, string strFilename)
            {
                string strFormatStub    = "." + eExport.ToString();
                string strFullPath      = Path.Combine(Library.strLogFolder, strFilename + strFormatStub);
                return strFullPath;
            }
        }
    }
}
```

### ShapeKernel/Functions/ShLatticeFunctions.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public partial class Sh
        {
            /// <summary>
            /// Creates a lattice from a point list / spline.
            /// </summary>
            public static Lattice latFromLine(List<Vector3> aPoints, float fBeam)
            {
                Lattice oLattice = new Lattice();
                for (int i = 1; i < aPoints.Count; i++)
                {
                    oLattice.AddBeam(aPoints[i - 1], fBeam, aPoints[i], fBeam, true);
                }
                return oLattice;
            }

            /// <summary>
            /// Adds a point list / spline to an existing lattice.
            /// </summary>
            public static void AddLine(ref Lattice oLattice, List<Vector3> aPoints, float fBeam)
            {
                for (int i = 1; i < aPoints.Count; i++)
                {
                    oLattice.AddBeam(aPoints[i - 1], fBeam, aPoints[i], fBeam, true);
                }
            }

            /// <summary>
            /// Creates a node-only lattice from a point cloud.
            /// The points will not be connected.
            /// </summary>
            public static Lattice latFromPoints(List<Vector3> aPoints, float fBeam)
            {
                Lattice oLattice = new Lattice();
                for (int i = 0; i < aPoints.Count; i++)
                {
                    oLattice.AddSphere(aPoints[i], fBeam);
                }
                return oLattice;
            }

            /// <summary>
            /// Creates a lattice from multiple point lists / splines.
            /// </summary>
            public static Lattice latFromEdges(List<List<Vector3>> aEdges, float fBeam)
            {
                Lattice oLattice = new Lattice();
                for (int i = 0; i < aEdges.Count; i++)
                {
                    List<Vector3> aPoints = aEdges[i];
                    for (int j = 1; j < aPoints.Count; j++)
                    {
                        oLattice.AddBeam(aPoints[j - 1], fBeam, aPoints[j], fBeam, true);
                    }
                }
                return oLattice;
            }

            /// <summary>
            /// Creates a node-only lattice from a point.
            /// </summary>
            public static Lattice latFromPoint(Vector3 vecPt, float fBeam)
            {
                Lattice oLattice = new Lattice();
                oLattice.AddSphere(vecPt, fBeam);
                return oLattice;
            }

            /// <summary>
            /// Creates a lattice from a grid.
            /// </summary>
            public static Lattice latFromGrid(List<List<Vector3>> aGrid, float fBeam)
            {
                Lattice oLattice = new Lattice();
                for (int i = 0; i < aGrid.Count; i++)
                {
                    oLattice = latFromLine(aGrid[i], fBeam);
                }
                aGrid = GridOperations.aGetInverseGrid(aGrid);
                for (int i = 0; i < aGrid.Count; i++)
                {
                    List<Vector3> aPoints = aGrid[i];
                    for (int j = 1; j < aPoints.Count; j++)
                    {
                        oLattice.AddBeam(aPoints[j - 1], fBeam, aPoints[j], fBeam, true);
                    }
                }
                return oLattice;
            }

            /// <summary>
            /// Creates a lattice from a beam.
            /// Beam has a constant radius.
            /// Beam has rounded end caps.
            /// </summary>
            public static Lattice latFromBeam(Vector3 vecPt1, Vector3 vecPt2, float fBeam, bool bRounded)
            {
                Lattice oLattice = new Lattice();
                oLattice.AddBeam(vecPt1, fBeam, vecPt2, fBeam, bRounded);
                return oLattice;
            }

            /// <summary>
            /// Creates a lattice from a beam.
            /// Beam has a variable radius.
            /// Beam has rounded end caps.
            /// </summary>
            public static Lattice latFromBeam(Vector3 vecPt1, Vector3 vecPt2, float fBeam1, float fBeam2, bool bRounded)
            {
                Lattice oLattice = new Lattice();
                oLattice.AddBeam(vecPt1, fBeam1, vecPt2, fBeam2, bRounded);
                return oLattice;
            }
        }
    }
}
```

### ShapeKernel/Functions/ShVoxelFunctions.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//

using System.Numerics;
using PicoGK;

namespace Leap71
{
    namespace ShapeKernel
    {
        public partial class Sh
        {
            [Obsolete("Use PicoGK.Voxels.vecClosestPointOnSurface instead")]
            /// <summary>
            /// Returns a point on the voxelfield that is closest to the specified point.
            /// "Snap to surface".
            /// </summary>
            public static Vector3 vecGetClosestSurfacePoint(Voxels vox, Vector3 vecPt)
                => vox.vecClosestPointOnSurface(vecPt);

            [Obsolete("Use PicoGK.Voxels.vecRayCastToSurface instead")]
            /// <summary>
            /// Returns a point on the voxelfield as a result from raycasting from the specified point into the specidied direction.
            /// "Project to surface".
            /// </summary>
            public static Vector3 vecGetProjectedSurfacePoint(Voxels vox, Vector3 vecPt, Vector3 vecDir)
                => vox.vecRayCastToSurface(vecPt, vecDir);

            [Obsolete("Use PicoGK.Voxels.oCalculateBoundingBox instead")]
            /// <summary>
            /// Returns the axis-aligned bounding box of a voxelfield.
            /// </summary>
            public static BBox3 oGetBoundingBox(Voxels vox)
                => vox.oCalculateBoundingBox();
        }
    }
}
```

### ShapeKernel/Modulations/LineModulation(1D).cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        //Modulation in 1D
        public class LineModulation
        {
            public delegate float       RatioFunc(float fRatio);
            public enum                 ECoord { X, Y, Z };
            protected ECoord            m_eValues;
            protected ECoord            m_eAxis;

            public float                m_fConstValue;      // has a constant return value
            protected RatioFunc         m_oFunc;            // has a function to be evaluated
            protected List<Vector3>     m_aDiscretePoints;  // has a discrete point list to be interpolated
            protected List<float>       m_aXValues;
            protected List<float>       m_aYValues;


            /// <summary>
            /// Line modulation built around a constant value.
            /// </summary>
            public LineModulation(float fConstValue)
            {
                m_fConstValue = fConstValue;
                m_oFunc       = fConstLineDummyFunc;

                // unused
                m_aDiscretePoints = new();
                m_aXValues = new();
                m_aYValues = new();
            }

            /// <summary>
            /// Line modulation based on a (continuous) 1D function.
            /// </summary>
            public LineModulation(RatioFunc oModuationFunc)
            {
                m_oFunc = oModuationFunc;

                // unused
                m_aDiscretePoints = new();
                m_aXValues = new();
                m_aYValues = new();
            }

            /// <summary>
            /// Line modulation based on a discrete distribution.
            /// </summary>
            public LineModulation(List<Vector3> aDiscretePoints, ECoord eValues, ECoord eAxis)
            {
                m_eValues           = eValues;
                m_eAxis             = eAxis;
                m_aDiscretePoints   = aDiscretePoints;

                m_aXValues          = new ();
                m_aYValues          = new();
                float fXValue       = fGetCoordinate(m_aDiscretePoints[0], eAxis);
                float fYValue       = fGetCoordinate(m_aDiscretePoints[0], eValues);
                m_aXValues.Add(fXValue);
                m_aYValues.Add(fYValue);

                for (int i = 1; i < m_aDiscretePoints.Count; i++)
                {
                    Vector3 vecPt   = m_aDiscretePoints[i];
                    fXValue         = fGetCoordinate(vecPt, eAxis);
                    fYValue         = fGetCoordinate(vecPt, eValues);

                    if (fXValue > m_aXValues[^1])
                    {
                        m_aXValues.Add(fXValue);
                        m_aYValues.Add(fYValue);
                    }
                }

                // fix start and end
                if (m_aXValues[0] > 0.0f)
                {
                    float fFirstY   = m_aYValues[0];
                    m_aXValues.Insert(0, 0.0f);
                    m_aYValues.Insert(0, fFirstY);
                }
                if (m_aXValues[^1] < 1.0f)
                {
                    float fLastY    = m_aYValues[^1];
                    m_aXValues.Add(1.0f);
                    m_aYValues.Add(fLastY);
                }
                
                // interpolation function
                m_oFunc = oPointsDummyFunc;
            }

            protected float fGetCoordinate(Vector3 vecPt, ECoord eCoord)
            {
                float fCoordinate = vecPt.X;
                if (eCoord == ECoord.Y)
                {
                    fCoordinate = vecPt.Y;
                }
                else if (eCoord == ECoord.Z)
                {
                    fCoordinate = vecPt.Z;
                }
                return fCoordinate;
            }

            protected float fConstLineDummyFunc(float fRatio)
            {
                return m_fConstValue;
            }

            protected float oPointsDummyFunc(float fX)
            {
                fX = float.Clamp(fX, 0, 1);
                fX = float.Clamp(fX, m_aXValues[0], m_aXValues[^1]);
        
                int idx = m_aXValues.BinarySearch(fX);
                if (idx < 0)
                {
                    idx = ~idx;
                }

                int iUpper      = Math.Min(idx, m_aXValues.Count - 1);
                int iLower      = Math.Max(iUpper - 1, 0);
                float fLowerX   = m_aXValues[iLower];
                float fUpperX   = m_aXValues[iUpper];

                if (fUpperX == fLowerX)
                {
                    return m_aYValues[iLower];
                }

                float fLR       = (fX - fLowerX) / (fUpperX - fLowerX);
                float fY        = m_aYValues[iLower] + fLR * (m_aYValues[iUpper] - m_aYValues[iLower]);
                return fY;
            }

            /// <summary>
            /// Queries the value of the line modulation at a given ratio.
            /// The ratio should be between 0 and 1.
            /// </summary>
            public float fGetModulation(float fRatio)
            {
                return m_oFunc(fRatio);
            }

            /// <summary>
            /// Multiplies a modulation with a factor.
            /// </summary>
            public static LineModulation operator *(float fFactor, LineModulation oMod)
            {
                return ModulationMultiplication.oGetScaledModulation(fFactor, oMod);
            }

            /// <summary>
            /// Adds one modulation to another.
            /// </summary>
            public static LineModulation operator +(LineModulation oMod1, LineModulation oMod2)
            {
                return ModulationAddition.oGetSumOfModulations(oMod1, oMod2);
            }

            /// <summary>
            /// Subtract one modulation from another.
            /// </summary>
            public static LineModulation operator -(LineModulation oMod1, LineModulation oMod2)
            {
                return ModulationAddition.oGetDifferenceOfModulations(oMod1, oMod2);
            }

            class ModulationAddition
            {
                LineModulation m_oMod1;
                LineModulation m_oMod2;

                ModulationAddition( LineModulation oMod1,
                                    LineModulation oMod2)
                {
                    m_oMod1 = oMod1;
                    m_oMod2 = oMod2;
                }

                public static LineModulation oGetSumOfModulations(  LineModulation oMod1,
                                                                    LineModulation oMod2)
                {
                    ModulationAddition oUtil = new (oMod1, oMod2);
                    return oUtil.oGetSumOfModulations();
                }

                public static LineModulation oGetDifferenceOfModulations(   LineModulation oMod1,
                                                                            LineModulation oMod2)
                {
                    ModulationAddition oUtil = new(oMod1, oMod2);
                    return oUtil.oGetDifferenceOfModulations();
                }

                LineModulation oGetSumOfModulations()
                {
                    return new LineModulation(fGetAddedModulation);
                }

                LineModulation oGetDifferenceOfModulations()
                {
                    return new LineModulation(fGetSubtractedModulation);
                }

                float fGetAddedModulation(float fLengthRatio)
                {
                    return m_oMod1.fGetModulation(fLengthRatio) + m_oMod2.fGetModulation(fLengthRatio);
                }

                float fGetSubtractedModulation(float fLengthRatio)
                {
                    return m_oMod1.fGetModulation(fLengthRatio) - m_oMod2.fGetModulation(fLengthRatio);
                }
            }

            class ModulationMultiplication
            {
                float             m_fFactor;
                LineModulation    m_oMod;
                

                ModulationMultiplication(   float fFactor,
                                            LineModulation oMod)
                {
                    m_fFactor   = fFactor;
                    m_oMod      = oMod;
                }

                public static LineModulation oGetScaledModulation(  float fFactor,
                                                                    LineModulation oMod)
                {
                    ModulationMultiplication oUtil = new (fFactor, oMod);
                    return oUtil.oGetMultipliedModulation();
                }

                LineModulation oGetMultipliedModulation()
                {
                    return new LineModulation(fGetScaledModulation);
                }

                float fGetScaledModulation(float fLengthRatio)
                {
                    return m_fFactor * m_oMod.fGetModulation(fLengthRatio);
                }
            }
        }

        public class Distribution
        {
            public float          m_fTotalLength;
            public LineModulation m_oModulation;

            /// <summary>
            /// This class bundles a line modulation (which is normalized) with a physical length.
            /// It can be used to store data distributions consistently.
            /// </summary>
            public Distribution(float           fTotalLength,
                                LineModulation  oModulation)
            {
                m_fTotalLength = fTotalLength;
                m_oModulation  = oModulation;
            }
        }

        public class GenericContour : Distribution
        {
            /// <summary>
            /// This class bundles a line modulation (which is normalized) with a physical length.
            /// It is a special case of a distribution that describes countours of rotationally symmetric objects.
            /// </summary>
            public GenericContour(  float          fTotalLength,
                                    LineModulation oModulation) : base(fTotalLength, oModulation) { }
        }
    }
}
```

### ShapeKernel/Modulations/SurfaceModulation(2D).cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        //Modulation in 2D
        public class SurfaceModulation
        {
            public delegate float       MappingFunc(float fGrayValue);
            public delegate float       RatioFunc(float fPhi, float fLengthRatio);
            public enum                 EInput { FUNC, IMAGE };
            public enum                 ELine { FIRST, SECOND };

            protected Image             m_oImage;
            protected RatioFunc         m_oFunc;
            protected MappingFunc       m_oMappingFunc;
            protected EInput            m_eInput;
            protected ELine             m_eLine;
            protected LineModulation    m_oLineModulation;
            protected float             m_fConstValue;


            /// <summary>
            /// Surface modulation based on a discrete distribution.
            /// </summary>
            public SurfaceModulation(float fConstValue)
            {
                m_fConstValue           = fConstValue;
                m_oFunc                 = fConstSurfaceDummyFunc;
                m_eInput                = EInput.FUNC;
            }

            /// <summary>
            /// Surface modulation based on a (continuous) 2D function.
            /// </summary>
            public SurfaceModulation(RatioFunc oFunc)
            {
                m_oFunc                 = oFunc;
                m_eInput                = EInput.FUNC;
            }

            /// <summary>
            /// Surface modulation derived from a line modulation.
            /// The enum dictates for which dimension the 1D line modulation applies.
            /// </summary>
            public SurfaceModulation(LineModulation oLineModulation, ELine eLine = ELine.SECOND)
            {
                m_oLineModulation       = oLineModulation;
                m_eLine                 = eLine;
                m_oFunc                 = fRatioSurfaceDummyFunc;
                m_eInput                = EInput.FUNC;
            }

            /// <summary>
            /// Surface modulation derived from an image.
            /// The mapping function indicates how an image grayscale value shall be translated into physical modulation.
            /// </summary>
            public SurfaceModulation(Image oImage, MappingFunc oMappingFunc)
            {
                m_oImage                = oImage;
                m_oMappingFunc          = oMappingFunc;
                m_eInput                = EInput.IMAGE;
            }

            protected float fConstSurfaceDummyFunc(float fPhi, float fLengthRatio)
            {
                return m_fConstValue;
            }

            protected float fRatioSurfaceDummyFunc(float fPhi, float fLengthRatio)
            {
                if (m_eLine == ELine.FIRST)
                {
                    return m_oLineModulation.fGetModulation(fPhi);
                }
                else
                {
                    return m_oLineModulation.fGetModulation(fLengthRatio);
                }
            }

            public EInput oGetInputType()
            {
                return m_eInput;
            }

            /// <summary>
            /// Queries the value of the surface modulation at given ratios.
            /// The ratios should be between 0 and 1.
            /// </summary>
            public float fGetModulation(float fPhi, float fLengthRatio)
            {
                if (m_eInput == EInput.FUNC)
                {
                    return m_oFunc(fPhi, fLengthRatio);
                }
                else if (m_eInput == EInput.IMAGE)
                {
                    int nXRange         = m_oImage.nWidth - 1;
                    int nYRange         = m_oImage.nHeight - 1;
                    int x               = (int)float.Round(nXRange - fPhi * nXRange);
                    int y               = (int)float.Round(fLengthRatio * nYRange);
                    float fGrayValue    = m_oImage.fValue(x, y);
                    float fValue        = m_oMappingFunc(fGrayValue);
                    return fValue;
                }
                else
                {
                    throw new Exception("Invalid Surface Modulation type.");
                }
            }

             /// <summary>
            /// Multiplies a modulation with a factor.
            /// </summary>
            public static SurfaceModulation operator *(float fFactor, SurfaceModulation oMod)
            {
                return ModulationMultiplication.oGetScaledModulation(fFactor, oMod);
            }

            /// <summary>
            /// Adds one modulation to another.
            /// </summary>
            public static SurfaceModulation operator +(SurfaceModulation oMod1, SurfaceModulation oMod2)
            {
                return ModulationAddition.oGetSumOfModulations(oMod1, oMod2);
            }

            /// <summary>
            /// Subtract one modulation from another.
            /// </summary>
            public static SurfaceModulation operator -(SurfaceModulation oMod1, SurfaceModulation oMod2)
            {
                return ModulationAddition.oGetDifferenceOfModulations(oMod1, oMod2);
            }

            class ModulationAddition
            {
                SurfaceModulation m_oMod1;
                SurfaceModulation m_oMod2;

                ModulationAddition( SurfaceModulation oMod1,
                                    SurfaceModulation oMod2)
                {
                    m_oMod1 = oMod1;
                    m_oMod2 = oMod2;
                }

                public static SurfaceModulation oGetSumOfModulations(   SurfaceModulation oMod1,
                                                                        SurfaceModulation oMod2)
                {
                    ModulationAddition oUtil = new (oMod1, oMod2);
                    return oUtil.oGetSumOfModulations();
                }

                public static SurfaceModulation oGetDifferenceOfModulations(SurfaceModulation oMod1,
                                                                            SurfaceModulation oMod2)
                {
                    ModulationAddition oUtil = new(oMod1, oMod2);
                    return oUtil.oGetDifferenceOfModulations();
                }

                SurfaceModulation oGetSumOfModulations()
                {
                    return new SurfaceModulation(fGetAddedModulation);
                }

                SurfaceModulation oGetDifferenceOfModulations()
                {
                    return new SurfaceModulation(fGetSubtractedModulation);
                }

                float fGetAddedModulation(float fPhi, float fLR)
                {
                    return m_oMod1.fGetModulation(fPhi, fLR) + m_oMod2.fGetModulation(fPhi, fLR);
                }

                float fGetSubtractedModulation(float fPhi, float fLR)
                {
                    return m_oMod1.fGetModulation(fPhi, fLR) - m_oMod2.fGetModulation(fPhi, fLR);
                }
            }

            class ModulationMultiplication
            {
                float             m_fFactor;
                SurfaceModulation m_oMod;
                

                ModulationMultiplication(   float fFactor,
                                            SurfaceModulation oMod)
                {
                    m_fFactor   = fFactor;
                    m_oMod      = oMod;
                }

                public static SurfaceModulation oGetScaledModulation(  float fFactor,
                                                                        SurfaceModulation oMod)
                {
                    ModulationMultiplication oUtil = new (fFactor, oMod);
                    return oUtil.oGetMultipliedModulation();
                }

                SurfaceModulation oGetMultipliedModulation()
                {
                    return new SurfaceModulation(fGetScaledModulation);
                }

                float fGetScaledModulation(float fPhi, float fLR)
                {
                    return m_fFactor * m_oMod.fGetModulation(fPhi, fLR);
                }
            }
        }
    }
}
```

### ShapeKernel/Splines/ControlPointSpline.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class ControlPointSpline : ISpline
        {
            public enum EEnds       { OPEN, CLOSED };
            protected EEnds         m_eEnds;
            protected List<float>   m_aKnot;
            protected List<Vector3> m_aControlPoints;
            protected uint          m_nDegree;
            protected float         m_fError = 0.0000001f;


            /// <summary>
            /// BSpline-based control point spline.
            /// Can have open ends or closed.
            /// Open ends will match the first and last control point precisely.
            /// https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-closed.html
            /// https://math.stackexchange.com/questions/1296954/b-spline-how-to-generate-a-closed-curve-using-uniform-b-spline-curve
            /// </summary>
            public ControlPointSpline(List<Vector3> aControlPoints, uint nDegree = 2, EEnds eEnds = EEnds.OPEN)
            {
                m_aControlPoints    = aControlPoints;
                m_eEnds             = eEnds;

                if (m_eEnds == EEnds.CLOSED)
                {
                    //check that first and last points are not the same!
                    if ((m_aControlPoints[0] - m_aControlPoints[^1]).Length() < m_fError)
                    {
                        m_aControlPoints.RemoveAt(m_aControlPoints.Count - 1);
                    }
                }

                m_nDegree           = nDegree;
                m_aKnot             = aGetKnotVector();
            }

            public List<float> aGetKnotVector()
            {
                if (m_eEnds == EEnds.OPEN)
                {
                    //calculate equal spacing
                    uint nNumberOfControlPoints = (uint)m_aControlPoints.Count;
                    uint nNumberOfKnots         = nNumberOfControlPoints + m_nDegree + 1;
                    List<float> aVector         = new List<float>(new float[nNumberOfKnots]);
                    uint nValidRange            = (nNumberOfKnots - m_nDegree - (m_nDegree + 1));
                    float dR                    = 1f / nValidRange;

                    for (int i = 0; i < nNumberOfKnots; i++)
                    {
                        float fValue = -(dR * m_nDegree) + dR * i;
                        fValue       = float.Clamp(fValue, 0f, 1f);
                        aVector[i]   = fValue;
                    }
                    return aVector;
                }
                else
                {
                    //add n-1 control points
                    uint nNumberOfControlPointsBefore = (uint)m_aControlPoints.Count;
                    for (int i = 0; i < nNumberOfControlPointsBefore - 1; i++)
                    {
                        m_aControlPoints.Add(m_aControlPoints[i]);
                    }

                    //calculate equal spacing
                    uint nNumberOfControlPoints = (uint)m_aControlPoints.Count;
                    uint nNumberOfKnots         = nNumberOfControlPoints + m_nDegree + 1;
                    List<float> aVector         = new List<float>(new float[nNumberOfKnots]);
                    uint nValidRange            = (nNumberOfKnots - m_nDegree - (m_nDegree + 1));
                    float dR                    = 1f / nValidRange;

                    for (int i = 0; i < nNumberOfKnots; i++)
                    {
                        float fValue    = -(dR * m_nDegree) + dR * i;
                        aVector[i]      = fValue;
                    }
                    return aVector;
                }
            }

            //render spline with given samples
            public List<Vector3> aGetPoints(uint nSamples)
            {
                List<Vector3> aPoints = new List<Vector3>();
                for (uint i = 0; i < nSamples; i++)
                {
                    float fLengthRatio  = (float)(i) / (float)(nSamples - 1);
                    Vector3 vecPt       = vecGetPointAt(fLengthRatio);
                    aPoints.Add(vecPt);
                }
                return aPoints;
            }

            //sample dynamically
            public Vector3 vecGetPointAt(float fLengthRatio)
            {
                Vector3 vecPt = new Vector3();
                for (int i = 0; i < m_aControlPoints.Count; ++i)
                {
                    float fBaseValue = fBaseFunc(fLengthRatio, i, (int)m_nDegree);
                    vecPt += fBaseValue * m_aControlPoints[(int)i];
                }
                return vecPt;
            }

            public float fBaseFunc(float fLengthRatio, int nControlPoint, int nDegree)
            {
                float fValue = 0;

                if (nDegree == 0)
                {
                    //last iteration loop
                    if (
                        (fLengthRatio >= m_aKnot[nControlPoint] && fLengthRatio < m_aKnot[nControlPoint + 1]) ||
                        ((MathF.Abs(fLengthRatio - m_aKnot[nControlPoint + 1]) < m_fError) && (MathF.Abs(fLengthRatio - m_aKnot[^1]) < m_fError))
                        )
                    {
                        fValue = 1f;
                    }
                }
                else
                {
                    //decrease degree with each iteration
                    if (MathF.Abs(m_aKnot[nControlPoint + nDegree] - m_aKnot[nControlPoint]) > m_fError)
                    {
                        fValue += (fLengthRatio - m_aKnot[nControlPoint]) / (m_aKnot[nControlPoint + nDegree] - m_aKnot[nControlPoint]) * fBaseFunc(fLengthRatio, nControlPoint, nDegree - 1);
                    }
                    if (MathF.Abs(m_aKnot[nControlPoint + nDegree + 1] - m_aKnot[nControlPoint + 1]) > m_fError)
                    {
                        fValue += (m_aKnot[nControlPoint + nDegree + 1] - fLengthRatio) / (m_aKnot[nControlPoint + nDegree + 1] - m_aKnot[nControlPoint + 1]) * fBaseFunc(fLengthRatio, nControlPoint + 1, nDegree - 1);
                    }
                }

                return fValue;
            }
        }
    }
}
```

### ShapeKernel/Splines/ControlPointSurface.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class ControlPointSurface
        {
            public enum EEnds    { OPEN, CLOSED };
            public EEnds         m_eEndsU;
            public EEnds         m_eEndsV;
            public List<float>   m_aKnotU;
            public List<float>   m_aKnotV;
            public uint          m_nDegreeU;
            public uint          m_nDegreeV;
            public List<List<Vector3>>
                                m_aControlGrid;
            protected float     m_fError = 0.0000001f;


            /// <summary>
            /// BSpline-based control grid surface (2D).
            /// Can have open ends or closed for either of the two dimensions.
            /// Open ends will match the first and last control grid precisely.
            /// https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-closed.html
            /// https://math.stackexchange.com/questions/1296954/b-spline-how-to-generate-a-closed-curve-using-uniform-b-spline-curve
            /// </summary>
            public ControlPointSurface(
                List<List<Vector3>> aControlGrid,
                uint                nDegreeU    = 2,
                uint                nDegreeV    = 2,
                EEnds               eEndsU      = EEnds.OPEN,
                EEnds               eEndsV      = EEnds.OPEN)
            {
                m_aControlGrid  = aControlGrid;
                m_nDegreeU      = nDegreeU;
                m_nDegreeV      = nDegreeV;
                m_eEndsU        = eEndsU;
                m_eEndsV        = eEndsV;

                if (m_eEndsU == EEnds.CLOSED)
                {
                    //check that first and last points are not the same!
                    if ((m_aControlGrid[0][0] - m_aControlGrid[^1][0]).Length() < m_fError)
                    {
                        m_aControlGrid = GridOperations.aRemoveListInX(m_aControlGrid, (uint)m_aControlGrid.Count - 1);
                    }
                }

                if (m_eEndsV == EEnds.CLOSED)
                {
                    //check that first and last points are not the same!
                    if ((m_aControlGrid[0][0] - m_aControlGrid[0][^1]).Length() < m_fError)
                    {
                        m_aControlGrid = GridOperations.aRemoveListInY(m_aControlGrid, (uint)m_aControlGrid.Count - 1);
                    }
                }

                m_aKnotU = aGetUKnotVector((uint)m_aControlGrid.Count, m_nDegreeU, m_eEndsU);
                m_aKnotV = aGetVKnotVector((uint)m_aControlGrid[0].Count, m_nDegreeV, m_eEndsV);
            }

            public List<float> aGetUKnotVector(uint nNumberOfControlPoints, uint nDegree, EEnds eEnds)
            {
                if (eEnds == EEnds.OPEN)
                {
                    //calculate equal spacing
                    uint nNumberOfKnots = nNumberOfControlPoints + nDegree + 1;
                    List<float> aVector = new List<float>(new float[nNumberOfKnots]);
                    uint nValidRange    = (nNumberOfKnots - nDegree - (nDegree + 1));
                    float dR            = 1f / nValidRange;

                    for (int i = 0; i < nNumberOfKnots; i++)
                    {
                        float fValue    = -(dR * nDegree) + dR * i;
                        fValue          = float.Clamp(fValue, 0f, 1f);
                        aVector[i]      = fValue;
                    }
                    return aVector;
                }
                else
                {
                    //add n-1 control points
                    uint nNumberOfControlPointsBefore = (uint)m_aControlGrid.Count;
                    for (int i = 0; i < nNumberOfControlPointsBefore - 1; i++)
                    {
                        List<Vector3> aListToAdd = GridOperations.aGetListInX(m_aControlGrid, (uint)i);
                        m_aControlGrid = GridOperations.aAddListInX(m_aControlGrid, aListToAdd);
                    }

                    //calculate equal spacing
                    nNumberOfControlPoints  = (uint)m_aControlGrid.Count;
                    uint nNumberOfKnots     = nNumberOfControlPoints + nDegree + 1;
                    List<float> aVector     = new List<float>(new float[nNumberOfKnots]);
                    uint nValidRange        = (nNumberOfKnots - nDegree - (nDegree + 1));
                    float dR                = 1f / nValidRange;

                    for (int i = 0; i < nNumberOfKnots; i++)
                    {
                        float fValue    = -(dR * nDegree) + dR * i;
                        aVector[i]      = fValue;
                    }
                    return aVector;
                }
            }

            public List<float> aGetVKnotVector(uint nNumberOfControlPoints, uint nDegree, EEnds eEnds)
            {
                if (eEnds == EEnds.OPEN)
                {
                    //calculate equal spacing
                    uint nNumberOfKnots = nNumberOfControlPoints + nDegree + 1;
                    List<float> aVector = new List<float>(new float[nNumberOfKnots]);
                    uint nValidRange    = (nNumberOfKnots - nDegree - (nDegree + 1));
                    float dR            = 1f / nValidRange;

                    for (int i = 0; i < nNumberOfKnots; i++)
                    {
                        float fValue    = -(dR * nDegree) + dR * i;
                        fValue          = float.Clamp(fValue, 0f, 1f);
                        aVector[i]      = fValue;
                    }
                    return aVector;
                }
                else
                {
                    //add n-1 control points
                    uint nNumberOfControlPointsBefore = (uint)m_aControlGrid[0].Count;
                    for (int i = 0; i < nNumberOfControlPointsBefore - 1; i++)
                    {
                        List<Vector3> aListToAdd = GridOperations.aGetListInY(m_aControlGrid, (uint)i);
                        m_aControlGrid = GridOperations.aAddListInY(m_aControlGrid, aListToAdd);
                    }

                    //calculate equal spacing
                    nNumberOfControlPoints  = (uint)m_aControlGrid[0].Count;
                    uint nNumberOfKnots     = nNumberOfControlPoints + nDegree + 1;
                    List<float> aVector     = new List<float>(new float[nNumberOfKnots]);
                    uint nValidRange        = (nNumberOfKnots - nDegree - (nDegree + 1));
                    float dR                = 1f / nValidRange;

                    for (int i = 0; i < nNumberOfKnots; i++)
                    {
                        float fValue    = -(dR * nDegree) + dR * i;
                        aVector[i]      = fValue;
                    }
                    return aVector;
                }
            }

            //render spline with given samples
            public List<List<Vector3>> aGetGrid(uint nUSamples = 500, uint nVSamples = 500)
            {
                List<List<Vector3>> aGrid = new List<List<Vector3>>();
                for (uint i = 0; i < nUSamples; i++)
                {
                    float fURatio           = (float)(i) / (float)(nUSamples - 1);
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint j = 0; j < nVSamples; j++)
                    {
                        float fVRatio = (float)(j) / (float)(nVSamples - 1);
                        Vector3 vecPt = vecGetPointAt(fURatio, fVRatio);
                        aPoints.Add(vecPt);
                    }
                    aGrid.Add(aPoints);
                }
                return aGrid;
            }

            //sample dynamically
            public Vector3 vecGetPointAt(float fURatio, float fVRatio)
            {
                Vector3 vecPt = new Vector3();
                for (int u = 0; u < m_aControlGrid.Count; u++)
                {
                    float fUBaseValue = fBaseFunc(m_aKnotU, fURatio, u, (int)m_nDegreeU);
                    for (int v = 0; v < m_aControlGrid[u].Count; v++)
                    {
                        float fVBaseValue = fBaseFunc(m_aKnotV, fVRatio, v, (int)m_nDegreeV);
                        vecPt += fUBaseValue * fVBaseValue * m_aControlGrid[(int)u][(int)v];
                    }
                }
                return vecPt;
            }

            public float fBaseFunc(List<float> aKnot, float fLengthRatio, int nControlPoint, int nDegree)
            {
                float fValue = 0;

                if (nDegree == 0)
                {
                    //last iteration loop
                    if (
                        (fLengthRatio >= aKnot[nControlPoint] && fLengthRatio < aKnot[nControlPoint + 1]) ||
                        ((MathF.Abs(fLengthRatio - aKnot[nControlPoint + 1]) < m_fError) && (MathF.Abs(fLengthRatio - aKnot[^1]) < m_fError))
                        )
                    {
                        fValue = 1f;
                    }
                }
                else
                {
                    //decrease degree with each iteration
                    if (MathF.Abs(aKnot[nControlPoint + nDegree] - aKnot[nControlPoint]) > m_fError)
                    {
                        fValue += (fLengthRatio - aKnot[nControlPoint]) / (aKnot[nControlPoint + nDegree] - aKnot[nControlPoint]) * fBaseFunc(aKnot, fLengthRatio, nControlPoint, nDegree - 1);
                    }
                    if (MathF.Abs(aKnot[nControlPoint + nDegree + 1] - aKnot[nControlPoint + 1]) > m_fError)
                    {
                        fValue += (aKnot[nControlPoint + nDegree + 1] - fLengthRatio) / (aKnot[nControlPoint + nDegree + 1] - aKnot[nControlPoint + 1]) * fBaseFunc(aKnot, fLengthRatio, nControlPoint + 1, nDegree - 1);
                    }
                }

                return fValue;
            }

            public List<List<Vector3>> aGetControlGrid()
            {
                return m_aControlGrid;
            }

            public Vector3 vecGetControlPoint(uint u, uint v)
            {
                return m_aControlGrid[(int)u][(int)v];
            }

            public void UpdateControlPoint(Vector3 vecPt, uint u, uint v)
            {
                m_aControlGrid[(int)u][(int)v] = vecPt;
            }
        }
    }
}
```

### ShapeKernel/Splines/CylindricalControlSpline.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class CylindricalControlSpline : ISpline
        {
            protected List<Vector3> m_aControlPoints;
            public enum EDirection { RADIAL, TANGENTIAL, Z };

            public CylindricalControlSpline(Vector3 vecStart)
            {
                m_aControlPoints = new List<Vector3>();
                m_aControlPoints.Add(vecStart);
            }

            public void AddRelativeStep(EDirection eDir, float fStepLength)
            {
                Vector3 vecLastPos              = m_aControlPoints[^1];
                if (eDir == EDirection.Z)
                {
                    Vector3 vecZDir             = Vector3.UnitZ;
                    Vector3 vecNewPos           = vecLastPos + fStepLength * vecZDir;
                    m_aControlPoints.Add(vecNewPos);
                }
                else if (eDir == EDirection.RADIAL)
                {
                    Vector3 vecRadialDir        = VecOperations.vecGetPlanarDir(vecLastPos);
                    Vector3 vecNewPos           = vecLastPos + fStepLength * vecRadialDir;
                    m_aControlPoints.Add(vecNewPos);
                }
                else
                {
                    Vector3 vecRadialDir        = VecOperations.vecGetPlanarDir(vecLastPos);
                    Vector3 vecTangentialDir    = Vector3.Cross(Vector3.UnitZ, vecRadialDir);
                    Vector3 vecNewPos           = vecLastPos + fStepLength * vecTangentialDir;
                    m_aControlPoints.Add(vecNewPos);
                }
            }

            public void AddAbsoluteStep(EDirection eDir, float fNewValue)
            {
                Vector3 vecLastPos      = m_aControlPoints[^1];
                if (eDir == EDirection.Z)
                {
                    Vector3 vecNewPos   = VecOperations.vecSetZ(vecLastPos, fNewValue);
                    m_aControlPoints.Add(vecNewPos);
                }
                else if (eDir == EDirection.RADIAL)
                {
                    Vector3 vecNewPos   = VecOperations.vecSetRadius(vecLastPos, fNewValue);
                    m_aControlPoints.Add(vecNewPos);
                }
            }

            public List<Vector3> aGetPoints(uint nSamples = 500)
            {
                ControlPointSpline oBSpline = new ControlPointSpline(m_aControlPoints);
                return oBSpline.aGetPoints(nSamples);
            }
        }
    }
}
```

### ShapeKernel/Splines/TangentialControlSpline.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public interface ISpline
        {
            public abstract List<Vector3> aGetPoints(uint nSamples = 500);
        }

        public class TangentialControlSpline : ISpline
        {
            protected ControlPointSpline m_oBSpline;

            public TangentialControlSpline(
                Vector3 vecStart,
                Vector3 vecEnd,
                Vector3 vecStartDir,
                Vector3 vecEndDir,
                float   fStartTangentStrength   = -1,
                float   fEndTangentStrenth      = -1,
                bool bRelativeStartStrength     = false,
                bool bRelativeEndStrength       = false)
            {
                if (fStartTangentStrength == -1)
                {
                    fStartTangentStrength   = 0.3f * (vecStart - vecEnd).Length();
                }
                if (fEndTangentStrenth == -1)
                {
                    fEndTangentStrenth      = 0.3f * (vecStart - vecEnd).Length();
                }
                if (bRelativeStartStrength == true)
                {
                    fStartTangentStrength   = fStartTangentStrength * (vecStart - vecEnd).Length();
                }
                if (bRelativeEndStrength == true)
                {
                    fEndTangentStrenth      = fEndTangentStrenth * (vecStart - vecEnd).Length();
                }

                Vector3 vecPt1                  = vecStart;
                Vector3 vecPt2                  = vecStart   + fStartTangentStrength * vecStartDir.Normalize();
                Vector3 vecPt3                  = vecEnd     - fEndTangentStrenth    * vecEndDir.Normalize();
                Vector3 vecPt4                  = vecEnd;
                List<Vector3> aControlPoints    = new List<Vector3>() { vecPt1, vecPt2, vecPt3, vecPt4 };
                m_oBSpline                      = new ControlPointSpline(aControlPoints);
            }

            public TangentialControlSpline(
                LocalFrame  oStartFrame,
                LocalFrame  oEndFrame,
                float       fStartTangentStrength   = -1,
                float       fEndTangentStrenth      = -1,
                bool        bRelativeStartStrength  = false,
                bool        bRelativeEndStrength    = false)
            {
                Vector3 vecStart                = oStartFrame.vecGetPosition();
                Vector3 vecEnd                  = oEndFrame.vecGetPosition();
                Vector3 vecStartDir             = oStartFrame.vecGetLocalZ();
                Vector3 vecEndDir               = oEndFrame.vecGetLocalZ();

                if (fStartTangentStrength == -1)
                {
                    fStartTangentStrength = 0.3f * (vecStart - vecEnd).Length();
                }
                if (fEndTangentStrenth == -1)
                {
                    fEndTangentStrenth = 0.3f * (vecStart - vecEnd).Length();
                }
                if (bRelativeStartStrength == true)
                {
                    fStartTangentStrength   = fStartTangentStrength * (vecStart - vecEnd).Length();
                }
                if (bRelativeEndStrength == true)
                {
                    fEndTangentStrenth      = fEndTangentStrenth * (vecStart - vecEnd).Length();
                }

                Vector3 vecPt1                  = vecStart;
                Vector3 vecPt2                  = vecStart   + fStartTangentStrength * vecStartDir.vecNormalized();
                Vector3 vecPt3                  = vecEnd     - fEndTangentStrenth    * vecEndDir.vecNormalized();
                Vector3 vecPt4                  = vecEnd;
                List<Vector3> aControlPoints    = new List<Vector3>() { vecPt1, vecPt2, vecPt3, vecPt4 };
                m_oBSpline                      = new ControlPointSpline(aControlPoints);
            }

            public List<Vector3> aGetPoints(uint nSamples = 500)
            {
                return m_oBSpline.aGetPoints(nSamples);
            }
        }
    }
}
```

### ShapeKernel/Utilities/Bisection.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using PicoGK.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class Bisection
        {
            public delegate float Func(float fValue);

            protected float m_fEpsilon;
            protected float m_fMinInput;
            protected float m_fMaxInput;
            protected float m_fTargetOutput;
            protected Func  m_oFunc;
            protected uint  m_nIterations;
            protected uint  m_nMaxIterations;
            protected float m_fRemainingDiff;
            protected float m_fBestGuess;


            /// <summary>
            /// Class to perform a bisection method to approximate an input point
            /// for the given function that returns the desired target output value.
            /// The allowable error epsilon is absolute.
            /// https://en.wikipedia.org/wiki/Bisection_method
            /// </summary>
            public Bisection(
                Func  oFunc,
                float fMinInput,
                float fMaxInput,
                float fTargetOutput,
                float fEpsilon       = 0.01f,
                uint  nMaxIterations = 500)
            {
                m_oFunc             = oFunc;
                m_fEpsilon          = fEpsilon;
                m_fMinInput         = fMinInput;
                m_fMaxInput         = fMaxInput;
                m_fTargetOutput     = fTargetOutput;
                m_nIterations       = 0;
                m_nMaxIterations    = nMaxIterations;
            }

            protected float fGetOutputFromFunc(float fInput)
            {
                return m_oFunc(fInput) - m_fTargetOutput;
            }

            public float fFindOptimalInput()
            {
                float fMin          = m_fMinInput;
                float fMax          = m_fMaxInput;
                float fOutputAtMin  = fGetOutputFromFunc(fMin);
                float fOutputAtMax  = fGetOutputFromFunc(fMax);
                if (fOutputAtMin.bAlmostZero())
                {
                    return m_fMinInput;
                }
                if (fOutputAtMax.bAlmostZero())
                {
                    return m_fMaxInput;
                }
                if (fOutputAtMin * fOutputAtMax >= 0)
                {
                    throw new BisectionException("No valid limits.");
                }

                float fMid              = fMin;
                m_fRemainingDiff        = fMax - fMin;
                while (m_fRemainingDiff >= m_fEpsilon)
                {
                    fMid                = 0.5f * (fMin + fMax);
                    if (fGetOutputFromFunc(fMid) == 0f)
                    {
                        break;
                    }
                    else if (fGetOutputFromFunc(fMid) * fGetOutputFromFunc(fMin) < 0)
                    {
                        fMax = fMid;
                    }
                    else
                    {
                        fMin = fMid;
                    }

                    m_fRemainingDiff    = fMax - fMin;
                    m_nIterations++;
                    m_fBestGuess        = fMid;

                    if (m_nIterations == m_nMaxIterations)
                    {
                        throw new BisectionException("No solution reached after max number of interations.");
                    }
                }
                return fMid;
            }

            public uint nGetIterations()
            {
                return m_nIterations;
            }

            public float fGetRemainingDiff()
            {
                return m_fRemainingDiff;
            }

            public float fGetBestGuess()
            {
                return m_fBestGuess;
            }
        }
    }

    public class BisectionException : Exception
    {
        public BisectionException() { }

        public BisectionException(string message) : base(message)
        {

        }
    }
}
```

### ShapeKernel/Utilities/CSVWriter.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//

using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class CSVWriter
        {
            protected StreamWriter  m_oWriter;
            protected string        m_strFilename;

            public CSVWriter(string strFilename)
            {
                m_strFilename       = strFilename;
                m_oWriter           = new StreamWriter(m_strFilename);
            }

            public void AddLine(string strLine)
            {
                m_oWriter.WriteLine(strLine);
            }

            public void ExportCSVFile()
            {
                try
                {
                    m_oWriter.Flush();
                    Library.Log($"CSV Export: {m_strFilename} exported.");
                }
                catch (Exception e)
                {
                    Library.Log("Could not save CSV: " + e.Message);
                }
            }
        }
    }
}
```

### ShapeKernel/Utilities/CylUtility.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
	namespace ShapeKernel
	{
        public static class CylUtility
        {
            /// <summary>
            /// Simplifies the creation of a base cylinder along the absolute z-axis.
            /// </summary>
            public static Voxels voxGetCyl(float fStartZ, float fEndZ, float fRadius)
            {
                LocalFrame oFrame   = new (new Vector3(0, 0, fStartZ));
                float fLength       = fEndZ - fStartZ;
                BaseCylinder oCyl   = new (oFrame, fLength, fRadius);
                return oCyl.voxConstruct();
            }

            /// <summary>
            /// Simplifies the creation of a base cone along the absolute z-axis.
            /// </summary>
            public static Voxels voxGetCone(float fStartZ, float fEndZ, float fStartRadius, float fEndRadius)
            {
                LocalFrame oFrame   = new (new Vector3(0, 0, fStartZ));
                float fLength       = fEndZ - fStartZ;
                BaseCone oCone      = new (oFrame, fLength, fStartRadius, fEndRadius);
                return oCone.voxConstruct();
            }

            /// <summary>
            /// Simplifies the creation of a base pipe along the absolute z-axis.
            /// </summary>
            public static Voxels voxGetPipe(float fStartZ, float fEndZ, float fInnerRadius, float fOuterRadius)
            {
                LocalFrame oFrame   = new (new Vector3(0, 0, fStartZ));
                float fLength       = fEndZ - fStartZ;
                BasePipe oPipe      = new (oFrame, fLength, fInnerRadius, fOuterRadius);
                return oPipe.voxConstruct();
            }

            /// <summary>
            /// Simplifies the creation of a base cylinder with respect to the reference frame's local z-axis.
            /// </summary>
            public static Voxels voxGetCyl(LocalFrame oRefFrame, float fStartZ, float fEndZ, float fRadius)
            {
                LocalFrame oFrame   = oRefFrame.oTranslate(fStartZ * oRefFrame.vecGetLocalZ());
                float fLength       = fEndZ - fStartZ;
                BaseCylinder oCyl   = new (oFrame, fLength, fRadius);
                return oCyl.voxConstruct();
            }

            /// <summary>
            /// Simplifies the creation of a base cone with respect to the reference frame's local z-axis.
            /// </summary>
            public static Voxels voxGetCone(LocalFrame oRefFrame, float fStartZ, float fEndZ, float fStartRadius, float fEndRadius)
            {
                LocalFrame oFrame   = oRefFrame.oTranslate(fStartZ * oRefFrame.vecGetLocalZ());
                float fLength       = fEndZ - fStartZ;
                BaseCone oCone      = new (oFrame, fLength, fStartRadius, fEndRadius);
                return oCone.voxConstruct();
            }

            /// <summary>
            /// Simplifies the creation of a base pipe with respect to the reference frame's local z-axis.
            /// </summary>
            public static Voxels voxGetPipe(LocalFrame oRefFrame, float fStartZ, float fEndZ, float fInnerRadius, float fOuterRadius)
            {
                LocalFrame oFrame   = oRefFrame.oTranslate(fStartZ * oRefFrame.vecGetLocalZ());
                float fLength       = fEndZ - fStartZ;
                BasePipe oPipe      = new (oFrame, fLength, fInnerRadius, fOuterRadius);
                return oPipe.voxConstruct();
            }
        }
    }
}
```

### ShapeKernel/Utilities/GridOperations.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//

using System.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public static class GridOperations
        {
            /// <summary>
            /// Swithes rows (x) and columns (y) within the grid.
            /// </summary>
            public static List<List<Vector3>> aGetInverseGrid(List<List<Vector3>> aGrid)
            {
                List<List<Vector3>> aInverseGrid = new List<List<Vector3>>();
                for (int i = 0; i < aGrid[0].Count; i++)
                {
                    List<Vector3> aPoints = new List<Vector3>();
                    for (int j = 0; j < aGrid.Count; j++)
                    {
                        aPoints.Add(aGrid[j][i]);
                    }
                    aInverseGrid.Add(aPoints);
                }
                return aInverseGrid;
            }

            /// <summary>
            /// Addes a row (in x) at the end.
            /// </summary>
            public static List<List<Vector3>> aAddListInX(List<List<Vector3>> aGrid, List<Vector3> aPoints)
            {
                aGrid.Add(aPoints);
                return aGrid;
            }

            /// <summary>
            /// Removes a row (in x) at the specified index.
            /// </summary>
            public static List<List<Vector3>> aRemoveListInX(List<List<Vector3>> aGrid, uint nIndex)
            {
                aGrid.RemoveAt((int)nIndex);
                return aGrid;
            }

            /// <summary>
            /// Returns the row (in x) at the specified index.
            /// </summary>
            public static List<Vector3> aGetListInX(List<List<Vector3>> aGrid, uint nIndex)
            {
                return aGrid[(int)nIndex];
            }

            /// <summary>
            /// Addes a column (in y) at the end.
            /// </summary>
            public static List<List<Vector3>> aAddListInY(List<List<Vector3>> aGrid, List<Vector3> aPoints)
            {
                List<List<Vector3>> aInverseGrid = aGetInverseGrid(aGrid);
                aInverseGrid = aAddListInX(aInverseGrid, aPoints);
                List<List<Vector3>> aNewGrid = aGetInverseGrid(aInverseGrid);
                return aNewGrid;
            }

            /// <summary>
            /// Removes a column (in y) at the specified index.
            /// </summary>
            public static List<List<Vector3>> aRemoveListInY(List<List<Vector3>> aGrid, uint nIndex)
            {
                List<List<Vector3>> aInverseGrid = aGetInverseGrid(aGrid);
                aInverseGrid.RemoveAt((int)nIndex);
                List<List<Vector3>> aNewGrid = aGetInverseGrid(aInverseGrid);
                return aNewGrid;
            }

            /// <summary>
            /// Returns the column (in y) at the specified index.
            /// </summary>
            public static List<Vector3> aGetListInY(List<List<Vector3>> aGrid, uint nIndex)
            {
                List<List<Vector3>> aInverseGrid = aGetInverseGrid(aGrid);
                return aInverseGrid[(int)nIndex];
            }
        }
    }
}
```

### ShapeKernel/Utilities/ImplicitUtility.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
	namespace ShapeKernel
	{
        public class ImplicitGyroid : IImplicit
		{
            protected float         m_fFrequencyScale;
			protected float		    m_fThicknessRatio;

            /// <summary>
            /// Helper class for an implicit gyroid pattern.
            /// The unit size in mm will determine the length after which the pattern repreats.
            /// The thickness ratio is a measure (!) for the wall thickness.
            /// Use fGetThicknessRatio function to determine the correct ratio value
            /// to meet a target physical wall thickness in mm.
            /// </summary>
            public ImplicitGyroid(float fUnitSize, float fThicknessRatio)
			{
                m_fFrequencyScale   = (2f * MathF.PI) / fUnitSize;
                m_fThicknessRatio   = fThicknessRatio;
            }

            /// <summary>
            /// Function to determine the correct gyroid thickness ratio value
            /// to meet a target physical wall thickness in mm.
            /// </summary>
            public static float fGetThicknessRatio(float fWallThickness, float fUnitSize)
            {
                float fRefWallRatio = fWallThickness * 10f / fUnitSize;
                return fRefWallRatio;
            }

            public float fSignedDistance(in Vector3 vecPt)
			{
                double dX = vecPt.X;
                double dY = vecPt.Y;
                double dZ = vecPt.Z;

                //calculate the gyroid surface equation
                double fDist =   Math.Sin(m_fFrequencyScale * dX) * Math.Cos(m_fFrequencyScale * dY) +
                                 Math.Sin(m_fFrequencyScale * dY) * Math.Cos(m_fFrequencyScale * dZ) +
                                 Math.Sin(m_fFrequencyScale * dZ) * Math.Cos(m_fFrequencyScale * dX);

                //apply thickness to the gyroid surface
                return (float)(Math.Abs(fDist) - 0.5f * m_fThicknessRatio);
            }
		}

        public class ImplicitSphere : IImplicit
        {
			protected Vector3	m_vecCentre;
			protected float		m_fRadius;

            /// <summary>
            /// Helper class for an implicit sphere.
            /// </summary>
            public ImplicitSphere(Vector3 vecCentre, float fRadius)
            {
				m_vecCentre = vecCentre;
				m_fRadius	= fRadius;
            }

            public float fSignedDistance(in Vector3 vecPt)
            {
                return (vecPt - m_vecCentre).Length() - m_fRadius;
            }
        }

        public class ImplicitGenus : IImplicit
        {
            protected float m_fGap;

            /// <summary>
            /// Helper class for an implicit genus.
            /// https://en.wikipedia.org/wiki/Implicit_surface
            /// The sepcified gap controls the size of the hole in center.
            /// </summary>
            public ImplicitGenus(float fGap)
            {
                m_fGap = fGap;
            }

            public float fSignedDistance(in Vector3 vecPt)
            {
                return  (float)(2 * vecPt.Y * (vecPt.Y * vecPt.Y - 3 * vecPt.X * vecPt.X) * (1 - vecPt.Z * vecPt.Z)
                            + Math.Pow((vecPt.X * vecPt.X + vecPt.Y * vecPt.Y), 2)
                            - (9 * vecPt.Z * vecPt.Z - 1) * (1 - vecPt.Z * vecPt.Z) - m_fGap);
            }
        }

        public class ImplicitSuperEllipsoid : IImplicit
        {
            protected float     m_fAx;
            protected float     m_fAy;
            protected float     m_fAz;
            protected float     m_fEpsilon1;
            protected float     m_fEpsilon2;
            protected Vector3   m_vecCentre;

            /// <summary>
            /// Helper class for an implicit super ellipsoid.
            /// https://en.wikipedia.org/wiki/Superellipsoid
            /// </summary>
            public ImplicitSuperEllipsoid(Vector3 vecCentre, float fAx, float fAy, float fAz,  float fEpsilon1, float fEpsilon2)
            {
                m_fAx           = fAx;                
                m_fAy           = fAy;
                m_fAz           = fAz;
                m_fEpsilon1     = fEpsilon1;
                m_fEpsilon2     = fEpsilon2;
                m_vecCentre     = vecCentre;
            }

            public float fSignedDistance(in Vector3 vecPt)
            {
                double dX           = Math.Abs(vecPt.X + m_vecCentre.X)/ m_fAx;
                double dY           = Math.Abs(vecPt.Y + m_vecCentre.Y)/ m_fAy;
                double dZ           = Math.Abs(vecPt.Z + m_vecCentre.Z)/ m_fAz;

                double dDist        = Math.Pow((Math.Pow(dX, 2 / m_fEpsilon2) + Math.Pow(dY, 2 / m_fEpsilon2)), m_fEpsilon2 / m_fEpsilon1)
                                        + Math.Pow(dZ, 2 / m_fEpsilon1) ;
                float fFinalDist    = (float)(dDist - 1);
                return fFinalDist;
            }
        }
    }
}
```

### ShapeKernel/Utilities/LineDecimation.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//



using System.Numerics;


namespace Leap71
{
	namespace ShapeKernel
	{
		public class LineDecimation
		{
			protected List<Vector3> m_aPoints;
			protected List<Vector3> m_aDecimatedPoints;


			/// <summary>
			/// Class to resample a spline by decimating points that lie in a staight line given the error range.
			/// Start and end points remain constant.
			/// The error is measured as a points deviation distance perpendicular to the idea line (in mm).
			/// </summary>
			public LineDecimation(List<Vector3> aPoints, float fMaxError)
			{
				m_aPoints = aPoints;


				//decimate and record point indices
				int iStartIndex		= 0;
				int iEndIndex		= 0;
				List<int> aIndices	= new List<int>() { iStartIndex };
				while (iEndIndex < aPoints.Count - 1)
				{
					iEndIndex		= iGetNextIndex(iStartIndex, fMaxError);
					iStartIndex		= iEndIndex;
					aIndices.Add(iStartIndex);
				}


				//assemble decimated points
				m_aDecimatedPoints = new List<Vector3>();
				foreach (int iIndex in aIndices)
				{
					m_aDecimatedPoints.Add(m_aPoints[iIndex]);
				}
			}

			protected int iGetNextIndex(int iStartIndex, float fMaxError)
			{
				if (iStartIndex > m_aPoints.Count - 2)
				{
					int iEndIndex = m_aPoints.Count - 1;
					return iEndIndex;
				}
				else
				{
					int iCount		= 1;
					int iEndIndex	= iStartIndex + iCount;
					List<Vector3> aLinePoints = m_aPoints.GetRange(iStartIndex, 2);
					for (int iIndex = iStartIndex + 2; iIndex < m_aPoints.Count; iIndex++)
					{
						aLinePoints.Add(m_aPoints[iIndex]);
						float fError = fGetMaxError(aLinePoints);

						if (fError > fMaxError)
						{
							break;
						}
						iEndIndex = iIndex;
					}
					return iEndIndex;
				}
			}

			protected static float fGetMaxError(List<Vector3> aLinePoints)
			{
				Vector3 vecLineDir		= aLinePoints[^1] - aLinePoints[0];
				float fMaxError			= 0;
				int iCounter			= 0;
				for (int i = 1; i < aLinePoints.Count - 1; i++)
				{
					Vector3 vecPointer	= (aLinePoints[i] - aLinePoints[0]);
					float fAngle		= VecOperations.fGetAngleBetween(vecPointer, vecLineDir);
					fMaxError			= MathF.Max(fMaxError, MathF.Sin(fAngle) * vecPointer.Length());
					iCounter++;
				}
				return fMaxError;
			}

			public List<Vector3> aGetDecimatedPoints()
			{
				return m_aDecimatedPoints;
			}
		}
	}
}
```

### ShapeKernel/Utilities/ListOperations.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


namespace Leap71
{
    namespace ShapeKernel
    {
        public class ListOperations
        {
            /// <summary>
            /// Samples the specified list with an increment.
            /// Note that the count of the list will change!
            /// Start and end value remain constant.
            /// </summary>
            public static List<float> aOverSampleList(List<float> aList, int iSamplesPerStep)
            {
                List<float> aFinalList = new List<float>();
                for (int i = 1; i < aList.Count; i++)
                {
                    for (int j = 0; j < iSamplesPerStep; j++)
                    {
                        float fValue = aList[i - 1] + (float)j / (float)(iSamplesPerStep) * (aList[i] - aList[i - 1]);
                        aFinalList.Add(fValue);
                    }
                }
                aFinalList.Add(aList[^1]);
                return aFinalList;
            }

            /// <summary>
            /// Samples the specified list with an increment.
            /// Note that the count of the list will change!
            /// Start and end value remain constant.
            /// </summary>
            public static List<float> aSubsampleList(List<float> aList, int iSampleSize)
            {
                List<float> aFinalList = new List<float>();
                int i = 0;
                for (i = 0; i < aList.Count; i += iSampleSize)
                {
                    aFinalList.Add(aList[i]);
                }
                aFinalList.Add(aList[^1]);
                return aFinalList;
            }

            /// <summary>
            /// Returns the index of the maximum value within the list.
            /// </summary>
            public static int iGetIndexOfMaxValue(List<float> aList)
            {
                float fMaxValue = float.MinValue;
                int iIndex = -1;

                for (int i = 0; i < aList.Count; i++)
                {
                    if (aList[i] > fMaxValue)
                    {
                        fMaxValue = aList[i];
                        iIndex = i;
                    }
                }
                return iIndex;
            }

            /// <summary>
            /// Returns the index of the minimum value within the list.
            /// </summary>
            public static int iGetIndexOfMinValue(List<float> aList)
            {
                float fMinValue = float.MaxValue;
                int iIndex = -1;

                for (int i = 0; i < aList.Count; i++)
                {
                    if (aList[i] < fMinValue)
                    {
                        fMinValue = aList[i];
                        iIndex = i;
                    }
                }
                return iIndex;
            }
        }
    }
}
```

### ShapeKernel/Utilities/Measure.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
	namespace ShapeKernel
	{
		public partial class Measure
		{
            /// <summary>
            /// Calculates the volume by counting the number of voxels.
            /// The volume is measured in mm^3.
            /// </summary>
            public static float fGetVolume(Voxels oVoxels)
            {
                oVoxels.CalculateProperties(out float fVolume, out BBox3 oBBox);
                return fVolume;
            }

            /// <summary>
            /// Converts voxelfield into mesh.
            /// Calculates the area of each mesh triangle.
            /// Adds all triangle areas to obtain the final result.
            /// The area is measured in mm^2.
            /// </summary>
            public static float fGetSurfaceArea(Voxels oVoxels)
			{
				Mesh oMesh = new Mesh(oVoxels);
				return fGetSurfaceArea(oMesh);
            }

			/// <summary>
            /// Calculates the area of each mesh triangle.
            /// Adds all triangle areas to obtain the final result.
            /// The area is measured in mm^2.
            /// </summary>
            public static float fGetSurfaceArea(Mesh msh)
			{
				int nTriangleCount	= msh.nTriangleCount();

				float fArea = 0;
                
				for (int n = 0; n < nTriangleCount; n++)
				{
                    msh.GetTriangle(    n, 
                                        out Vector3 vecA, 
                                        out Vector3 vecB, 
                                        out Vector3 vecC);

					fArea += fGetTriangleArea(vecA, vecB, vecC);
                }
				return fArea;
			}

            /// <summary>
            /// Returns the area for an individual triangle.
            /// The area is measured in mm^2.
            /// </summary>
            public static float fGetTriangleArea(Vector3 vecA, Vector3 vecB, Vector3 vecC)
			{
				Vector3 vecSideAB	= vecB - vecA;
                Vector3 vecSideAC	= vecC - vecA;
				float fArea			= 0.5f * Vector3.Cross(vecSideAB, vecSideAC).Length();
				return fArea;
            }

            /// <summary>
            /// Returns the centre of gravity of a voxelfield.
            /// The function iterates across all active voxels.
            /// All active voxel positions are accumulated and devided by the voxel count.
            /// The centre of gravity is measured in units of mm.
            /// </summary>
			public static Vector3 vecGetCentreOfGravity(Voxels oVoxels)
            {
                VectorField oGradientField  = new(oVoxels);
                ScalarField oSDField        = new(oVoxels);
                oVoxels.CalculateProperties(out float fVolume, out BBox3 oBox);
                oBox.Grow(1f);
                Vector3 vecSize             = oBox.vecSize();
                float fStep                 = Library.fVoxelSizeMM;
                Vector3 vecCoG              = new Vector3();
                float fCounter              = 0f;


                for (float fX = 0f; fX < vecSize.X; fX += fStep)
                {
                    for (float fY = 0f; fY < vecSize.Y; fY += fStep)
                    {
                        for (float fZ = 0f; fZ < vecSize.Z; fZ += fStep)
                        {
                            Vector3 vecPt  = oBox.vecMin + new Vector3(fX, fY, fZ);
                            if (oGradientField.bGetValue(vecPt, out Vector3 vecVal))
                            {
                                if (oSDField.bGetValue(vecPt, out float fSDVal))
                                {
                                    if (fSDVal < 0)
                                    {
                                        vecCoG      += vecPt;
                                        fCounter    += 1f;
                                    }
                                }
                            }
                        }
                    }
                }
                vecCoG /= fCounter;
                return vecCoG;
            }

            /// <summary>
            /// Returns the inertia tensor of a voxelfield with respect to a reference frame.
            /// The function iterates across all active voxels.
            /// All active voxels are treated as idealized point masses.
            /// All active voxel contributions to the inertia tensor are accumulated and devided by the mass.
            /// The voxelfield's density is specified in kg/m3.
            /// The density is assumed to be homogeneously distributed.
            /// The resulting 3x3 matrix holds components of moments of inertia in units of kg * m2.
            /// </summary>
            public static double[,] matGetMomentOfInertia(Voxels oVoxels, LocalFrame oRefFrame, float fDensity)
            {
                // initialize
                float fMeasureMass          = 0;
                double[,] matInertiaTensor  = new double[3, 3]   {
                                                                    { 0f, 0f, 0f },
                                                                    { 0f, 0f, 0f },
                                                                    { 0f, 0f, 0f }
                                                                };

                // iterate across all active voxels
                // treat active voxel as point mass
                VectorField oGradientField  = new(oVoxels);
                ScalarField oSDField        = new(oVoxels);
                oVoxels.CalculateProperties(out float fVolume, out BBox3 oBox);
                oBox.Grow(1f);
                Vector3 vecSize             = oBox.vecSize();
                float fStep                 = Library.fVoxelSizeMM;
                float fCounter              = 0f;

                // count active voxels
                for (float fX = 0f; fX < vecSize.X; fX += fStep)
                {
                    for (float fY = 0f; fY < vecSize.Y; fY += fStep)
                    {
                        for (float fZ = 0f; fZ < vecSize.Z; fZ += fStep)
                        {
                            Vector3 vecPt  = oBox.vecMin + new Vector3(fX, fY, fZ);
                            if (oGradientField.bGetValue(vecPt, out Vector3 vecVal))
                            {
                                if (oSDField.bGetValue(vecPt, out float fSDVal))
                                {
                                    if (fSDVal < 0)
                                    {
                                        fCounter               += 1f;
                                    }
                                }
                            }
                        }
                    }
                }

                float dVoxelVolume  = Library.fVoxelSizeMM * Library.fVoxelSizeMM * Library.fVoxelSizeMM;
                float fVoxelVolume  = fCounter * dVoxelVolume;
                float fVolumeFactor = fVolume / fVoxelVolume;

                for (float fX = 0f; fX < vecSize.X; fX += fStep)
                {
                    for (float fY = 0f; fY < vecSize.Y; fY += fStep)
                    {
                        for (float fZ = 0f; fZ < vecSize.Z; fZ += fStep)
                        {
                            Vector3 vecPt  = oBox.vecMin + new Vector3(fX, fY, fZ);
                            if (oGradientField.bGetValue(vecPt, out Vector3 vecVal))
                            {
                                if (oSDField.bGetValue(vecPt, out float fSDVal))
                                {
                                    if (fSDVal < 0)
                                    {
                                        float dVoxelMass        = fDensity * fVolumeFactor * dVoxelVolume / MathF.Pow(10f, 9f);     // kg
                                        double[,] matIncrement  = matGetMomentOfInertia(vecPt, oRefFrame, dVoxelMass);              // kg * m2
                                        fMeasureMass            += dVoxelMass;

                                        // accumulate inertia matrices
                                        for (int k = 0; k < 3; k++)
                                        {
                                            for (int l = 0; l < 3; l++)
                                            {
                                                matInertiaTensor[k, l] += matIncrement[k, l];
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // compare total mass against accumulated voxel mass
                float fMass = fDensity * fVolume / MathF.Pow(10f, 9f);
        
                return matInertiaTensor;
            }

            /// <summary>
            /// Returns the inertia tensor of an idealized point mass with respect to a reference frame.
            /// General Formula: I = m * r^2.
            /// The point's mass is specified in kg.
            /// The resulting 3x3 matrix holds components of moments of inertia in units of kg * mm2.
            /// </summary>
            protected static double[,] matGetMomentOfInertia(Vector3 vecPt, LocalFrame oRefFrame, float fMass)
            {
                // get coordinate representation relative to reference frame
                Vector3 vecRel      = VecOperations.vecExpressPointInFrame(oRefFrame, vecPt);
                float fX            = vecRel.X;
                float fY            = vecRel.Y;
                float fZ            = vecRel.Z;

                // components of inertia tensor
                float fIxx          = fMass * (fY * fY + fZ * fZ);
                float fIyy          = fMass * (fX * fX + fZ * fZ);
                float fIzz          = fMass * (fX * fX + fY * fY);
                float fIxy          = fMass * (-fX * fY);
                float fIxz          = fMass * (-fX * fZ);
                float fIyx          = fMass * (-fY * fX);
                float fIyz          = fMass * (-fY * fZ);
                float fIzx          = fMass * (-fZ * fX);
                float fIzy          = fMass * (-fZ * fY);

                // write inertia tensor from components as a 3x3 matrix
                double[,] matInertiaTensor = new double[3, 3]   {
                                                                    { fIxx, fIxy, fIxz },
                                                                    { fIyx, fIyy, fIyz },
                                                                    { fIzx, fIzy, fIzz }
                                                                };
                return matInertiaTensor;
            }

			/// <summary>
			/// Runs a test to compare the calculated surface area of a sphere against the measured value.
			/// </summary>
			public static void TestSurfaceMesurement()
			{
				float fRadius				= 20f;
				BaseSphere oSphere			= new BaseSphere(new LocalFrame(), fRadius);
				Voxels voxSphere			= oSphere.voxConstruct();

				float fMeasuredSurfaceArea	= fGetSurfaceArea(voxSphere);
				float fAnalyticSurfaceArea	= 4f * MathF.PI * fRadius * fRadius;

				Library.Log($"Measured surface area = {fMeasuredSurfaceArea} mm^2.");
                Library.Log($"Expected surface area = {fAnalyticSurfaceArea} mm^2.");
            }

            /// <summary>
            /// Runs a test to compare the calculated volume of a sphere against the measured value.
            /// </summary>
            public static void TestVolumeMesurement()
			{
				float fRadius				= 20f;
				BaseSphere oSphere			= new BaseSphere(new LocalFrame(), fRadius);
				Voxels voxSphere			= oSphere.voxConstruct();

				float fMeasuredVolume		= fGetVolume(voxSphere);
				float fAnalyticVolume		= 4f / 3f * MathF.PI * fRadius * fRadius * fRadius;

				Library.Log($"Measured volume = {fMeasuredVolume} mm^3.");
                Library.Log($"Expected volume = {fAnalyticVolume} mm^3.");
            }

            /// <summary>
            /// Runs a test to compare the calculated centre of gravity of a cylinder against the measured value.
            /// </summary>
            public static void TestCentreOfGravityMesurement()
            {
                float fHeight               = 40f;
                float fRadius               = 30f;
                LocalFrame oFrame           = new LocalFrame(new Vector3(30, 36, -12), new Vector3(2f, -1f, 1f).Normalize());
                BaseCylinder oCyl           = new BaseCylinder(oFrame, fHeight, fRadius);
                Voxels vox                  = oCyl.voxConstruct();

                Vector3 vecMeasuredCoG      = vecGetCentreOfGravity(vox);
                Vector3 vecAnalyticCoG      = oFrame.vecGetPosition() + 0.5f * fHeight * oFrame.vecGetLocalZ();

                Library.Log($"Measured centre of gravity = {vecMeasuredCoG} mm.");
                Library.Log($"Expected centre of gravity = {vecAnalyticCoG} mm.");
            }

            /// <summary>
            /// Runs a test to compare the calculated inertia tensor of a cylinder against the measured value.
            /// </summary>
            public static void TestInertiaTensorMesurement()
            {
                float fHeight               = 5f;
                float fRadius               = 50f;
                float fDensity              = 7000f;
                LocalFrame oFrame           = new LocalFrame(new Vector3(30, 36, -12), new Vector3(2f, -1f, 1f).Normalize());
                BaseCylinder oCyl           = new BaseCylinder(oFrame, fHeight, fRadius);
                Voxels vox                  = oCyl.voxConstruct();



                // measured cylinder
                Vector3 vecMeasuredCoG      = vecGetCentreOfGravity(vox);
                float fMeasuredVolume       = fGetVolume(vox);                                      // mm3
                float fMeasuredMass         = fDensity * fMeasuredVolume / MathF.Pow(10f, 9f);      // kg

                // reference frame witho on CoG and main axes
                LocalFrame oRefFrame        = new LocalFrame(vecMeasuredCoG, oFrame.vecGetLocalZ(), oFrame.vecGetLocalX());
                double[,] matInertiaTensor  = matGetMomentOfInertia(vox, oRefFrame, fDensity);
                float fMeasuredIxx          = (float)matInertiaTensor[0, 0];
                float fMeasuredIyy          = (float)matInertiaTensor[1, 1];
                float fMeasuredIzz          = (float)matInertiaTensor[2, 2];



                // analytic cylinder
                Vector3 vecAnalyticCoG      = oFrame.vecGetPosition() + 0.5f * fHeight * oFrame.vecGetLocalZ();
                float fAnalyticVolume       = MathF.PI * fRadius * fRadius * fHeight;               // mm3
                float fAnalyticMass         = fDensity * fAnalyticVolume / MathF.Pow(10f, 9f);      // kg

                // analytical formulas for a "chubby" cylinder
                float fAnalyticIxx          = 0.25f * fAnalyticMass * fRadius * fRadius;
                float fAnalyticIyy          = 0.25f * fAnalyticMass * fRadius * fRadius;
                float fAnalyticIzz          = 0.5f * fAnalyticMass * fRadius * fRadius;
                if (fHeight > 5f * fRadius)
                {
                    // analytical formulas for a "skinny" cylinder
                    fAnalyticIxx            = 1f / 12f * fAnalyticMass * (3f * fRadius * fRadius + fHeight * fHeight);
                    fAnalyticIyy            = 1f / 12f * fAnalyticMass * (3f * fRadius * fRadius + fHeight * fHeight);
                    fAnalyticIzz            = 0.5f * fAnalyticMass * fRadius * fRadius;
                }
              
                Library.Log($"Measured Mass = {fMeasuredMass} kg.");
                Library.Log($"Measured Centre of Gravity = {vecMeasuredCoG} mm.");
                Library.Log($"Measured Ixx = {fMeasuredIxx} kg * mm2.");
                Library.Log($"Measured Iyy = {fMeasuredIyy} kg * mm2.");
                Library.Log($"Measured Izz = {fMeasuredIzz} kg * mm2.");
                Library.Log($"\n");
                Library.Log($"Expected Mass = {fAnalyticMass} kg.");
                Library.Log($"Expected Centre of Gravity = {vecAnalyticCoG} mm.");
                Library.Log($"Expected Ixx = {fAnalyticIxx} kg * mm2.");
                Library.Log($"Expected Iyy = {fAnalyticIyy} kg * mm2.");
                Library.Log($"Expected Izz = {fAnalyticIzz} kg * mm2.");
            }
        }
	}
}
```

### ShapeKernel/Utilities/MeshUtility.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
	namespace ShapeKernel
	{
		public static class MeshUtility
		{
            /// <summary>
            /// Creates a mesh object from a regularly arranged point grid.
            /// </summary>
            public static Mesh mshFromGrid(List<List<Vector3>> aGrid)
            {
                Mesh msh = new Mesh();
                for (int i = 1; i < aGrid.Count; i++)
                {
                    for (int j = 1; j < aGrid[i].Count; j++)
                    {
                        Vector3 vecPt1 = aGrid[i - 1][j - 1];
                        Vector3 vecPt2 = aGrid[i - 1][j];
                        Vector3 vecPt3 = aGrid[i][j];
                        Vector3 vecPt4 = aGrid[i][j - 1];
                        msh.nAddTriangle(vecPt4, vecPt1, vecPt2);
                        msh.nAddTriangle(vecPt2, vecPt3, vecPt4);
                    }
                }
                return msh;
            }

            /// <summary>
            /// Creates a mesh object from four points that form a quad shape.
            /// </summary>
            public static Mesh mshFromQuad(
                Vector3 vecPt1,
                Vector3 vecPt2,
                Vector3 vecPt3,
                Vector3 vecPt4)
            {
                Mesh msh = new Mesh();
                msh.nAddTriangle(vecPt4, vecPt1, vecPt2);
                msh.nAddTriangle(vecPt2, vecPt3, vecPt4);
                return msh;
            }

            /// <summary>
            /// Uses the referenced mesh object and adds four points that form a quad shape.
            /// </summary>
            public static void AddQuad(
                ref Mesh msh,
                Vector3 vecPt1,
                Vector3 vecPt2,
                Vector3 vecPt3,
                Vector3 vecPt4)
            {
                msh.nAddTriangle(vecPt4, vecPt1, vecPt2);
                msh.nAddTriangle(vecPt2, vecPt3, vecPt4);
            }

            /// <summary>
            /// Creates a new mesh by applying a transformation function to each vertex of the input mesh.
            /// </summary>
            public static Mesh mshApplyTransformation(  Mesh msh,
                                                        BaseShape.fnVertexTransformation fnTrafo)
            {
                Mesh oNewMesh       = new Mesh();
                int nTriangles      = msh.nTriangleCount();
                for (int i = 0; i < nTriangles; i++)
                {
                    Triangle oTri   = msh.oTriangleAt(i);
                    int iIndexA     = oTri.A;
                    int iIndexB     = oTri.B;
                    int iIndexC     = oTri.C;
                    Vector3 vecA    = msh.vecVertexAt(iIndexA);
                    Vector3 vecB    = msh.vecVertexAt(iIndexB);
                    Vector3 vecC    = msh.vecVertexAt(iIndexC);
                    Vector3 vecNewA = fnTrafo(vecA);
                    Vector3 vecNewB = fnTrafo(vecB);
                    Vector3 vecNewC = fnTrafo(vecC);
                    oNewMesh.nAddTriangle(vecNewA, vecNewB, vecNewC);
                }
                return oNewMesh;
            }

            /// <summary>
            /// Converts voxels into a mesh.
            /// Creates a new mesh by applying a transformation function to each vertex of the input mesh.
            /// Voxelizes the new mesh.
            /// </summary>
            public static Voxels voxApplyTransformation(Voxels vox, 
                                                        BaseShape.fnVertexTransformation fnTrafo)
            {
                Mesh msh    = new (vox);
                msh         = mshApplyTransformation(msh, fnTrafo);
                return new Voxels(msh);
            }

            /// <summary>
            /// Returns a mesh that has been translated from the input to the output frame.
            /// </summary>
            public static Mesh mshTranslateMeshOntoFrame(Mesh msh,
                                                         LocalFrame oInputFrame,
                                                         LocalFrame oOutputFrame)
            {
                return Mover.mshTranslateMeshOntoFrame(msh, oInputFrame, oOutputFrame);
            }

            public static Mesh Append(this Mesh msh1, Mesh msh2)
            {
                int nTriangles      = msh2.nTriangleCount();
                for (int i = 0; i < nTriangles; i++)
                {
                    Triangle oTri   = msh2.oTriangleAt(i);
                    int iIndexA     = oTri.A;
                    int iIndexB     = oTri.B;
                    int iIndexC     = oTri.C;
                    Vector3 vecA    = msh2.vecVertexAt(iIndexA);
                    Vector3 vecB    = msh2.vecVertexAt(iIndexB);
                    Vector3 vecC    = msh2.vecVertexAt(iIndexC);
                    msh1.nAddTriangle(vecA, vecB, vecC);
                }
                return msh1;
            }

            protected class Mover
            {
                LocalFrame m_oInputFrame;
                LocalFrame m_oOutputFrame;

                /// <summary>
                /// Returns a mesh that has been translated from the input to the output frame.
                /// </summary>
                public static Mesh mshTranslateMeshOntoFrame(Mesh msh, LocalFrame oInputFrame, LocalFrame oOutputFrame)
                {
                    Mover oMover  = new(oInputFrame, oOutputFrame);
                    Mesh mshMoved = mshApplyTransformation(msh, oMover.vecTrafo);
                    return mshMoved;
                }

                protected Mover(LocalFrame oInputFrame,
                                LocalFrame oOutputFrame)
                {
                    m_oInputFrame  = oInputFrame;
                    m_oOutputFrame = oOutputFrame;
                }

                public Vector3 vecTrafo(Vector3 vecPt)
                {
                    Vector3 vecRel = VecOperations.vecExpressPointInFrame(m_oInputFrame, vecPt);
                    Vector3 vecNew = VecOperations.vecTranslatePointOntoFrame(m_oOutputFrame, vecRel);
                    return vecNew;
                }
            }
        }
    }
}
```

### ShapeKernel/Utilities/PolygonalShapes.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


namespace Leap71
{
    namespace ShapeKernel
    {
        public partial class Uf
        {
            /// <summary>
            /// https://math.stackexchange.com/questions/41940/is-there-an-equation-to-describe-regular-polygons
            /// </summary>
            public enum EPolygon { HEX, QUAD, TRI };

            /// <summary>
            /// Returns the radius at a given polar angle of a regular polygon from custom inputs.
            /// The polygon will sit inside the unit circle and occasionally reach the reference radius = 1.
            /// </summary>
            public static float fGetPolygonRadius(float fPhi, uint nM)
            {
                float dPhi      = fPhi % (2f * MathF.PI / (float)nM);
                float fRadius   = MathF.Cos(MathF.PI / (float)nM) /
                                    MathF.Cos(dPhi - MathF.PI / (float)nM);
                return fRadius;
            }

            /// <summary>
            /// Returns the radius at a given polar angle of a regular polygon from custom inputs.
            /// The polygon will sit inside the unit circle and occasionally reach the reference radius = 1.
            /// The polygon will touch the unit cicle multiple times depending on the symmetry.
            /// The maximum and minimum radius depend on the polygon specified.
            /// </summary>
            public static float fGetPolygonRadius(float fPhi, EPolygon ePolygon)
            {
                if (ePolygon == EPolygon.HEX)
                {
                    return fGetPolygonRadius(fPhi, 6);
                }
                else if (ePolygon == EPolygon.QUAD)
                {
                    return fGetPolygonRadius(fPhi, 4);
                }
                else if (ePolygon == EPolygon.TRI)
                {
                    return fGetPolygonRadius(fPhi, 3);
                }
                else
                {
                    //round
                    return 1f;
                }
            }
        }
    }
}
```

### ShapeKernel/Utilities/RectUtility.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using PicoGK;
using System.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public static class RectUtility
        {
            /// <summary>
            /// Simplifies the creation of a base box along the absolute z-axis.
            /// </summary>
            public static Voxels voxGetBox(float fStartZ, float fEndZ, float fXSize, float fYSize)
            {
                LocalFrame oBoxFrame    = new (new Vector3(0, 0, fStartZ));
                float fLength           = fEndZ - fStartZ;
                BaseBox oBox            = new (oBoxFrame, fLength, fXSize, fYSize);
                return oBox.voxConstruct();
            }

            /// <summary>
            /// Simplifies the creation of a base box with respect to the reference frame's local z-axis.
            /// </summary>
            public static Voxels voxGetBox(LocalFrame oFrame, float fStartZ, float fEndZ, float fXSize, float fYSize)
            {
                LocalFrame oBoxFrame    = oFrame.oTranslate(fStartZ * oFrame.vecGetLocalZ());
                float fLength           = fEndZ - fStartZ;
                BaseBox oBox            = new (oBoxFrame, fLength, fXSize, fYSize);
                return oBox.voxConstruct();
            }
        }
    }
}
```

### ShapeKernel/Utilities/SplineOperations.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;
using PicoGK.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class SplineOperations
        {
            /// <summary>
            /// Returns a list of linearly interpolated vectors between specified start and end.
            /// </summary>
            public static List<Vector3> aGetLinearInterpolation(Vector3 vecStart, Vector3 vecEnd, uint nSamples)
            {
                List<Vector3> aPoints = new List<Vector3>();
                for (int i = 0; i < nSamples; i++)
                {
                    float fRatio = 1f / (float)(nSamples - 1) * i;
                    Vector3 vecPt = vecStart + fRatio * (vecEnd - vecStart);
                    aPoints.Add(vecPt);
                }
                return aPoints;
            }

            /// <summary>
            /// Returns a list points on the surface of the target voxelfield.
            /// The function bClosestPointOnSurface() is applied to each input point. 
            /// </summary>
            public static List<Vector3> aGetSnappedSpline(List<Vector3> aPoints, Voxels voxTarget)
            {
                List<Vector3> aNewPoints = new List<Vector3>();
                for (int i = 0; i < aPoints.Count; i++)
                {
                    voxTarget.bClosestPointOnSurface(aPoints[i], out Vector3 vecSurf);
                    aNewPoints.Add(vecSurf);
                }
                return aNewPoints;
            }

            /// <summary>
            /// Resamples the spline such that all points within have a constant spacing and the number of points match the specified target.
            /// Start and end points remain constant.
            /// </summary>
            public static List<Vector3> aGetReparametrizedSpline(List<Vector3> aPoints, uint nTargetSamples)
            {
                List<float> aLengthsAtIndices   = aGetLengthsAtIndices(aPoints);
                float fSpineLength              = aLengthsAtIndices[aLengthsAtIndices.Count - 1];
                float fTargetStep               = fSpineLength / nTargetSamples;
                List<Vector3> aNewPoints        = new List<Vector3>();

                aNewPoints.Add(aPoints[0]);
                for (int j = 1; j < nTargetSamples; j++)
                {
                    float fTargetLength = fTargetStep * j;
                    int iUpperIndex     = 0;
                    float fUpperLength  = 0;

                    for (iUpperIndex = 1; iUpperIndex < aPoints.Count; iUpperIndex++)
                    {
                        fUpperLength    = aLengthsAtIndices[iUpperIndex];
                        if (fUpperLength >= fTargetLength)
                        {
                            break;
                        }
                    }
                    int iLowerIndex     = iUpperIndex - 1;
                    float fLowerLength  = aLengthsAtIndices[iLowerIndex];
                    float dS            = (fTargetLength - fLowerLength) / (fUpperLength - fLowerLength);

                    Vector3 vecLowerPt  = aPoints[iLowerIndex];
                    Vector3 vecUpperPt  = aPoints[iUpperIndex];

                    //linear interpolation
                    Vector3 vecInterPol = vecLowerPt + dS * (vecUpperPt - vecLowerPt);
                    aNewPoints.Add(vecInterPol);
                }
                aNewPoints.Add(aPoints[aPoints.Count - 1]);
                return aNewPoints;
            }

            /// <summary>
            /// Resamples the spline such that all points within have a constant spacing.
            /// Start and end points remain constant.
            /// </summary>
            public static List<Vector3> aGetReparametrizedSpline(List<Vector3> aPoints, float fTargetSpacing)
            {
                float fTotalLength          = fGetTotalLength(aPoints);
                uint nTargetSamples         = (uint)(MathF.Max(10, fTotalLength / fTargetSpacing));
                List<Vector3> aNewPoints    = aGetReparametrizedSpline(aPoints, nTargetSamples);
                return aNewPoints;
            }

            /// <summary>
            /// Returns a list of values, each value representing the distance of the point at that index along the spline.
            /// </summary>
            public static List<float> aGetLengthsAtIndices(List<Vector3> aPoints)
            {
                List<float> aLengthsAtIndices = new List<float>();

                float fTotalSpineLength = 0;
                aLengthsAtIndices.Add(0);

                for (int i = 1; i < aPoints.Count; i++)
                {
                    Vector3 vecPt1      = aPoints[i - 1];
                    Vector3 vecPt2      = aPoints[i];
                    fTotalSpineLength   += (vecPt2 - vecPt1).Length();
                    aLengthsAtIndices.Add(fTotalSpineLength);
                }
                return aLengthsAtIndices;
            }

            /// <summary>
            /// Calculates the average spacing between points of a spline.
            /// </summary>
            public static float fGetAveragePointSpacing(List<Vector3> aPoints)
            {
                float fTotalLength  = fGetTotalLength(aPoints);
                float fAvgSpacing   = fTotalLength / (aPoints.Count - 1);
                return fAvgSpacing;
            }

            /// <summary>
            /// Calculates the length of a spline.
            /// </summary>
            public static float fGetTotalLength(List<Vector3> aPoints)
            {
                float fTotalSpineLength = 0;

                for (int i = 1; i < aPoints.Count; i++)
                {
                    Vector3 vecPt1      = aPoints[i - 1];
                    Vector3 vecPt2      = aPoints[i];
                    fTotalSpineLength   += (vecPt2 - vecPt1).Length();
                }
                return fTotalSpineLength;
            }

            /// <summary>
            /// Splits the specified list at the index, returns two separate listes witout overlap.
            /// </summary>
            public static (List<Vector3>, List<Vector3>) aSplitLists(List<Vector3> aList, int iFirstIndexOfSecondList)
            {
                List<Vector3> aFirstList    = new List<Vector3>();
                List<Vector3> aSecondList   = new List<Vector3>();
                for (int i = 0; i < aList.Count; i++)
                {
                    if (i < iFirstIndexOfSecondList)
                    {
                        aFirstList.Add(aList[i]);
                    }
                    else
                    {
                        aSecondList.Add(aList[i]);
                    }
                }
                return (aFirstList, aSecondList);
            }

            /// <summary>
            /// Combines multiple lists of points into one list.
            /// </summary>
            public static List<Vector3> aCombineLists(List<List<Vector3>> aLists)
            {
                List<Vector3> aFinalList = new List<Vector3>();
                foreach (List<Vector3> aList in aLists)
                {
                    foreach (Vector3 vecPt in aList)
                    {
                        aFinalList.Add(vecPt);
                    }
                }
                return aFinalList;
            }

            /// <summary>
            /// Rotates the spline around the absolute z-axis by a given angle.
            /// The angle is measured in radian.
            /// </summary>
            public static List<Vector2> aRotateListAroundZ(List<Vector2> aList, float fAngle)
            {
                List<Vector2> aFinalList = new List<Vector2>();
                foreach (Vector2 vecPt in aList)
                {
                    aFinalList.Add(VecOperations.vecRotateAroundZ(vecPt, fAngle));
                }
                return aFinalList;
            }

            /// <summary>
            /// Rotates the spline around the absolute z-axis by a given angle.
            /// The angle is measured in radian.
            /// </summary>
            public static List<Vector3> aRotateListAroundZ(List<Vector3> aList, float fAngle)
            {
                List<Vector3> aFinalList = new List<Vector3>();
                foreach (Vector3 vecPt in aList)
                {
                    aFinalList.Add(VecOperations.vecRotateAroundZ(vecPt, fAngle));
                }
                return aFinalList;
            }

            /// <summary>
            /// Translates the spline by a given vector.
            /// </summary>
            public static List<Vector3> aTranslateList(List<Vector3> aList, Vector3 vecShift)
            {
                List<Vector3> aFinalList = new List<Vector3>();
                foreach (Vector3 vecPt in aList)
                {
                    aFinalList.Add(vecPt + vecShift);
                }
                return aFinalList;
            }

            /// <summary>
            /// Scales the spline by a given factor with respect to the absolute origin.
            /// </summary>
            public static List<Vector3> aScaleList(List<Vector3> aList, float fScale)
            {
                List<Vector3> aFinalList = new List<Vector3>();
                foreach (Vector3 vecPt in aList)
                {
                    aFinalList.Add(vecPt * fScale);
                }
                return aFinalList;
            }

            /// <summary>
            /// Applies nurb-subdivision to smoothen the points witin the list.
            /// Note that the count of the list will change!
            /// Start and end value remain constant.
            /// https://en.wikipedia.org/wiki/Non-uniform_rational_B-spline
            /// </summary>
            public static List<Vector3> aGetNURBSpline(List<Vector3> aControlPoints, uint nSamples)
            {
                ControlPointSpline oBSpline = new (aControlPoints, 2, ControlPointSpline.EEnds.OPEN);
                return oBSpline.aGetPoints(nSamples);
            }
            
            /// <summary>
            /// Samples the specified list with an increment.
            /// Note that the count of the list will change!
            /// Start and end value remain constant.
            /// </summary>
            public static List<Vector3> aOverSampleList(List<Vector3> aList, int iSamplesPerStep)
            {
                List<Vector3> aFinalList = new List<Vector3>();
                for (int i = 1; i < aList.Count; i++)
                {
                    for (int j = 0; j < iSamplesPerStep; j++)
                    {
                        Vector3 vecPt = aList[i - 1] + (float)j / (float)(iSamplesPerStep) * (aList[i] - aList[i - 1]);
                        aFinalList.Add(vecPt);
                    }
                }
                aFinalList.Add(aList[^1]);
                return aFinalList;
            }

            /// <summary>
            /// Samples the specified list with an increment.
            /// Note that the count of the list will change!
            /// Start and end value remain constant.
            /// </summary>
            public static List<Vector3> aSubSampleList(List<Vector3> aList, int iSampleSize)
            {
                List<Vector3> aFinalList = new List<Vector3>();
                int i = 0;
                for (i = 0; i < aList.Count; i += iSampleSize)
                {
                    aFinalList.Add(aList[i]);
                }
                aFinalList.Add(aList[^1]);
                return aFinalList;
            }

            /// <summary>
            /// Rotates and translates the spline onto a new local frame of reference.
            /// </summary>
            public static List<Vector3> aTranslateListOntoFrame(LocalFrame oFrame, List<Vector2> aList)
            {
                List<Vector3> aNewList  = new ();
                foreach (Vector2 vecPt in aList)
                {
                    Vector3 vecNewPt    = VecOperations.vecTranslatePointOntoFrame(oFrame, vecPt.vecAsVector3());
                    aNewList.Add(vecNewPt);
                }
                return aNewList;
            }

            /// <summary>
            /// Rotates and translates the spline onto a new local frame of reference.
            /// </summary>
            public static List<Vector3> aTranslateListOntoFrame(LocalFrame oFrame, List<Vector3> aList)
            {
                List<Vector3> aNewList  = new List<Vector3>();
                foreach (Vector3 vecPt in aList)
                {
                    Vector3 vecNewPt    = VecOperations.vecTranslatePointOntoFrame(oFrame, vecPt);
                    aNewList.Add(vecNewPt);
                }
                return aNewList;
            }

            /// <summary>
            /// Expresses the spline relative to the specified local frame of reference.
            /// </summary>
            public static List<Vector3> aExpressListInFrame(LocalFrame oFrame, List<Vector3> aList)
            {
                List<Vector3> aNewList  = new List<Vector3>();
                foreach (Vector3 vecPt in aList)
                {
                    Vector3 vecNewPt    = VecOperations.vecExpressPointInFrame(oFrame, vecPt);
                    aNewList.Add(vecNewPt);
                }
                return aNewList;
            }

            /// <summary>
            /// Rotates the spline around an arbiary 3D axis by a given angle.
            /// The angle is measured in radian.
            /// </summary>
            public static List<Vector3> aRotateListAroundAxis(List<Vector3> aList, float dPhi, Vector3 vecAxis, Vector3 vecAxisOrigin = new Vector3())
            {
                List<Vector3> aNewList  = new List<Vector3>();
                foreach (Vector3 vecPt in aList)
                {
                    Vector3 vecNewPt    = VecOperations.vecRotateAroundAxis(vecPt, dPhi, vecAxis, vecAxisOrigin);
                    aNewList.Add(vecNewPt);
                }
                return aNewList;
            }

            /// <summary>
            /// Returns the average of all list positions.
            /// </summary>
            public static Vector3 vecGetAverage(List<Vector3> aPoints)
            {
                Vector3 vecCentre = Vector3.Zero;
                for (int i = 0; i < aPoints.Count; i++)
                {
                    Vector3 vecPt = aPoints[i];
                    vecCentre += vecPt;
                }
                vecCentre /= aPoints.Count;
                return vecCentre;
            }

            /// <summary>
            /// Returns the point from the list that is closest to the given start position.
            /// </summary>
            public static Vector3 vecGetClosestPoint(List<Vector3> aPoints, Vector3 vecStart)
            {
                float fMinDist      = float.MaxValue;
                Vector3 vecNear     = Vector3.Zero;

                for (int i = 0; i < aPoints.Count; i++)
                {
                    Vector3 vecPt   = aPoints[i];
                    float fDist     = (vecPt - vecStart).LengthSquared();
                    if (fDist < fMinDist)
                    {
                        fMinDist    = fDist;
                        vecNear     = vecPt;
                    }
                }
                return vecNear;
            }

            /// <summary>
            /// Returns the point from the list that is closest to the given start position.
            /// </summary>
            public static Vector2 vecGetClosestPoint(List<Vector2> aPoints, Vector2 vecStart)
            {
                float fMinDist      = float.MaxValue;
                Vector2 vecNear     = Vector2.Zero;

                for (int i = 0; i < aPoints.Count; i++)
                {
                    Vector2 vecPt   = aPoints[i];
                    float fDist     = (vecPt - vecStart).LengthSquared();
                    if (fDist < fMinDist)
                    {
                        fMinDist    = fDist;
                        vecNear     = vecPt;
                    }
                }
                return vecNear;
            }

            /// <summary>
            /// Returns the distance to the point from the list that is closest to the given start position.
            /// </summary>
            public static float fGetDistanceToClosestPoint(List<Vector3> aPoints, Vector3 vecStart)
            {
                float fMinDist      = float.MaxValue;
                for (int i = 0; i < aPoints.Count; i++)
                {
                    Vector3 vecPt   = aPoints[i];
                    float fDist     = (vecPt - vecStart).LengthSquared();
                    if (fDist < fMinDist)
                    {
                        fMinDist    = fDist;
                    }
                }
                return MathF.Sqrt(fMinDist);
            }

            /// <summary>
            /// Returns the distance to the point from the list that is closest to the given start position.
            /// </summary>
            public static float fGetDistanceToClosestPoint(List<Vector2> aPoints, Vector2 vecStart)
            {
                float fMinDist      = float.MaxValue;
                for (int i = 0; i < aPoints.Count; i++)
                {
                    Vector2 vecPt   = aPoints[i];
                    float fDist     = (vecPt - vecStart).LengthSquared();
                    if (fDist < fMinDist)
                    {
                        fMinDist    = fDist;
                    }
                }
                return MathF.Sqrt(fMinDist);
            }

            /// <summary>
            /// Returns a list of points that make up centres if the input points were clustered by the given range.
            /// All input points that are within the clustering range to an already existing point will be skipped.
            /// </summary>
            public static List<Vector3> aGetClusteredPoints(List<Vector3> aPoints, float fClusteringRange)
            {
                float fDist                     = fClusteringRange * fClusteringRange;
                List<Vector3> aClusteredPoints  = new List<Vector3>() { aPoints[0] };

                for (int i = 1; i < aPoints.Count; i++)
                {
                    //check it point is in range of existing cluster
                    Vector3 vecPt   = aPoints[i];
                    Vector3 vecNear = vecGetClosestPoint(aClusteredPoints, vecPt);
                    if ((vecNear - vecPt).LengthSquared() > fDist)
                    {
                        aClusteredPoints.Add(vecPt);
                    }
                }
                return aClusteredPoints;
            }
        }
    }
}
```

### ShapeKernel/Utilities/SuperShapes.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


namespace Leap71
{
    namespace ShapeKernel
    {
        public partial class Uf
        {
            /// <summary>
            /// http://paulbourke.net/geometry/supershape/
            /// https://en.wikipedia.org/wiki/Superformula
            /// </summary>
            public enum ESuperShape { ROUND, HEX, QUAD, TRI };

            /// <summary>
            /// Returns the radius at a given polar angle of a supershape from custom inputs.
            /// The supershape has a reference radius = 1.
            /// </summary>
            public static float fGetSuperShapeRadius(float fPhi, float fM, float fN1, float fN2, float fN3)
            {
                double dA       = Math.Pow(Math.Abs(Math.Cos(0.25f * fM * fPhi)), fN2);
                double dB       = Math.Pow(Math.Abs(Math.Sin(0.25f * fM * fPhi)), fN3);
                float fRadius   = (float)Math.Pow(dA + dB, -(1 / fN1));
                return fRadius;
            }

            /// <summary>
            /// Returns the radius at a given polar angle of a supershape from preset inputs.
            /// The supershape has a reference radius = 1.
            /// The supershape will touch the unit cicle multiple times depending on the symmetry.
            /// The maximum and minimum radius depend on the supershape specified.
            /// </summary>
            public static float fGetSuperShapeRadius(float fPhi, ESuperShape eSuperShape)
            {
                if (eSuperShape == ESuperShape.HEX)
                {
                    return fGetSuperShapeRadius(fPhi, 6f, 2f, 1.2f, 1.2f);
                }
                else if (eSuperShape == ESuperShape.QUAD)
                {
                    return fGetSuperShapeRadius(fPhi, 4f, 20f, 15f, 15f);
                }
                else if (eSuperShape == ESuperShape.TRI)
                {
                    return fGetSuperShapeRadius(fPhi, 3f, 3f, 4f, 4f);
                }
                else
                {
                    //round
                    return 1f;
                }
            }
        }
    }
}
```

### ShapeKernel/Utilities/UsefulFormulas.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public partial class Uf
        {
            static Random               m_oRandom = new ();
            static ControlPointSpline?  m_oBSpline;


            /// <summary>
            /// Pauses the program execution for a given number of seconds.
            /// </summary>
            public static void Wait(float fSeconds)
            {
                Thread.Sleep((int)(1000 * fSeconds));
            }

            /// <summary>
            /// Returns an intermediate point between the two specified values.
            /// The transition is determined by an open BSpline.
            /// </summary>
            /// <param name="fS"> Current position along a dimension. </param>
            /// <returns></returns>
            public static float fTransFixed(float fValue1, float fValue2, float fS)
            {
                if (m_oBSpline is null)
                {
                    List<Vector3> aControlPoints = new List<Vector3>();
                    aControlPoints.Add(new Vector3(0, 0, 0.0f));
                    aControlPoints.Add(new Vector3(0, 0, 0.5f));
                    aControlPoints.Add(new Vector3(1, 0, 0.5f));
                    aControlPoints.Add(new Vector3(1, 0, 1.0f));
                    m_oBSpline = new ControlPointSpline(aControlPoints);
                }
                Vector3 vecPt   = m_oBSpline.vecGetPointAt(fS);
                float fRatio    = vecPt.X;
                float fValue    = fValue1 + fRatio * (fValue2 - fValue1);
                return fValue;
            }

            /// <summary>
            /// Returns a smoothly interpolated point between the two specified points.
            /// The transition is determined by an open BSpline.
            /// The start and end point will be fixed.
            /// </summary>
            public static Vector3 vecTransFixed(Vector3 vecPt1, Vector3 vecPt2, float fS)
            {
                Vector3 vecPt = fTransFixed(vecPt1.X, vecPt2.X, fS) * Vector3.UnitX +
                                fTransFixed(vecPt1.Y, vecPt2.Y, fS) * Vector3.UnitY +
                                fTransFixed(vecPt1.Z, vecPt2.Z, fS) * Vector3.UnitZ;
                return vecPt;
            }

            /// <summary>
            /// https://www.j-raedler.de/2010/10/smooth-transition-between-functions-with-tanh/
            /// </summary>
            static float fGetNormalizedTangensHyperbolicus(float fS, float fTransitionS, float fSmooth)
            {
                float fValue = (float)(0.5 + 0.5 * Math.Tanh((fS - fTransitionS) / fSmooth));
                return fValue;
            }

            /// <summary>
            /// Returns an intermediate point between the two specified values.
            /// The transition is determined by a smooth tanh function.
            /// </summary>
            /// <param name="fS"> Current position along a dimension. </param>
            /// <param name="fTransitionS"> Position of transition. </param>
            /// <param name="fSmooth"> Smoothness of transition. The lower the value, the sharper the transition and the shorter the transition interval. </param>
            /// <returns></returns>
            public static float fTransSmooth(float fValue1, float fValue2, float fS, float fTransitionS, float fSmooth)
            {
                float fValue =  fValue1 * (1 - fGetNormalizedTangensHyperbolicus(fS, fTransitionS, fSmooth)) +
                                fValue2 * (fGetNormalizedTangensHyperbolicus(fS, fTransitionS, fSmooth));
                return fValue;
            }

            /// <summary>
            /// Returns an intermediate point between the two specified vectors.
            /// The transition is determined by a smooth tanh function.
            /// </summary>
            /// <param name="fS"> Current position along a dimension. </param>
            /// <param name="fTransitionS"> Position of transition. </param>
            /// <param name="fSmooth"> Smoothness of transition. The lower the value, the sharper the transition and the shorter the transition interval. </param>
            /// <returns></returns>
            public static Vector3 vecTransSmooth(Vector3 vecPt1, Vector3 vecPt2, float fS, float fTransitionS, float fSmooth)
            {
                Vector3 vecPt =  vecPt1 * (1 - fGetNormalizedTangensHyperbolicus(fS, fTransitionS, fSmooth)) +
                                 vecPt2 * (fGetNormalizedTangensHyperbolicus(fS, fTransitionS, fSmooth));
                return vecPt;
            }

            [Obsolete("Use float.Clamp() instead")]
            /// <summary>
            /// Clips a value at min and max limits.
            /// </summary>
            public static float fLimitValue(float fValue, float fMin, float fMax)
            {
                fValue = MathF.Min(fValue, fMax);
                fValue = MathF.Max(fValue, fMin);
                return fValue;
            }

            /// <summary>
            /// Returns a random sample according to the specified gauss distribution.
            /// Mean±1 SD contains 68.2% of all values.
            /// Mean±2 SD contains 95.5% of all values.
            /// Mean±3 SD contains 99.7% of all values.
            /// This randomness is not reproducable.
            /// https://gist.github.com/tansey/1444070
            /// </summary>
            public static float fGetRandomGaussian(float fMean, float fStdDev)
            {
                double dX1      = 1 - m_oRandom.NextDouble();
                double dX2      = 1 - m_oRandom.NextDouble();
                double dY1      = Math.Sqrt(-2.0 * Math.Log(dX1)) * Math.Cos(2.0 * Math.PI * dX2);
                float fValue    = (float)dY1 * fStdDev + fMean;
                return fValue;
            }

            /// <summary>
            /// Returns a random sample according to the specified gauss distribution.
            /// Mean±1 SD contains 68.2% of all values.
            /// Mean±2 SD contains 95.5% of all values.
            /// Mean±3 SD contains 99.7% of all values.
            /// This randomness can be made reproducable by passing custom randomness with a seed.
            /// https://gist.github.com/tansey/1444070
            /// </summary>
            public static float fGetRandomGaussian(float fMean, float fStdDev, Random oRandom)
            {
                double dX1      = 1 - oRandom.NextDouble();
                double dX2      = 1 - oRandom.NextDouble();
                double dY1      = Math.Sqrt(-2.0 * Math.Log(dX1)) * Math.Cos(2.0 * Math.PI * dX2);
                float fValue    = (float)dY1 * fStdDev + fMean;
                return fValue;
            }

            /// <summary>
            /// Renturns a random sample according to a linear propability distribution.
            /// This randomness is not reproducable.
            /// </summary>
            public static float fGetRandomLinear(float fMin, float fMax)
            {
                float fValue = (float)(fMin + (fMax - fMin) * m_oRandom.NextDouble());
                return fValue;
            }

            /// <summary>
            /// Renturns a random sample according to a linear propability distribution.
            /// This randomness can be made reproducable by passing custom randomness with a seed.
            /// </summary>
            public static float fGetRandomLinear(float fMin, float fMax, Random oRandom)
            {
                float fValue = (float)(fMin + (fMax - fMin) * oRandom.NextDouble());
                return fValue;
            }

            /// <summary>
            /// Renturns a random boolean value according to a linear propability distribution.
            /// This randomness is not reproducable.
            /// </summary>
            public static bool bGetRandomBool()
            {
                float fValue = (float)m_oRandom.NextDouble();
                if (fValue > 0.5f)
                {
                    return true;
                }
                else
                {
                    return false;
                }
            }

            /// <summary>
            /// Renturns a random boolean value according to a linear propability distribution.
            /// This randomness can be made reproducable by passing custom randomness with a seed.
            /// </summary>
            public static bool bGetRandomBool(Random oRandom)
            {
                float fValue = (float)oRandom.NextDouble();
                if (fValue > 0.5f)
                {
                    return true;
                }
                else
                {
                    return false;
                }
            }

            /// <summary>
            /// Distributes points within a given 2D outer radius according to the fibonacci sequence.
            /// https://medium.com/@vagnerseibert/distributing-points-on-a-sphere-6b593cc05b42
            /// </summary>
            public static List<Vector3> aGetFibonacciCirlePoints(float fOuterRadius, uint nSamples)
            {
                List<Vector3> aPoints = new List<Vector3>();
                for (int i = 0; i < nSamples; i++)
                {
                    float fK        = i + 0.5f;
                    float fR        = MathF.Sqrt((fK) / (float)nSamples);
                    float fPhi      = MathF.PI * (1 + MathF.Sqrt(5f)) * fK;
                    float fX        = fR * fOuterRadius * MathF.Cos(fPhi);
                    float fY        = fR * fOuterRadius * MathF.Sin(fPhi);
                    Vector3 vecPt   = new Vector3(fX, fY, 0f);
                    aPoints.Add(vecPt);
                }
                return aPoints;
            }

            /// <summary>
            /// Distributes points on the surface of a 3D sphere (with outer radius) according to the fibonacci sequence.
            /// https://medium.com/@vagnerseibert/distributing-points-on-a-sphere-6b593cc05b42
            /// </summary>
            public static List<Vector3> aGetFibonacciSpherePoints(float fOuterRadius, uint nSamples)
            {
                List<Vector3> aPoints = new List<Vector3>();
                for (int i = 0; i < nSamples; i++)
                {
                    float fK        = i + 0.5f;
                    float fPhi      = MathF.Acos(1f - 2f * fK / (float)nSamples);
                    float fTheta    = MathF.PI * (1 + MathF.Sqrt(5f)) * fK;
                    float fX        = fOuterRadius * MathF.Cos(fTheta) * MathF.Sin(fPhi);
                    float fY        = fOuterRadius * MathF.Sin(fTheta) * MathF.Sin(fPhi);
                    float fZ        = fOuterRadius * MathF.Cos(fPhi);
                    Vector3 vecPt   = new Vector3(fX, fY, fZ);
                    aPoints.Add(vecPt);
                }
                return aPoints;
            }
        }
    }
}
```

### ShapeKernel/Utilities/VecOperations.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;
using PicoGK.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public static class VecOperations
        {
            /// <summary>
            /// Returns the planar radius (XY) of the point with respect to the Z axis on origin.
            /// </summary>
            public static float R(this Vector3 vecPt)
            {
                return fGetRadius(vecPt);
            }

            [Obsolete("Use vec.vecSafeNormalized or vec.vecNormalized (throws when length is 0) instead")]
            /// <summary>
            /// Sets the vector's length to 1.
            /// </summary>
            public static Vector3 Normalize(this Vector3 vecA)
            {
                return vecA.vecSafeNormalized();
            }

            [Obsolete("Use vec.vecAsVector3 instead")]
            /// <summary>
            /// Adds z-dimension the flat vector.
            /// </summary>
            public static Vector3 ConvertTo3D(this Vector2 vecFlat, float fZ = 0)
            {
                return vecFlat.vecAsVector3(fZ);
            }

            [Obsolete("Use vec.vecStripZ instead")]
            /// <summary>
            /// Removes z-dimension from vector.
            /// The information about the z-value will be lost.
            /// </summary>
            public static Vector2 ConvertTo2D(this Vector3 vecA)
            {
                return vecA.vecStripZ();
            }

            /// <summary>
            /// Returns the carthesian coordinates of a point specified in cylindrical coordinates.
            /// The angle is measured in radian.
            /// </summary>
            public static Vector3 vecGetCylPoint(float fRadius, float fPhi, float fZ)
            {
                float fX        = fRadius * MathF.Cos(fPhi);
                float fY        = fRadius * MathF.Sin(fPhi);
                Vector3 vecPt   = new Vector3(fX, fY, fZ);
                return vecPt;
            }

            /// <summary>
            /// Returns the carthesian coordinates of a point specified in spherical coordinates.
            /// All angles are measured in radian.
            /// </summary>
            public static Vector3 vecGetSphPoint(float fRadius, float fPhi, float fTheta)
            {
                float fX        = fRadius * MathF.Cos(fPhi) * MathF.Cos(fTheta);
                float fY        = fRadius * MathF.Sin(fPhi) * MathF.Cos(fTheta);
                float fZ        = fRadius * MathF.Sin(fTheta);
                Vector3 vecPt   = new Vector3(fX, fY, fZ);
                return vecPt;
            }

            /// <summary>
            /// Returns the 2D planar radius of a point with respect to the absolute z-axis.
            /// </summary>
            public static float fGetRadius(Vector2 vecPt)
            {
                float fRadius = MathF.Sqrt(vecPt.X * vecPt.X + vecPt.Y * vecPt.Y);
                return fRadius;
            }

            /// <summary>
            /// Returns the 2D planar radius of a point with respect to the absolute z-axis.
            /// </summary>
            public static float fGetRadius(Vector3 vecPt)
            {
                float fRadius = MathF.Sqrt(vecPt.X * vecPt.X + vecPt.Y * vecPt.Y);
                return fRadius;
            }

            /// <summary>
            /// Returns the 2D planar polar angle of a point with respect to the absolute z-axis.
            /// Cylindrical coordinate system.
            /// The angle is measured in radian.
            /// </summary>
            public static float fGetPhi(Vector2 vecPt)
            {
                float fPhi = MathF.Atan2(vecPt.Y, vecPt.X);
                return fPhi;
            }

            /// <summary>
            /// Returns the 2D planar polar angle of a point with respect to the absolute z-axis.
            /// Cylindrical coordinate system.
            /// The angle is measured in radian.
            /// </summary>
            public static float fGetPhi(Vector3 vecPt)
            {
                float fPhi = MathF.Atan2(vecPt.Y, vecPt.X);
                return fPhi;
            }

            /// <summary>
            /// Returns the azimuthal angle of a point with respect to the absolute z-axis.
            /// Spherical coordinate system.
            /// The angle is measured in radian.
            /// </summary>
            public static float fGetTheta(Vector3 vecPt)
            {
                float fRadius   = fGetRadius(vecPt);
                float fTheta    = MathF.Atan2(vecPt.Z, fRadius);
                return fTheta;
            }

            /// <summary>
            /// Returns a point with the same cylindrical coordinates (z and phi), but with a new radial position.
            /// </summary>
            public static Vector3 vecSetRadius(Vector3 vecPt, float fNewRadius)
            {
                float fZ            = vecPt.Z;
                float fPhi          = fGetPhi(vecPt);
                Vector3 vecNewPt    = vecGetCylPoint(fNewRadius, fPhi, fZ);
                return vecNewPt;
            }

            /// <summary>
            /// Returns a point with the same cylindrical coordinates (z and radius), but with a new polar position.
            /// The angle is measured in radian.
            /// </summary>
            public static Vector2 vecSetPhi(Vector2 vecPt, float fNewPhi)
            {
                float fRadius       = fGetRadius(vecPt);
                Vector2 vecNewPt    = vecGetCylPoint(fRadius, fNewPhi, 0f).vecStripZ();
                return vecNewPt;
            }

            /// <summary>
            /// Returns a point with the same cylindrical coordinates (z and radius), but with a new polar position.
            /// The angle is measured in radian.
            /// </summary>
            public static Vector3 vecSetPhi(Vector3 vecPt, float fNewPhi)
            {
                float fZ            = vecPt.Z;
                float fRadius       = fGetRadius(vecPt);
                Vector3 vecNewPt    = vecGetCylPoint(fRadius, fNewPhi, fZ);
                return vecNewPt;
            }

            /// <summary>
            /// Returns a point with the same coordinates, but with a new height position.
            /// </summary>
            public static Vector3 vecSetZ(Vector3 vecPt, float fNewZ)
            {
                float fRadius       = fGetRadius(vecPt);
                float fPhi          = fGetPhi(vecPt);
                Vector3 vecNewPt    = vecGetCylPoint(fRadius, fPhi, fNewZ);
                return vecNewPt;
            }

            /// <summary>
            /// Returns a point that is radially shifted by dRadius.
            /// </summary>
            public static Vector3 vecUpdateRadius(Vector3 vecPt, float dRadius)
            {
                float fZ            = vecPt.Z;
                float fNewRadius    = fGetRadius(vecPt) + dRadius;
                float fPhi          = fGetPhi(vecPt);
                Vector3 vecNewPt    = vecGetCylPoint(fNewRadius, fPhi, fZ);
                return vecNewPt;
            }

            /// <summary>
            /// Returns a point that is turned around the absolute z-axis by an angle dPhi.
            /// The angle increment is measured in radian.
            /// </summary>
            public static Vector3 vecUpdatePhi(Vector3 vecPt, float dPhi)
            {
                float fZ            = vecPt.Z;
                float fRadius       = fGetRadius(vecPt);
                float fNewPhi       = fGetPhi(vecPt) + dPhi;
                Vector3 vecNewPt    = vecGetCylPoint(fRadius, fNewPhi, fZ);
                return vecNewPt;
            }

            /// <summary>
            /// Returns a point that is vertically shifted by dZ.
            /// </summary>
            public static Vector3 vecUpdateZ(Vector3 vecPt, float dZ)
            {
                float fRadius       = fGetRadius(vecPt);
                float fPhi          = fGetPhi(vecPt);
                float fNewZ         = vecPt.Z + dZ;
                Vector3 vecNewPt    = vecGetCylPoint(fRadius, fPhi, fNewZ);
                return vecNewPt;
            }

            /// <summary>
            /// Returns the normalized, 2D planar radial direction from the absolute z-axis to the specified point.
            /// </summary>
            public static Vector3 vecGetPlanarDir(Vector3 vecPt)
            {
                Vector3 vecDir  = new Vector3(vecPt.X, vecPt.Y, 0);
                vecDir          = vecDir.vecSafeNormalized();
                return vecDir;
            }

            /// <summary>
            /// Returns the same or the flipped vector depending on which option is more aligned with the target direction.
            /// Two vectors are aligned when they point in the same direction.
            /// Two vectors can either be aligned, orthogonal to each other or not aligned.
            /// </summary>
            public static Vector3 vecFlipForAlignment(Vector3 vecDir, Vector3 vecTargetDir)
            {
                if (Vector3.Dot(vecTargetDir, vecDir) >= Vector3.Dot(vecTargetDir, -vecDir))
                {
                    return vecDir;
                }
                else
                {
                    return -vecDir;
                }
            }

            /// <summary>
            /// Returns true if the specified direction is aligned with the target direction.
            /// Two vectors are aligned when they point in the same direction.
            /// Two vectors can either be aligned, orthogonal to each other or not aligned.
            /// </summary>
            public static bool bCheckAlignment(Vector3 vecDir, Vector3 vecTargetDir)
            {
                if (Vector3.Dot(vecTargetDir, vecDir) >= Vector3.Dot(vecTargetDir, -vecDir))
                {
                    return true;
                }
                else
                {
                    return false;
                }
            }

            /// <summary>
            /// Rotates a point around the absolute z-axis.
            /// The axis origin can be customised.
            /// The angle increment is measured in radian.
            /// </summary>
            public static Vector2 vecRotateAroundZ(Vector2 vecPt, float dPhi, Vector2 vecAxisOrigin = new Vector2())
            {
                Vector2 vecDiff     = vecPt - vecAxisOrigin;
                float fPhi          = fGetPhi(vecDiff);
                Vector2 vecRotDiff  = vecSetPhi(vecDiff, fPhi + dPhi);
                Vector2 vecRotPt    = vecAxisOrigin + vecRotDiff;
                return vecRotPt;
            }

            /// <summary>
            /// Rotates a point around the absolute z-axis.
            /// The axis origin can be customised.
            /// The angle increment is measured in radian.
            /// </summary>
            public static Vector3 vecRotateAroundZ(Vector3 vecPt, float dPhi, Vector3 vecAxisOrigin = new Vector3())
            {
                Vector3 vecDiff     = vecPt - vecAxisOrigin;
                float fPhi          = fGetPhi(vecDiff);
                Vector3 vecRotDiff  = vecSetPhi(vecDiff, fPhi + dPhi);
                Vector3 vecRotPt    = vecAxisOrigin + vecRotDiff;
                return vecRotPt;
            }

            /// <summary>
            /// Returns a arbitary vector that is orthogonal to the specified direction.
            /// </summary>
            public static Vector3 vecGetOrthogonalDir(Vector3 vecDir)
            {
                Vector3 vecNonParallel = Vector3.UnitX;
                if (MathF.Abs(Vector3.Dot(vecDir, vecNonParallel)) > 0.95f)
                {
                    vecNonParallel  = Vector3.UnitY;
                }
                Vector3 vecNormal   = Vector3.Cross(vecDir, vecNonParallel);
                vecNormal           = vecNormal.vecSafeNormalized();
                return vecNormal;
            }

            /// <summary>
            /// Returns the minimum angle between to 3D vectors.
            /// The angle is measured in radian.
            /// </summary>
            public static float fGetAngleBetween(Vector3 vecA, Vector3 vecB)
            {
                vecA         = vecA.vecSafeNormalized();
                vecB         = vecB.vecSafeNormalized();
                float fDot   = float.Clamp(Vector3.Dot(vecA, vecB), -1, 1);
                float fTheta = MathF.Acos(fDot);

                if (float.IsNaN(fTheta) &&
                    (MathF.Abs(fDot) == 1))
                {
                    return MathF.PI;
                }
                return fTheta;
            }

            /// <summary>
            /// Returns the minimum angle between to 2D vectors.
            /// The angle is measured in radian.
            /// </summary>
            public static float fGetAngleBetween(Vector2 vecA, Vector2 vecB)
            {
                vecA         = vecA.vecSafeNormalized();
                vecB         = vecB.vecSafeNormalized();
                float fDot   = float.Clamp(Vector2.Dot(vecA, vecB), -1, 1);
                float fTheta = MathF.Acos(fDot);

                if (float.IsNaN(fTheta) &&
                    (MathF.Abs(fDot) == 1))
                {
                    return MathF.PI;
                }
                return fTheta;
            }

            /// <summary>
            /// Returns the minimum, signed angle between to 3D vectors.
            /// The angle is measured in radian.
            /// The order in which the vectors are specified will influence the rotation sense indicated by the sign.
            /// </summary>
            public static float fGetSignedAngleBetween(Vector3 vecA, Vector3 vecB, Vector3 vecRefNormal)
            {
                const float fError = 1e-20f;

                if (vecA.LengthSquared() < fError || 
                    vecB.LengthSquared() < fError || 
                    vecRefNormal.LengthSquared() < fError)
                {
                    throw new Exception("Vector3 with zero length.");
                }

                vecA                = vecA.vecSafeNormalized();
                vecB                = vecB.vecSafeNormalized();
                vecRefNormal        = vecRefNormal.vecSafeNormalized();
                Vector3 vecNormal   = Vector3.Cross(vecA, vecB);
                vecNormal           = vecFlipForAlignment(vecNormal, vecRefNormal);
                float fTheta        = MathF.Abs(fGetAngleBetween(vecA, vecB));
                float fPosDot       = Vector3.Dot(vecA, vecRotateAroundAxis(vecB, fTheta, vecNormal));
                float fNegDot       = Vector3.Dot(vecA, vecRotateAroundAxis(vecB, -fTheta, vecNormal));

                if (fNegDot > fPosDot)
                {
                    return -fTheta;
                }
                else
                {
                    return fTheta;
                }
            }

            /// <summary>
            /// Rotates a point around a custom axis.
            /// The axis origin can be customised.
            /// The angle increment is measured in radian.
            /// </summary>
            public static Vector3 vecRotateAroundAxis(Vector3 vecPt, float dPhi, Vector3 vecAxis, Vector3? vecAxisOrigin = null)
            {
                Vector3 vecOrigin   = new Vector3();
                if (vecAxisOrigin  != null)
                {
                    vecOrigin = (Vector3)vecAxisOrigin;
                }
                Vector3 vecRel      = vecPt - vecOrigin;
                Quaternion mat      = Quaternion.CreateFromAxisAngle(vecAxis, dPhi);
                Vector3 vecNewRel   = Vector3.Transform(vecRel, mat);
                Vector3 vecNewPt    = vecNewRel + vecOrigin;
                return vecNewPt;
            }

            [Obsolete("Use vec.vecPtWorld(oFrame)instead")]
            /// <summary>
            /// Rotates and translates a point in absolute carthesian coordinates onto the specified local reference frame.
            /// The relative coordinates of the result with respect to the local frame will mach those of the input point in absolute reference.
            /// The absolute coordinated of the result will update depending on the position and orientation of the local frame.
            /// "How would this point look like when it was referenced to a this local frame?".
            /// </summary> 
            public static Vector3 vecTranslatePointOntoFrame(LocalFrame oFrame, Vector3 vecPt)
            {
                Vector3 vecOrigin = oFrame.vecGetPosition();
                Vector3 vecNewPt =
                        vecOrigin +
                        vecPt.X * oFrame.vecGetLocalX() +
                        vecPt.Y * oFrame.vecGetLocalY() +
                        vecPt.Z * oFrame.vecGetLocalZ();
                return vecNewPt;
            }

            [Obsolete("Use vec.vecDirWorld(oFrame)instead")]
            /// <summary>
            /// Rotates and translates a direction in absolute carthesian coordinates onto the specified local reference frame.
            /// The relative coordinates of the result with respect to the local frame will mach those of the input point in absolute reference.
            /// The absolute coordinated of the result will update depending on the position and orientation of the local frame.
            /// "How would this direction look like when it was referenced to a this local frame?".
            /// </summary>
            public static  Vector3 vecTranslateDirectionOntoFrame(LocalFrame oFrame, Vector3 vecDir)
            {
                Vector3 vecPt1      = new Vector3();
                Vector3 vecPt2      = vecPt1 + vecDir;
                vecPt1              = VecOperations.vecTranslatePointOntoFrame(oFrame, vecPt1);
                vecPt2              = VecOperations.vecTranslatePointOntoFrame(oFrame, vecPt2);
                Vector3 vecNewDir   = vecPt2 - vecPt1;
                return vecNewDir;
            }

            [Obsolete("Use vec.vecPtLocal(oFrame)instead")]
            /// <summary>
            /// Returns the relative coordinates expression of an absolute, carthesian point with respect to a given local reference frame.
            /// "How would this point look like when viewed from this local frame?".
            /// </summary>
            public static Vector3 vecExpressPointInFrame(LocalFrame oFrame, Vector3 vecPt)
            {
                vecPt   -= oFrame.vecGetPosition();
                float fX = Vector3.Dot(vecPt, oFrame.vecGetLocalX());
                float fY = Vector3.Dot(vecPt, oFrame.vecGetLocalY());
                float fZ = Vector3.Dot(vecPt, oFrame.vecGetLocalZ());
                Vector3 vecNewPt = new Vector3(fX, fY, fZ);
                return vecNewPt;
            }

            [Obsolete("Use vec.vecDirLocal(oFrame)instead")]
            /// <summary>
            /// Returns the direction of a direct connection between the local frame's z-axis and the specified point.
            /// Similar to the function vecGetPlanarDir, but in an arbitary, 3D reference frame.
            /// </summary>
            public static Vector3 vecGetDirectionToAxis(LocalFrame oFrame, Vector3 vecPt)
            {
                Vector3 vecLocalX = oFrame.vecGetLocalX();
                Vector3 vecLocalY = oFrame.vecGetLocalY();
                Vector3 vecLocalZ = oFrame.vecGetLocalZ();

                vecPt   -= oFrame.vecGetPosition();
                float fX = Vector3.Dot(vecPt, vecLocalX);
                float fY = Vector3.Dot(vecPt, vecLocalY);

                Vector3 vecNewPt =
                    fX * vecLocalX +
                    fY * vecLocalY;

                vecNewPt = vecNewPt.vecSafeNormalized();
                return vecNewPt;
            }

            /// <summary>
            /// Returns the radius between the local frame's z-axis and the specified point.
            /// Similar to the function fGetRadius, but in an arbitary, 3D reference frame.
            /// </summary>
            public static float fGetRadiusToAxis(LocalFrame oFrame, Vector3 vecPt)
            {
                Vector3 vecLocalX = oFrame.vecGetLocalX();
                Vector3 vecLocalY = oFrame.vecGetLocalY();
                Vector3 vecLocalZ = oFrame.vecGetLocalZ();

                vecPt   -= oFrame.vecGetPosition();
                float fX = Vector3.Dot(vecPt, vecLocalX);
                float fY = Vector3.Dot(vecPt, vecLocalY);

                float fRadius = MathF.Sqrt(fX * fX + fY * fY);
                return fRadius;
            }

            /// <summary>
            /// Returns the polar angle between the local frame's z-axis and the specified point.
            /// Similar to the function fGetPhi, but in an arbitary, 3D reference frame.
            /// The angle is measured in radian.
            /// </summary>
            public static float fGetPhiToAxis(LocalFrame oFrame, Vector3 vecPt)
            {
                Vector3 vecLocalX = oFrame.vecGetLocalX();
                Vector3 vecLocalY = oFrame.vecGetLocalY();
                Vector3 vecLocalZ = oFrame.vecGetLocalZ();

                vecPt   -= oFrame.vecGetPosition();
                float fX = Vector3.Dot(vecPt, vecLocalX);
                float fY = Vector3.Dot(vecPt, vecLocalY);

                float fPhi = MathF.Atan2(fY, fX);
                return fPhi;
            }

            [Obsolete("Use Vector3.Lerp(vecPt1, vecPt2, fRatio) instead")]
            /// <summary>
            /// Returns a linearly interpolated point between the two specified points.
            /// </summary>
            public static Vector3 vecLinearInterpolation(Vector3 vecPt1, Vector3 vecPt2, float fRatio)
            {
                Vector3 vecInter = vecPt1 + fRatio * (vecPt2 - vecPt1);
                return vecInter;
            }

            /// <summary>
            /// Returns a cylidrically interpolated point between the two specified points.
            /// </summary>
            public static Vector3 vecCylindricalInterpolation(Vector3 vecPt1, Vector3 vecPt2, float fRatio, Vector3 vecAxisOrigin = new Vector3())
            {
                vecAxisOrigin       = vecSetZ(vecAxisOrigin, 0f);
                float dMinAngle     = fGetAngleBetween(vecPt1, vecPt2);

                Vector3 vecSide1    = (vecPt1 - vecAxisOrigin).vecSafeNormalized();
                Vector3 vecSide2    = (vecPt2 - vecAxisOrigin).vecSafeNormalized();
                Vector3 vecNormal   = Vector3.Cross(vecSide1, vecSide2);

                //figure out rotation sense
                float fDistPos      = (vecPt2 - vecRotateAroundZ(vecPt1, dMinAngle)).Length();
                float fDistNeg      = (vecPt2 - vecRotateAroundZ(vecPt1, -dMinAngle)).Length();

                int iSense = 1;
                if (fDistNeg < fDistPos)
                {
                    iSense = -1;
                }

                float fRadius1      = fGetRadius(vecPt1 - vecAxisOrigin);
                float fRadius2      = fGetRadius(vecPt2 - vecAxisOrigin);
                float fInterRadius  = fRadius1 + fRatio * (fRadius2 - fRadius1);

                float fInterZ       = vecPt1.Z + fRatio * (vecPt2.Z - vecPt1.Z);

                Vector3 vecInter    = vecRotateAroundZ(fInterRadius * vecSide1, iSense * fRatio * dMinAngle);
                vecInter            = vecSetZ(vecInter, fInterZ);
                return vecInter + vecAxisOrigin;
            }

            /// <summary>
            /// Returns a spherically interpolated point between the two specified points.
            /// </summary>
            public static Vector3 vecSphericalInterpolation(Vector3 vecPt1, Vector3 vecPt2, float fRatio, Vector3 vecAxisOrigin = new Vector3())
            {
                float dMinAngle     = fGetAngleBetween(vecPt1, vecPt2);

                Vector3 vecSide1    = (vecPt1 - vecAxisOrigin).vecSafeNormalized();
                Vector3 vecSide2    = (vecPt2 - vecAxisOrigin).vecSafeNormalized();
                Vector3 vecNormal   = Vector3.Cross(vecSide1, vecSide2);

                //figure out rotation sense
                float fDistPos      = (vecPt2 - vecRotateAroundAxis(vecPt1, dMinAngle, vecNormal)).Length();
                float fDistNeg      = (vecPt2 - vecRotateAroundAxis(vecPt1, -dMinAngle, vecNormal)).Length();

                int iSense = 1;
                if (fDistNeg < fDistPos)
                {
                    iSense = -1;
                }

                float fRadius1      = (vecPt1 - vecAxisOrigin).Length();
                float fRadius2      = (vecPt2 - vecAxisOrigin).Length();
                float fInterRadius  = fRadius1 + fRatio * (fRadius2 - fRadius1);

                Vector3 vecInter    = vecRotateAroundAxis(fInterRadius * vecSide1, iSense * fRatio * dMinAngle, vecNormal);
                return vecInter + vecAxisOrigin;
            }
        }
    }
}
```

### ShapeKernel/Visualizations/ColorPalette.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public partial class Cp
        {
            public static readonly ColorFloat clrBlack        = new ColorFloat("#000000");
            public static readonly ColorFloat clrRacingGreen  = new ColorFloat("#065c35");
            public static readonly ColorFloat clrGreen        = new ColorFloat("#00b800");
            public static readonly ColorFloat clrBillie       = new ColorFloat("#02f70b");
            public static readonly ColorFloat clrLemongrass   = new ColorFloat("#b8e031");
            public static readonly ColorFloat clrYellow       = new ColorFloat("#fcd808");
            public static readonly ColorFloat clrWarning      = new ColorFloat("#fc6608");
            public static readonly ColorFloat clrRed          = new ColorFloat("#ff0000");
            public static readonly ColorFloat clrRuby         = new ColorFloat("#b0002c");
            public static readonly ColorFloat clrOrchid       = new ColorFloat("#c72483");
            public static readonly ColorFloat clrPitaya       = new ColorFloat("#fa2a88");
            public static readonly ColorFloat clrBubblegum    = new ColorFloat("#ff66ce");
            public static readonly ColorFloat clrLavender     = new ColorFloat("#c966ff");
            public static readonly ColorFloat clrGray         = new ColorFloat("#bdbdbd");
            public static readonly ColorFloat clrRock         = new ColorFloat("#6b7178");
            public static readonly ColorFloat clrCrystal      = new ColorFloat("#0cc1f7");
            public static readonly ColorFloat clrFrozen       = new ColorFloat("#6de2fc");
            public static readonly ColorFloat clrBlueberry    = new ColorFloat("#4f0dbf");
            public static readonly ColorFloat clrBlue         = new ColorFloat("#4287f5");
            public static readonly ColorFloat clrToothpaste   = new ColorFloat("#25e6c9");


            /// <summary>
            /// Returns a random color that is always consistent for the specified index.
            /// Color is random but reproducible.
            /// </summary>
            public static ColorFloat clrRandom(int j)
            {
                Random oRand    = new Random(j);
                return ColorFloat.clrRandom(oRand);
            }

            /// <summary>
            /// Returns a random color the is not reproducible.
            /// </summary>
            public static ColorFloat clrRandom()
            {
                return ColorFloat.clrRandom();
            }
        }
    }
}
```

### ShapeKernel/Visualizations/ColorScale2D.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public interface IColorScale
        {
            public ColorFloat   clrGetColor(float fValue);
            public float        fGetMinValue();
            public float        fGetMaxValue();
        }

        public class LinearColorScale2D : IColorScale
        {
            protected float             m_fMinValue;
            protected float             m_fMaxValue;
            protected ColorFloat        m_clrMin;
            protected ColorFloat        m_clrMax;

            /// <summary>
            /// 2D color scale that interpolates linerly between min and max color on RGB basis.
            /// </summary>
            public LinearColorScale2D(  ColorFloat clrMin,
                                        ColorFloat clrMax,
                                        float fMinValue,
                                        float fMaxValue)
            {
                m_fMaxValue         = fMaxValue;
                m_fMinValue         = fMinValue;
                m_clrMin            = clrMin;
                m_clrMax            = clrMax;
            }

            public float fGetMinValue()
            {
                return m_fMinValue;
            }

            public float fGetMaxValue()
            {
                return m_fMaxValue;
            }

            protected virtual float fGetInterpolated(float fValue1, float fValue2, float fValue)
            {
                float fRatio = (fValue - m_fMinValue) / (m_fMaxValue - m_fMinValue);
                return fValue1 + fRatio * (fValue2 - fValue1);
            }

            public ColorFloat clrGetColor(float fValue)
            {
                fValue              = float.Clamp(fValue, m_fMinValue, m_fMaxValue);
                int R               = (int)(255f * fGetInterpolated(m_clrMin.R, m_clrMax.R, fValue));
                int G               = (int)(255f * fGetInterpolated(m_clrMin.G, m_clrMax.G, fValue));
                int B               = (int)(255f * fGetInterpolated(m_clrMin.B, m_clrMax.B, fValue));
                string strColor     = "#" +
                                        R.ToString("X2") +
                                        G.ToString("X2") +
                                        B.ToString("X2");
                ColorFloat clr      = new ColorFloat(strColor);
                return clr;
            }
        }

        public class SmoothColorScale2D : LinearColorScale2D
        {
            /// <summary>
            /// 2D color scale that interpolates smoothly between min and max color on RGB basis.
            /// Uses Uf.fTransFixed() interpolation internally.
            /// </summary>
            public SmoothColorScale2D(  ColorFloat clrMin,
                                        ColorFloat clrMax,
                                        float fMinValue,
                                        float fMaxValue) : base (clrMin, clrMax, fMinValue, fMaxValue) { }

            protected override float fGetInterpolated(float fValue1, float fValue2, float fValue)
            {
                float fRatio = (fValue - m_fMinValue) / (m_fMaxValue - m_fMinValue);
                return Uf.fTransFixed(fValue1, fValue2, fRatio);
            }
        }

        public class CustomColorScale2D : LinearColorScale2D
        {
            protected float m_fSmoothness;
            protected float m_fTransition;

            /// <summary>
            /// 2D color scale that interpolates smoothly between min and max color on RGB basis.
            /// Uses Uf.fTransSmooth() interpolation internally.
            /// Transition value and smoothness can be customized.
            /// </summary>
            public CustomColorScale2D(  ColorFloat clrMin,
                                        ColorFloat clrMax,
                                        float fMinValue,
                                        float fMaxValue,
                                        float fTransition,
                                        float fSmoothness) : base (clrMin, clrMax, fMinValue, fMaxValue)
            {
                m_fTransition = fTransition;
                m_fSmoothness = fSmoothness;
            }

            protected override float fGetInterpolated(float fValue1, float fValue2, float fValue)
            {
                return Uf.fTransSmooth(fValue1, fValue2, fValue, m_fTransition, m_fSmoothness);
            }
        }
    }
}
```

### ShapeKernel/Visualizations/ColorScale3D.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class ColorScale3D : IColorScale
        {
            List<Vector3>    m_aSmoothRGBList;
            float            m_fMinValue;
            float            m_fMaxValue;


            /// <summary>
            /// 3D color scale that interpolates smoothly between the sequence of colors in the specified spectrum.
            /// </summary>
            public ColorScale3D(    ISpectrum xSpectrum,
                                    float fMinValue,
                                    float fMaxValue)
            {
                m_fMaxValue         = fMaxValue;
                m_fMinValue         = fMinValue;
                m_aSmoothRGBList    = SplineOperations.aGetNURBSpline(xSpectrum.aGetRawRGBList(), 500);
                m_aSmoothRGBList    = SplineOperations.aGetReparametrizedSpline(m_aSmoothRGBList, 500);
            }

            public float fGetMinValue()
            {
                return m_fMinValue;
            }

            public float fGetMaxValue()
            {
                return m_fMaxValue;
            }

            public ColorFloat clrGetColor(float fValue)
            {
                fValue              = float.Clamp(fValue, m_fMinValue, m_fMaxValue);
                float fLengthRatio  = (fValue - m_fMinValue) / (m_fMaxValue - m_fMinValue);
                Vector3 vecRGB      = m_aSmoothRGBList[(int)(fLengthRatio * (m_aSmoothRGBList.Count - 1))];
                int R               = (int)(vecRGB.X);
                int G               = (int)(vecRGB.Y);
                int B               = (int)(vecRGB.Z);
                string strColor     = "#" +
                                        R.ToString("X2") +
                                        G.ToString("X2") +
                                        B.ToString("X2");
                ColorFloat clr      = new ColorFloat(strColor);
                return clr;
            }
        }
    }
}
```

### ShapeKernel/Visualizations/MeshPainter.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
	namespace ShapeKernel
	{
        using static BaseShape;

        public class MeshPainter
		{
            public delegate float ColorScaleFunc(Vector3 vecA, Vector3 vecB, Vector3 vecC);

            /// <summary>
            /// Divides the specified mesh into multiple sub-meshes from triangles that share a similar overhang angle.
            /// Each sub-mesh is previewed in a color that represents its overhang angle on the specified color scale.
            /// Overhang angles are specified in deg. Zero deg is vertical (minimum), 90 deg is horizontal (maximum).
            /// </summary>
            public static void PreviewOverhangAngle(        Mesh            oMesh,
                                                            IColorScale     xScale,
                                                            bool            bShowOnlyDownFacing,
                                                            uint            nClasses = 30)
            {
                Mesh[] aSubMeshes   = new Mesh[nClasses];
                float fMinAngle     = xScale.fGetMinValue();
                float fMaxAngle     = xScale.fGetMaxValue();
                float dAngle        = (fMaxAngle - fMinAngle) / (nClasses - 1f);

                for (int i = 0; i < nClasses; i++)
                {
                    aSubMeshes[i] = new Mesh();
                }

                uint nNumberOfTriangles  = (uint)oMesh.nTriangleCount();
                for (int i = 0; i < nNumberOfTriangles; i++)
                {
                    oMesh.GetTriangle(i, out Vector3 vecA, out Vector3 vecB, out Vector3 vecC);
                    Vector3 vecNormal    = Vector3.Cross(vecA - vecB, vecC - vecB).Normalize();

                    float dR             = MathF.Sqrt(vecNormal.X * vecNormal.X + vecNormal.Y * vecNormal.Y);
                    float dZ             = MathF.Abs(vecNormal.Z);
                    float fOverhangAngle = MathF.Atan2(dZ, dR) / MathF.PI * 180f;
                    fOverhangAngle       = float.Clamp(fOverhangAngle, 0f, 90f);

                    // only show downfacing
                    if (bShowOnlyDownFacing == true &&
                        vecNormal.Z < 0)
                    {
                        fOverhangAngle = 0;
                    }

                    float fRatio         = (fOverhangAngle - fMinAngle) / (fMaxAngle - fMinAngle);

                    uint nSubMeshIndex   = (uint)(fRatio * (nClasses - 1));
                    aSubMeshes[nSubMeshIndex].nAddTriangle(vecA, vecB, vecC);
                }

                for (int i = 0; i < nClasses; i++)
                {
                    ColorFloat clr      = xScale.clrGetColor(fMinAngle + (i * dAngle));
                    try
                    {
                        Sh.PreviewMesh(aSubMeshes[i], clr);
                    }
                    catch { }
                }
            }

            /// <summary>
            /// Divides the specified mesh into multiple sub-meshes from triangles that share a similar custom properties.
            /// Each sub-mesh is previewed in a color that represents its custom property on the specified color scale.
            /// </summary>
            public static void PreviewCustomProperty(       Mesh            oMesh,
                                                            IColorScale     xScale,
                                                            ColorScaleFunc  oColorFunc,
                                                            uint            nClasses = 30)
            {
                Mesh[] aSubMeshes   = new Mesh[nClasses];
                float fMinValue     = xScale.fGetMinValue();
                float fMaxValue     = xScale.fGetMaxValue();
                float dValue        = (fMaxValue - fMinValue) / (nClasses - 1f);

                for (int i = 0; i < nClasses; i++)
                {
                    aSubMeshes[i] = new Mesh();
                }

                uint nNumberOfTriangles = (uint)oMesh.nTriangleCount();
                for (int i = 0; i < nNumberOfTriangles; i++)
                {
                    oMesh.GetTriangle(i, out Vector3 vecA, out Vector3 vecB, out Vector3 vecC);

                    float fValue        = oColorFunc(vecA, vecB, vecC);
                    float fRatio        = (fValue - fMinValue) / (fMaxValue - fMinValue);
                    fRatio              = float.Clamp(fRatio, 0f, 1f);

                    uint nSubMeshIndex  = (uint)(fRatio * (nClasses - 1));
                    aSubMeshes[nSubMeshIndex].nAddTriangle(vecA, vecB, vecC);
                }


                for (int i = 0; i < nClasses; i++)
                {
                    ColorFloat clr      = xScale.clrGetColor(fMinValue + (i * dValue));
                    try
                    {
                        Mesh mshSub         = aSubMeshes[i];
                        int nTriangleCount  = mshSub.nTriangleCount();
                        int nVertexCount    = mshSub.nVertexCount();

                        if (nTriangleCount == 0) { }
                        else if (nVertexCount == 0) { }
                        else
                        {
                            Sh.PreviewMesh(mshSub, clr);
                        }
                    }
                    catch { }
                }
            }

            /// <summary>
            /// Creates a new mesh that is deformed by the vertex-wise application of the trafo func.
            /// Divides this new mesh into multiple sub-meshes based on old mesh triangles that share a similar custom properties.
            /// Each sub-mesh is previewed in a color that represents its custom property on the specified color scale.
            /// </summary>
            public static void PreviewCustomDeformation(    Mesh                    oMesh,
                                                            IColorScale             xScale,
                                                            ColorScaleFunc          oColorFunc,
                                                            fnVertexTransformation  fnTrafo,
                                                            uint                    nClasses = 30)
            {
                Mesh[] aSubMeshes   = new Mesh[nClasses];
                float fMinValue     = xScale.fGetMinValue();
                float fMaxValue     = xScale.fGetMaxValue();
                float dValue        = (fMaxValue - fMinValue) / (nClasses - 1f);

                for (int i = 0; i < nClasses; i++)
                {
                    aSubMeshes[i] = new Mesh();
                }

                uint nNumberOfTriangles = (uint)oMesh.nTriangleCount();
                for (int i = 0; i < nNumberOfTriangles; i++)
                {
                    oMesh.GetTriangle(i, out Vector3 vecA, out Vector3 vecB, out Vector3 vecC);

                    float fValue        = oColorFunc(vecA, vecB, vecC);
                    float fRatio        = (fValue - fMinValue) / (fMaxValue - fMinValue);
                    fRatio              = float.Clamp(fRatio, 0f, 1f);

                    uint nSubMeshIndex  = (uint)(fRatio * (nClasses - 1));
                    aSubMeshes[nSubMeshIndex].nAddTriangle(vecA, vecB, vecC);
                }

                for (int i = 0; i < nClasses; i++)
                {
                    ColorFloat clr       = xScale.clrGetColor(fMinValue + (i * dValue));
                    try
                    {
                        Mesh msh         = aSubMeshes[i];
                        Mesh mshDeformed = MeshUtility.mshApplyTransformation(msh, fnTrafo);
                        Sh.PreviewMesh(mshDeformed, clr);
                    }
                    catch { }
                }
            }
        }
	}
}
```

### ShapeKernel/Visualizations/RainboxSpectrum.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using System.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public interface ISpectrum
        {
            public List<Vector3> aGetRawRGBList();
        }

        public class RainboxSpectrum : ISpectrum
        {
            public List<Vector3> aGetRawRGBList()
            {
                List<Vector3> aRGBList = new List<Vector3>();
                aRGBList.Add(new Vector3(0, 0, 255));                           // blue
                aRGBList.Add(new Vector3(0, 255, 0));                           // green
                aRGBList.Add(new Vector3(255, 255, 0));                         // yellow
                aRGBList.Add(new Vector3(255, 130, 0));                         // orange
                aRGBList.Add(new Vector3(255, 0, 0));                           // red
                return aRGBList;
            }
        }
    }
}
```

### ShapeKernel/Visualizations/RotationAnimator.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//


using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class RotationAnimator
        {
            /// <summary>
            /// When this class is instantiated, it starts to rotate the view port against
            /// the objects currently on display. This can be used for screen-capturing videos.
            /// The animation will go on indefinitely.
            /// </summary>
            public RotationAnimator()
            {
                while (true)
                {
                    Uf.Wait(0.01f);
                    Do();
                }
            }

            public void Do()
            {
                //float fElevation    = Library.oViewer().m_fElevation;
                //float fCurrentOrbit = Library.oViewer().m_fOrbit;
                //float fNextOrbit    = fCurrentOrbit + 0.5f;
                //Library.oViewer().SetViewAngles(fNextOrbit, fElevation);
            }
        }
    }
}
```

### ShapeKernel/Visualizations/ShPreviewFunctions_I.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//

using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public partial class Sh
        {
            public static uint nNumberOfGroups = 0;
            
            public static int PreviewMesh(
                Mesh        oMesh,
                ColorFloat  clrColor,
                float       fTransparency   = 0.9f,
                float       fMetallic       = 0.4f,
                float       fRoughness      = 0.7f)
            {
                int iNextGroupId    = (int)nNumberOfGroups;
                ColorFloat clr      = new ColorFloat(clrColor, fTransparency);
                Library.oViewer().SetGroupMaterial(iNextGroupId,
                                            clr,
                                            fMetallic,
                                            fRoughness);
                Library.oViewer().Add(oMesh, iNextGroupId);
                nNumberOfGroups++;
                return (int)(nNumberOfGroups - 1);
            }

            public static int PreviewVoxels(
                Voxels      oVoxels,
                ColorFloat  clrColor,
                float       fTransparency   = 0.9f,
                float       fMetallic       = 0.4f,
                float       fRoughness      = 0.7f)
            {
                int iNextGroupId    = (int)nNumberOfGroups;
                ColorFloat clr      = new ColorFloat(clrColor, fTransparency);
                Library.oViewer().SetGroupMaterial(iNextGroupId,
                                            clr,
                                            fMetallic,
                                            fRoughness);
                Library.oViewer().Add(oVoxels, iNextGroupId);
                nNumberOfGroups++;
                return (int)(nNumberOfGroups - 1);
            }

            public static int PreviewLattice(
                Lattice     oLattice,
                ColorFloat  clrColor,
                float       fTransparency   = 0.9f,
                float       fMetallic       = 0.4f,
                float       fRoughness      = 0.7f)
            {
                int iNextGroupId    = (int)nNumberOfGroups;
                ColorFloat clr      = new ColorFloat(clrColor, fTransparency);
                Library.oViewer().SetGroupMaterial(iNextGroupId,
                                            clr,
                                            fMetallic,
                                            fRoughness);
                Voxels oVoxels = new Voxels(oLattice);
                Library.oViewer().Add(oVoxels, iNextGroupId);
                nNumberOfGroups++;
                return (int)(nNumberOfGroups - 1);
            }

            public static void PreviewPoint(
                Vector3     vecPt,
                float       fBeam,
                ColorFloat  clrColor,
                float       fTransparency   = 0.9f,
                float       fMetallic       = 0.4f,
                float       fRoughness      = 0.7f)
            {
                BaseSphere oBall = new (new (vecPt), fBeam);
                PreviewMesh(oBall.mshConstruct(), clrColor, fTransparency, fMetallic, fRoughness);
            }

            public static void PreviewBeam(
                Vector3     vecPt1,
                float       fBeam1,
                Vector3     vecPt2,
                float       fBeam2,
                ColorFloat  clrColor,
                float       fTransparency   = 0.9f,
                float       fMetallic       = 0.4f,
                float       fRoughness      = 0.7f)
            {
                Lattice oLattice = new Lattice();
                oLattice.AddBeam(vecPt1, fBeam1, vecPt2, fBeam2, true);
                PreviewLattice(oLattice, clrColor, fTransparency, fMetallic, fRoughness);
            }

            public static void PreviewLine(
                List<Vector3>   aPoints,
                ColorFloat      clrColor)
            {
                int iNextGroupId = (int)nNumberOfGroups;
                PolyLine oLine = new PolyLine(clrColor);
                for (int i = 0; i < aPoints.Count; i++)
                {
                    oLine.nAddVertex(aPoints[i]);
                }
                Library.oViewer().Add(oLine, iNextGroupId);
                nNumberOfGroups++;
            }

            public static void PreviewLine(
                Vector3     vecPt1, 
                Vector3     vecPt2,
                ColorFloat  clrColor)
            {
                int iNextGroupId        = (int)nNumberOfGroups;
                PolyLine oLine          = new PolyLine(clrColor);
                List<Vector3> aPoints   = new () {vecPt1, vecPt2};
                for (int i = 0; i < aPoints.Count; i++)
                {
                    oLine.nAddVertex(aPoints[i]);
                }
                Library.oViewer().Add(oLine, iNextGroupId);
                nNumberOfGroups++;
            }

            public static void PreviewGrid(
                List<List<Vector3>> aGrid,
                ColorFloat          clrColor)
            {
                for (int i = 0; i < aGrid.Count; i++)
                {
                    PreviewLine(aGrid[i], clrColor);
                }
                aGrid = GridOperations.aGetInverseGrid(aGrid);
                for (int i = 0; i < aGrid.Count; i++)
                {
                    PreviewLine(aGrid[i], clrColor);
                }
            }

            public static void PreviewEdges(
                List<List<Vector3>> aEdges,
                ColorFloat          clrColor)
            {
                for (int i = 0; i < aEdges.Count; i++)
                {
                    PreviewLine(aEdges[i], clrColor);
                }
            }

            public static void PreviewPointCloud(
                List<Vector3>   aPoints,
                float           fBeam,
                ColorFloat      clrColor,
                float           fTransparency   = 0.9f,
                float           fMetallic       = 0.4f,
                float           fRoughness      = 0.7f)
            {
                for (int i = 0; i < aPoints.Count; i++)
                {
                    PreviewPoint(aPoints[i], fBeam, clrColor, fTransparency, fMetallic, fRoughness);
                }
            }

            public static void PreviewFrame(
                LocalFrame  oFrame,
                float       fSize)
            {
                PolyLine oXLine = new(Cp.clrRed);
                oXLine.nAddVertex(oFrame.vecGetPosition());
                oXLine.nAddVertex(oFrame.vecGetPosition() + fSize * oFrame.vecGetLocalX());
                oXLine.AddArrow(0.2f * fSize);

                PolyLine oYLine = new(Cp.clrGreen);
                oYLine.nAddVertex(oFrame.vecGetPosition());
                oYLine.nAddVertex(oFrame.vecGetPosition() + fSize * oFrame.vecGetLocalY());
                oYLine.AddArrow(0.2f * fSize);

                PolyLine oZLine = new(Cp.clrBlue);
                oZLine.nAddVertex(oFrame.vecGetPosition());
                oZLine.nAddVertex(oFrame.vecGetPosition() + fSize * oFrame.vecGetLocalZ());
                oZLine.AddArrow(0.2f * fSize);

                float fPointRadius = MathF.Min(0.5f, 0.05f * fSize);
                PreviewPoint(oFrame.vecGetPosition(), fPointRadius, Cp.clrBlack);
                Library.oViewer().Add(oXLine);
                Library.oViewer().Add(oYLine);
                Library.oViewer().Add(oZLine);
            }

            public static void PreviewFrames(
                Frames  aFrames,
                float   fSize)
            {
                float fTotalLength  = SplineOperations.fGetTotalLength(aFrames.aGetPoints(100));
                uint nSamples       = (uint)(2f * fTotalLength / fSize);
                for (int i = 0; i < nSamples; i++)
                {
                    float fLR           = 1f / (nSamples - 1f) * i;
                    LocalFrame oFrame   = aFrames.oGetLocalFrame(fLR);
                    PreviewFrame(oFrame, fSize);
                }
            }

            public static void PreviewCircleSection(
                LocalFrame  oFrame,
                float       fRadius,
                ColorFloat  clrColor,
                float       fTransparency   = 0.9f,
                float       fMetallic       = 0.4f,
                float       fRoughness      = 0.7f)
            {
                Lattice oLattice    = new Lattice();
                Vector3 vecPt1      = oFrame.vecGetPosition();
                Vector3 vecPt2      = vecPt1 + 1f * oFrame.vecGetLocalZ();
                oLattice.AddBeam(vecPt1, fRadius, vecPt2, fRadius, false);
                PreviewLattice(oLattice, clrColor, fTransparency, fMetallic, fRoughness);
            }

            public static void PreviewCircle(
                LocalFrame  oFrame,
                float       fRadius,
                ColorFloat  clrColor)
            {
                List<Vector3> aPoints   = new List<Vector3>();
                uint nSamples           = 100;
                for (uint i = 0; i < nSamples; i++)
                {
                    float fPhi      = 2f * MathF.PI / (float)(nSamples - 1) * i;
                    Vector3 vecRel  = VecOperations.vecGetCylPoint(fRadius, fPhi, 0f);
                    Vector3 vecPt   = VecOperations.vecTranslatePointOntoFrame(oFrame, vecRel);
                    aPoints.Add(vecPt);
                }
                PreviewLine(aPoints, clrColor);
            }

            public static void PreviewCircle(
                Vector3     vecCentre,
                float       fRadius,
                ColorFloat  clrColor)
            {
                LocalFrame oFrame = new (vecCentre);
                PreviewCircle(oFrame, fRadius, clrColor);
            }

            /// <summary>
            /// Constructs all triangle edges within the mesh from wireframe lines.
            /// Do not use this function for very large, finely-resolved meshes.
            /// </summary>
            public static void PreviewMeshWireframe(
                Mesh            msh,
                ColorFloat      clrColor)
            {
                int nTriangles = msh.nTriangleCount();
                for (int i = 0; i < nTriangles; i++)
                {
                    Triangle oTri   = msh.oTriangleAt(i);
                    Vector3 vecA    = msh.vecVertexAt(oTri.A);
                    Vector3 vecB    = msh.vecVertexAt(oTri.B);
                    Vector3 vecC    = msh.vecVertexAt(oTri.C);
                    List<Vector3> aBound = new () {vecA, vecB, vecC, vecA};
                    Preview(aBound, clrColor);
                }
            }

            public static void PreviewCylinderWireframe(
                BaseCylinder    oCyl,
                ColorFloat      clrColor,
                uint            nRadialSamples = 4,
                uint            nLengthSamples = 10)
            {
                // length samples
                for (uint nLengthSample = 0; nLengthSample < nLengthSamples; nLengthSample++)
                {
                    uint nSamples           = 100;
                    float fRadiusRatio      = 1f;
                    float fLengthRatio      = 1f / (float)(nLengthSamples - 1) * nLengthSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fPhiRatio     = 1f / (float)(nSamples - 1) * i;
                        aPoints.Add(oCyl.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clrColor);
                }

                // radial samples
                for (uint nRadialSample = 0; nRadialSample < nRadialSamples; nRadialSample++)
                {
                    uint nSamples           = 1000;
                    float fRadiusRatio      = 1f;
                    float fPhiRatio         = 1f / (float)(nRadialSamples) * nRadialSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fLengthRatio  = 1f / (float)(nSamples - 1) * i;
                        aPoints.Add(oCyl.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clrColor);
                }
            }

            public static void PreviewPipeWireframe(
                BasePipe    oCyl,
                ColorFloat  clrColor,
                uint        nRadialSamples = 4,
                uint        nLengthSamples = 10)
            {
                // length samples
                for (uint nLengthSample = 0; nLengthSample < nLengthSamples; nLengthSample++)
                {
                    uint nSamples           = 100;
                    float fRadiusRatio      = 1f;
                    float fLengthRatio      = 1f / (float)(nLengthSamples - 1) * nLengthSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fPhiRatio     = 1f / (float)(nSamples - 1) * i;
                        aPoints.Add(oCyl.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clrColor);
                }

                // length samples
                for (uint nLengthSample = 0; nLengthSample < nLengthSamples; nLengthSample++)
                {
                    uint nSamples           = 100;
                    float fRadiusRatio      = 0f;
                    float fLengthRatio      = 1f / (float)(nLengthSamples - 1) * nLengthSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fPhiRatio     = 1f / (float)(nSamples - 1) * i;
                        aPoints.Add(oCyl.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clrColor);
                }

                // radial samples
                for (uint nRadialSample = 0; nRadialSample < nRadialSamples; nRadialSample++)
                {
                    uint nSamples           = 100;
                    float fRadiusRatio      = 1f;
                    float fPhiRatio         = 1f / (float)(nRadialSamples) * nRadialSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fLengthRatio  = 1f / (float)(nSamples - 1) * i;
                        aPoints.Add(oCyl.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clrColor);
                }

                // radial samples
                for (uint nRadialSample = 0; nRadialSample < nRadialSamples; nRadialSample++)
                {
                    uint nSamples           = 100;
                    float fRadiusRatio      = 0f;
                    float fPhiRatio         = 1f / (float)(nRadialSamples) * nRadialSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fLengthRatio  = 1f / (float)(nSamples - 1) * i;
                        aPoints.Add(oCyl.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clrColor);
                }
            }

            public static void PreviewBoxWireframe(
                BaseBox     oBox,
                ColorFloat  clrColor)
            {
                // lower face
                PreviewLine(new List<Vector3>()
                {
                    oBox.vecGetSurfacePoint(-1, -1, 0),
                    oBox.vecGetSurfacePoint(-1,  1, 0),
                    oBox.vecGetSurfacePoint( 1,  1, 0),
                    oBox.vecGetSurfacePoint( 1, -1, 0),
                    oBox.vecGetSurfacePoint(-1, -1, 0)
                }, clrColor);


                // upper face
                PreviewLine(new List<Vector3>()
                {
                    oBox.vecGetSurfacePoint(-1, -1, 1),
                    oBox.vecGetSurfacePoint(-1,  1, 1),
                    oBox.vecGetSurfacePoint( 1,  1, 1),
                    oBox.vecGetSurfacePoint( 1, -1, 1),
                    oBox.vecGetSurfacePoint(-1, -1, 1)
                }, clrColor);

                // side pillars
                PreviewLine(new List<Vector3>()
                {
                    oBox.vecGetSurfacePoint(-1, -1, 0),
                    oBox.vecGetSurfacePoint(-1, -1, 1),
                }, clrColor);

                PreviewLine(new List<Vector3>()
                {
                    oBox.vecGetSurfacePoint(-1, 1, 0),
                    oBox.vecGetSurfacePoint(-1, 1, 1),
                }, clrColor);

                PreviewLine(new List<Vector3>()
                {
                    oBox.vecGetSurfacePoint(1, 1, 0),
                    oBox.vecGetSurfacePoint(1, 1, 1),
                }, clrColor);

                PreviewLine(new List<Vector3>()
                {
                    oBox.vecGetSurfacePoint(1, -1, 0),
                    oBox.vecGetSurfacePoint(1, -1, 1),
                }, clrColor);
            }

            public static void PreviewBoxWireframe(
                BBox3       oBBox,
                ColorFloat  clrColor)
            {
                Vector3 vecBase = VecOperations.vecSetZ(0.5f * (oBBox.vecMax + oBBox.vecMin), oBBox.vecMin.Z);
                float fLength   = (oBBox.vecMax - oBBox.vecMin).Z;
                float fWidth    = (oBBox.vecMax - oBBox.vecMin).X;
                float fDepth    = (oBBox.vecMax - oBBox.vecMin).Y;
                BaseBox oBox    = new BaseBox(new LocalFrame(vecBase), fLength, fWidth, fDepth);
                PreviewBoxWireframe(oBox, clrColor);
            }

            public static void PreviewRingWireframe(
                BaseRing    oRing, 
                ColorFloat  clr,
                uint        nRadialSamples = 4,
                uint        nLengthSamples = 10) 
            {
                // length samples
                for (uint nLengthSample = 0; nLengthSample < nLengthSamples; nLengthSample++)
                {
                    uint nSamples           = 100;
                    float fRadiusRatio      = 1f;
                    float fLengthRatio      = 1f / (nLengthSamples - 1f) * nLengthSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fPhiRatio     = 1f / (nSamples - 1f) * i;
                        aPoints.Add(oRing.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clr);
                }

                // radial samples
                for (uint nRadialSample = 0; nRadialSample < nRadialSamples; nRadialSample++)
                {
                    uint nSamples           = 500;
                    float fRadiusRatio      = 1f;
                    float fPhiRatio         = 1f / (nRadialSamples - 1f) * nRadialSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fLengthRatio  = 1f / (nSamples - 1f) * i;
                        aPoints.Add(oRing.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clr);
                }
            }
        }
    }
}
```

### ShapeKernel/Visualizations/ShPreviewFunctions_II.cs

```csharp
//
// SPDX-License-Identifier: Apache-2.0
//
// The LEAP 71 ShapeKernel is an open source geometry engine
// specifically for use in Computational Engineering Models (CEM).
//
// For more information, please visit https://leap71.com/shapekernel
// 
// This project is developed and maintained by LEAP 71 - © 2024 by LEAP 71
// https://leap71.com
//
// Computational Engineering will profoundly change our physical world in the
// years ahead. Thank you for being part of the journey.
//
// We have developed this library to be used widely, for both commercial and
// non-commercial projects alike. Therefore, have released it under a permissive
// open-source license.
// 
// The LEAP 71 ShapeKernel is based on the PicoGK compact computational geometry 
// framework. See https://picogk.org for more information.
//
// LEAP 71 licenses this file to you under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with the
// License. You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, THE SOFTWARE IS
// PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// See the License for the specific language governing permissions and
// limitations under the License.   
//

using System.Numerics;
using PicoGK;


namespace Leap71
{
    namespace ShapeKernel
    {
        public partial class Sh
        {            
            public static int Preview(
                Mesh        oMesh,
                ColorFloat  clrColor,
                float       fTransparency   = 0.9f,
                float       fMetallic       = 0.4f,
                float       fRoughness      = 0.7f)
            {
                int iNextGroupId    = (int)nNumberOfGroups;
                ColorFloat clr      = new ColorFloat(clrColor, fTransparency);
                Library.oViewer().SetGroupMaterial(iNextGroupId,
                                            clr,
                                            fMetallic,
                                            fRoughness);
                Library.oViewer().Add(oMesh, iNextGroupId);
                nNumberOfGroups++;
                return (int)(nNumberOfGroups - 1);
            }

            public static int Preview(
                Voxels      oVoxels,
                ColorFloat  clrColor,
                float       fTransparency   = 0.9f,
                float       fMetallic       = 0.4f,
                float       fRoughness      = 0.7f)
            {
                int iNextGroupId    = (int)nNumberOfGroups;
                ColorFloat clr      = new ColorFloat(clrColor, fTransparency);
                Library.oViewer().SetGroupMaterial(iNextGroupId,
                                            clr,
                                            fMetallic,
                                            fRoughness);
                Library.oViewer().Add(oVoxels, iNextGroupId);
                nNumberOfGroups++;
                return (int)(nNumberOfGroups - 1);
            }

            public static int Preview(
                Lattice     oLattice,
                ColorFloat  clrColor,
                float       fTransparency   = 0.9f,
                float       fMetallic       = 0.4f,
                float       fRoughness      = 0.7f)
            {
                int iNextGroupId    = (int)nNumberOfGroups;
                ColorFloat clr      = new ColorFloat(clrColor, fTransparency);
                Library.oViewer().SetGroupMaterial(iNextGroupId,
                                            clr,
                                            fMetallic,
                                            fRoughness);
                Voxels oVoxels = new Voxels(oLattice);
                Library.oViewer().Add(oVoxels, iNextGroupId);
                nNumberOfGroups++;
                return (int)(nNumberOfGroups - 1);
            }

            public static void Preview(
                Vector3     vecPt,
                float       fBeam,
                ColorFloat  clrColor,
                float       fTransparency   = 0.9f,
                float       fMetallic       = 0.4f,
                float       fRoughness      = 0.7f)
            {
                BaseSphere oBall = new (new (vecPt), fBeam);
                PreviewMesh(oBall.mshConstruct(), clrColor, fTransparency, fMetallic, fRoughness);
            }

            public static void Preview(
                List<Vector3>   aPoints,
                ColorFloat      clrColor)
            {
                int iNextGroupId = (int)nNumberOfGroups;
                PolyLine oLine = new PolyLine(clrColor);
                for (int i = 0; i < aPoints.Count; i++)
                {
                    oLine.nAddVertex(aPoints[i]);
                }
                Library.oViewer().Add(oLine, iNextGroupId);
                nNumberOfGroups++;
            }

            public static void Preview(
                LocalFrame  oFrame,
                float       fSize)
            {
                PolyLine oXLine = new(Cp.clrRed);
                oXLine.nAddVertex(oFrame.vecGetPosition());
                oXLine.nAddVertex(oFrame.vecGetPosition() + fSize * oFrame.vecGetLocalX());
                oXLine.AddArrow(0.2f * fSize);

                PolyLine oYLine = new(Cp.clrGreen);
                oYLine.nAddVertex(oFrame.vecGetPosition());
                oYLine.nAddVertex(oFrame.vecGetPosition() + fSize * oFrame.vecGetLocalY());
                oYLine.AddArrow(0.2f * fSize);

                PolyLine oZLine = new(Cp.clrBlue);
                oZLine.nAddVertex(oFrame.vecGetPosition());
                oZLine.nAddVertex(oFrame.vecGetPosition() + fSize * oFrame.vecGetLocalZ());
                oZLine.AddArrow(0.2f * fSize);

                float fPointRadius = MathF.Min(0.5f, 0.05f * fSize);
                PreviewPoint(oFrame.vecGetPosition(), fPointRadius, Cp.clrBlack);
                Library.oViewer().Add(oXLine);
                Library.oViewer().Add(oYLine);
                Library.oViewer().Add(oZLine);
            }

            public static void Preview(
                Frames  aFrames,
                float   fSize)
            {
                float fTotalLength  = SplineOperations.fGetTotalLength(aFrames.aGetPoints(100));
                uint nSamples       = (uint)(2f * fTotalLength / fSize);
                for (int i = 0; i < nSamples; i++)
                {
                    float fLR           = 1f / (nSamples - 1f) * i;
                    LocalFrame oFrame   = aFrames.oGetLocalFrame(fLR);
                    PreviewFrame(oFrame, fSize);
                }
            }

            public static void Preview(
                BaseCylinder    oCyl,
                ColorFloat      clrColor,
                uint            nRadialSamples = 4,
                uint            nLengthSamples = 10)
            {
                // length samples
                for (uint nLengthSample = 0; nLengthSample < nLengthSamples; nLengthSample++)
                {
                    uint nSamples           = 100;
                    float fRadiusRatio      = 1f;
                    float fLengthRatio      = 1f / (float)(nLengthSamples - 1) * nLengthSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fPhiRatio     = 1f / (float)(nSamples - 1) * i;
                        aPoints.Add(oCyl.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clrColor);
                }

                // radial samples
                for (uint nRadialSample = 0; nRadialSample < nRadialSamples; nRadialSample++)
                {
                    uint nSamples           = 1000;
                    float fRadiusRatio      = 1f;
                    float fPhiRatio         = 1f / (float)(nRadialSamples) * nRadialSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fLengthRatio  = 1f / (float)(nSamples - 1) * i;
                        aPoints.Add(oCyl.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clrColor);
                }
            }

            public static void Preview(
                BasePipe    oCyl,
                ColorFloat  clrColor,
                uint        nRadialSamples = 4,
                uint        nLengthSamples = 10)
            {
                // length samples
                for (uint nLengthSample = 0; nLengthSample < nLengthSamples; nLengthSample++)
                {
                    uint nSamples           = 100;
                    float fRadiusRatio      = 1f;
                    float fLengthRatio      = 1f / (float)(nLengthSamples - 1) * nLengthSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fPhiRatio     = 1f / (float)(nSamples - 1) * i;
                        aPoints.Add(oCyl.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clrColor);
                }

                // length samples
                for (uint nLengthSample = 0; nLengthSample < nLengthSamples; nLengthSample++)
                {
                    uint nSamples           = 100;
                    float fRadiusRatio      = 0f;
                    float fLengthRatio      = 1f / (float)(nLengthSamples - 1) * nLengthSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fPhiRatio     = 1f / (float)(nSamples - 1) * i;
                        aPoints.Add(oCyl.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clrColor);
                }

                // radial samples
                for (uint nRadialSample = 0; nRadialSample < nRadialSamples; nRadialSample++)
                {
                    uint nSamples           = 100;
                    float fRadiusRatio      = 1f;
                    float fPhiRatio         = 1f / (float)(nRadialSamples) * nRadialSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fLengthRatio  = 1f / (float)(nSamples - 1) * i;
                        aPoints.Add(oCyl.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clrColor);
                }

                // radial samples
                for (uint nRadialSample = 0; nRadialSample < nRadialSamples; nRadialSample++)
                {
                    uint nSamples           = 100;
                    float fRadiusRatio      = 0f;
                    float fPhiRatio         = 1f / (float)(nRadialSamples) * nRadialSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fLengthRatio  = 1f / (float)(nSamples - 1) * i;
                        aPoints.Add(oCyl.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clrColor);
                }
            }

            public static void Preview(
                BaseBox     oBox,
                ColorFloat  clrColor)
            {
                // lower face
                PreviewLine(new List<Vector3>()
                {
                    oBox.vecGetSurfacePoint(-1, -1, 0),
                    oBox.vecGetSurfacePoint(-1,  1, 0),
                    oBox.vecGetSurfacePoint( 1,  1, 0),
                    oBox.vecGetSurfacePoint( 1, -1, 0),
                    oBox.vecGetSurfacePoint(-1, -1, 0)
                }, clrColor);


                // upper face
                PreviewLine(new List<Vector3>()
                {
                    oBox.vecGetSurfacePoint(-1, -1, 1),
                    oBox.vecGetSurfacePoint(-1,  1, 1),
                    oBox.vecGetSurfacePoint( 1,  1, 1),
                    oBox.vecGetSurfacePoint( 1, -1, 1),
                    oBox.vecGetSurfacePoint(-1, -1, 1)
                }, clrColor);

                // side pillars
                PreviewLine(new List<Vector3>()
                {
                    oBox.vecGetSurfacePoint(-1, -1, 0),
                    oBox.vecGetSurfacePoint(-1, -1, 1),
                }, clrColor);

                PreviewLine(new List<Vector3>()
                {
                    oBox.vecGetSurfacePoint(-1, 1, 0),
                    oBox.vecGetSurfacePoint(-1, 1, 1),
                }, clrColor);

                PreviewLine(new List<Vector3>()
                {
                    oBox.vecGetSurfacePoint(1, 1, 0),
                    oBox.vecGetSurfacePoint(1, 1, 1),
                }, clrColor);

                PreviewLine(new List<Vector3>()
                {
                    oBox.vecGetSurfacePoint(1, -1, 0),
                    oBox.vecGetSurfacePoint(1, -1, 1),
                }, clrColor);
            }

            public static void Preview(
                BBox3       oBBox,
                ColorFloat  clrColor)
            {
                Vector3 vecBase = VecOperations.vecSetZ(0.5f * (oBBox.vecMax + oBBox.vecMin), oBBox.vecMin.Z);
                float fLength   = (oBBox.vecMax - oBBox.vecMin).Z;
                float fWidth    = (oBBox.vecMax - oBBox.vecMin).X;
                float fDepth    = (oBBox.vecMax - oBBox.vecMin).Y;
                BaseBox oBox    = new BaseBox(new LocalFrame(vecBase), fLength, fWidth, fDepth);
                PreviewBoxWireframe(oBox, clrColor);
            }

            public static void Preview(
                BaseRing    oRing, 
                ColorFloat  clr,
                uint        nRadialSamples = 4,
                uint        nLengthSamples = 10)
            {
                // length samples
                for (uint nLengthSample = 0; nLengthSample < nLengthSamples; nLengthSample++)
                {
                    uint nSamples           = 100;
                    float fRadiusRatio      = 1f;
                    float fLengthRatio      = 1f / (nLengthSamples - 1f) * nLengthSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fPhiRatio     = 1f / (nSamples - 1f) * i;
                        aPoints.Add(oRing.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clr);
                }

                // radial samples
                for (uint nRadialSample = 0; nRadialSample < nRadialSamples; nRadialSample++)
                {
                    uint nSamples           = 500;
                    float fRadiusRatio      = 1f;
                    float fPhiRatio         = 1f / (float)nRadialSamples * nRadialSample;
                    List<Vector3> aPoints   = new List<Vector3>();
                    for (uint i = 0; i < nSamples; i++)
                    {
                        float fLengthRatio  = 1f / (nSamples - 1f) * i;
                        aPoints.Add(oRing.vecGetSurfacePoint(fLengthRatio, fPhiRatio, fRadiusRatio));
                    }
                    PreviewLine(aPoints, clr);
                }
            }
        }
    }
}
```

---

## Anhang F: Beispiele

### Examples/Ex_BaseBoxShowCase.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this PicoGK Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using PicoGK;
using System.Numerics;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class BaseBoxShowCase
        {
            public static void Task()
            {
                try
                {
                    {
                        // basic
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(-50, 0, 0));
                        BaseBox oShape          = new BaseBox(oLocalFrame, 20, 10, 15);
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrBlue);
                    }

                    {
                        // modulated
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(50, 0, 0));
                        BaseBox oShape          = new BaseBox(oLocalFrame, 20);
                        oShape.SetWidth(new LineModulation(fGetLineModulation2));
                        oShape.SetDepth(new LineModulation(fGetLineModulation1));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrGreen);
                    }
                    {
                        // modulated + spined
                        ISpline oSpine          = new ExampleSpline();
                        Frames aFrames          = new Frames(oSpine.aGetPoints(), Vector3.UnitY);
                        BaseBox oShape          = new BaseBox(aFrames);
                        oShape.SetWidth(new LineModulation(fGetLineModulation2));
                        oShape.SetDepth(new LineModulation(fGetLineModulation1));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrYellow);
                    }
                }
                catch (Exception e)
                {
                    Library.Log($"Failed run example: \n{e.Message}"); ;
                }
            }

            // functions for generic line modulations
            public static float fGetLineModulation1(float fLengthRatio)
            {
                float fWidth = 10f - 3f * MathF.Cos(8f * fLengthRatio);
                return fWidth;
            }

            public static float fGetLineModulation2(float fLengthRatio)
            {
                float fDepth = 8f - 1f * MathF.Cos(40f * fLengthRatio);
                return fDepth;
            }
        }
    }
}
```

### Examples/Ex_BaseCylinderShowcase.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using PicoGK;
using System.Numerics;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class BaseCylinderShowCase
        {
            public static void Task()
            {
                try
                {
                    {
                        // basic
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(-50, 0, 0));
                        BaseCylinder oShape     = new BaseCylinder(oLocalFrame, 60f, 40);
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrBlue);
                    }

                    {
                        // modulated
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(50, 0, 0));
                        BaseCylinder oShape     = new BaseCylinder(oLocalFrame, 60, 12);
                        oShape.SetLengthSteps(500);
                        oShape.SetRadius(new SurfaceModulation(new LineModulation(fGetLineModulation)));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrGreen);
                    }
                    {
                        // modulated + spined
                        ISpline oSpine          = new ExampleSpline();
                        Frames aFrames          = new Frames(oSpine.aGetPoints(), Vector3.UnitY);
                        BaseCylinder oShape     = new BaseCylinder(aFrames, 12);
                        oShape.SetRadius(new SurfaceModulation(fGetSurfaceModulation));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrYellow);
                    }
                }
                catch (Exception e)
                {
                    Library.Log($"Failed run example: \n{e.Message}"); ;
                }
            }

            // functions for generic line modulations
            public static float fGetLineModulation(float fLengthRatio)
            {
                float fWidth = 10f - 3f * MathF.Cos(8f * fLengthRatio);
                return fWidth;
            }

            // functions for generic surface modulations
            public static float fGetSurfaceModulation(float fPhi, float fLengthRatio)
            {
                float fRadius = 12f + 3f * MathF.Cos(5f * fPhi);
                return fRadius;
            }
        }
    }
}
```

### Examples/Ex_BaseLensShowCase.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using PicoGK;
using System.Numerics;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class BaseLensShowCase
        {
            public static void Task()
            {
                try
                {
                    {
                        // basic
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(-50, -50, 0));
                        BaseLens oShape         = new BaseLens(oLocalFrame, 10, 10, 40);
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrFrozen);
                    }

                    {
                        // modulated 0
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(50, 50, 0));
                        BaseLens oShape         = new BaseLens(oLocalFrame, 10, 10, 40);
                        oShape.SetHeight(new SurfaceModulation(fGetLenseHeight1), new SurfaceModulation(fGetLenseHeight2));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrPitaya);
                    }

                    {
                        // modulated 1
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(-50, 50, 0));
                        BaseLens oShape         = new BaseLens(oLocalFrame, 10, 10, 40);
                        oShape.SetHeight(new SurfaceModulation(fGetLenseHeight1), new SurfaceModulation(fGetLenseHeight3));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrWarning);
                    }
                }
                catch (Exception e)
                {
                    Library.Log($"Failed run example: \n{e.Message}"); ;
                }
            }

            // functions for lense surface modulations
            static float fGetLenseHeight1(float fPhi, float fRadiusRatio)
            {
                float fRadius = 5f - fGetSurfaceModulation(fPhi, fRadiusRatio);
                return fRadius;
            }

            static float fGetLenseHeight2(float fPhi, float fRadiusRatio)
            {
                float fRadius = 5f + fGetSurfaceModulation(fPhi, fRadiusRatio);
                return fRadius;
            }

            static float fGetLenseHeight3(float fPhi, float fRadiusRatio)
            {
                fPhi += 0.3f * MathF.PI * fRadiusRatio;
                float fRadius = 5f + 1f * MathF.Cos(6f * fPhi) + 3f * MathF.Cos(20f * fRadiusRatio);
                return fRadius;
            }

            // functions for generic surface modulations
            public static float fGetSurfaceModulation(float fPhi, float fLengthRatio)
            {
                float fRadius = 12f + 3f * MathF.Cos(5f * fPhi);
                return fRadius;
            }
        }
    }
}
```

### Examples/Ex_BasePipeSegmentShowCase.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using PicoGK;
using System.Numerics;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class BasePipeSegmentShowCase
        {
            public static void Task()
            {
                try
                {
                    {
                        // basic
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(-50, 0, 0));
                        BasePipeSegment oShape  = new BasePipeSegment(oLocalFrame, 60, 20, 40,
                            new LineModulation(MathF.PI),
                            new LineModulation(0.5f * MathF.PI),
                            BasePipeSegment.EMethod.MID_RANGE);
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrBlue);
                    }

                    {
                        // modulated 0
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(-50, 50, 0));
                        BasePipeSegment oShape  = new BasePipeSegment(oLocalFrame, 60, 2, 40,
                            new LineModulation(MathF.PI),
                            new LineModulation(fGetSegmentPhiRange2),
                            BasePipeSegment.EMethod.MID_RANGE);
                        oShape.SetLengthSteps(500);
                        oShape.SetRadius(
                            new SurfaceModulation(6f),
                            new SurfaceModulation(new LineModulation(fGetLineModulation1)));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrCrystal);
                    }

                    {
                        // modulated 1
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(0, -50, 0));
                        BasePipeSegment oShape  = new BasePipeSegment(oLocalFrame, 60, 2, 40,
                            new LineModulation(MathF.PI),
                            new LineModulation(fGetSegmentPhiRange1),
                            BasePipeSegment.EMethod.MID_RANGE);
                        oShape.SetLengthSteps(500);
                        oShape.SetRadius(
                            new SurfaceModulation(fGetSurfaceModulation3),
                            new SurfaceModulation(fGetSurfaceModulation1));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrYellow);
                    }

                    {
                        // modulated 2
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(50, -50, 0));
                        BasePipeSegment oShape  = new BasePipeSegment(oLocalFrame, 60, 2, 40,
                            new LineModulation(fGetSegmentPhiMid1),
                            new LineModulation(1.75f * MathF.PI),
                            BasePipeSegment.EMethod.MID_RANGE);
                        oShape.SetLengthSteps(500);
                        oShape.SetRadius(
                            new SurfaceModulation(fGetSurfaceModulation4),
                            new SurfaceModulation(fGetSurfaceModulation2));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrRuby);
                    }

                    {
                        // modulated + spined
                        ISpline oSpine          = new ExampleSpline();
                        Frames aFrames          = new Frames(oSpine.aGetPoints(), Vector3.UnitY);
                        BasePipeSegment oShape  = new BasePipeSegment(aFrames, 2, 40,
                            new LineModulation(fGetSegmentPhiMid2),
                            new LineModulation(1.5f * MathF.PI),
                            BasePipeSegment.EMethod.MID_RANGE);
                        oShape.SetRadius(
                            new SurfaceModulation(fGetSurfaceModulation3),
                            new SurfaceModulation(fGetSurfaceModulation1));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrRacingGreen);
                    }

                    {
                        // spined
                        ISpline oSpine          = new ExampleSpline();
                        List<Vector3> aPoints   = SplineOperations.aTranslateList(oSpine.aGetPoints(), 50 * Vector3.UnitX);
                        Frames aFrames          = new Frames(aPoints, Vector3.UnitY);
                        BasePipeSegment oShape  = new BasePipeSegment(aFrames, 10, 12,
                            new LineModulation(fGetSegmentPhiMid1),
                            new LineModulation(1f * MathF.PI),
                            BasePipeSegment.EMethod.MID_RANGE);
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrGray);
                    }
                }
                catch (Exception e)
                {
                    Library.Log($"Failed run example: \n{e.Message}"); ;
                }
            }


            // functions for pipe segment line modulations
            static float fGetSegmentPhiMid1(float fLengthRatio)
            {
                float fPhiMid = -1f * MathF.PI * fLengthRatio;
                return fPhiMid;
            }

            static float fGetSegmentPhiMid2(float fLengthRatio)
            {
                float fPhiMid = 4f * MathF.PI * fLengthRatio;
                return fPhiMid;
            }

            static float fGetSegmentPhiRange1(float fLengthRatio)
            {
                float fPhiRange = 0.5f * MathF.PI + 0.25f * MathF.PI * MathF.Cos(8f * fLengthRatio);
                return fPhiRange;
            }

            static float fGetSegmentPhiRange2(float fLengthRatio)
            {
                float fPhiRange = 0.5f * MathF.PI + 0.25f * MathF.PI * MathF.Cos(40f * fLengthRatio);
                return fPhiRange;
            }

            // functions for generic line modulations
            static float fGetLineModulation1(float fLengthRatio)
            {
                float fWidth = 10f - 3f * MathF.Cos(8f * fLengthRatio);
                return fWidth;
            }

            // functions for generic surface modulations
            public static float fGetSurfaceModulation1(float fPhi, float fLengthRatio)
            {
                float fRadius = 12f + 3f * MathF.Cos(5f * fPhi);
                return fRadius;
            }

            public static float fGetSurfaceModulation2(float fPhi, float fLengthRatio)
            {
                fPhi += 1f * MathF.PI * fLengthRatio;
                float fRadius = 10f - 2f * MathF.Cos(3f * fPhi) + 9f * fLengthRatio;
                return fRadius;
            }

            public static float fGetSurfaceModulation3(float fPhi, float fLengthRatio)
            {
                float fRadius = 8f + 5f * MathF.Cos(5f * fPhi);
                return fRadius;
            }

            public static float fGetSurfaceModulation4(float fPhi, float fLengthRatio)
            {
                fPhi += 1f * MathF.PI * fLengthRatio;
                float fRadius = 9f - 1f * MathF.Cos(3f * fPhi) + 7f * fLengthRatio;
                return fRadius;
            }
        }
    }
}
```

### Examples/Ex_BasePipeShowCase.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using PicoGK;
using System.Numerics;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class BasePipeShowCase
        {
            public static void Task()
            {
                try
                {
                    {
                        // basic
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(-50, 0, 0));
                        BasePipe oShape         = new BasePipe(oLocalFrame, 60, 10, 20);
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrBlue);
                    }

                    {
                        // transformed
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(0, 0, 0));
                        BasePipe oShape         = new BasePipe(oLocalFrame, 60, 10, 20);
                        oShape.SetTransformation(vecGetTransformation);
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrGreen);
                    }

                    {
                        // modulated 0
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(50, -50, 0));
                        BasePipe oShape         = new BasePipe(oLocalFrame, 60, 2, 40);
                        oShape.SetLengthSteps(500);
                        oShape.SetRadius(
                            new SurfaceModulation(6f),
                            new SurfaceModulation(new LineModulation(fGetLineModulation1)));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrLemongrass);
                    }

                    {
                        // modulated 1
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(-50, -50, 0));
                        BasePipe oShape         = new BasePipe(oLocalFrame, 60, 2, 40);
                        oShape.SetLengthSteps(500);
                        oShape.SetRadius(
                            new SurfaceModulation(fGetSurfaceModulation3),
                            new SurfaceModulation(fGetSurfaceModulation1));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrLavender);
                    }

                    {
                        // modulated 2
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(0, -50, 0));
                        BasePipe oShape         = new BasePipe(oLocalFrame, 60, 2, 40);
                        oShape.SetLengthSteps(500);
                        oShape.SetRadius(
                            new SurfaceModulation(fGetSurfaceModulation4),
                            new SurfaceModulation(fGetSurfaceModulation2));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrRed);
                    }

                    {
                        // modulated + spined
                        ISpline oSpine          = new ExampleSpline();
                        Frames aFrames          = new Frames(oSpine.aGetPoints(), Vector3.UnitY);
                        BasePipe oShape         = new BasePipe(aFrames, 2, 40);
                        oShape.SetRadius(
                            new SurfaceModulation(fGetSurfaceModulation3),
                            new SurfaceModulation(fGetSurfaceModulation1));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrOrchid);
                    }

                    {
                        // spined
                        ISpline oSpine          = new ExampleSpline();
                        List<Vector3> aPoints   = SplineOperations.aTranslateList(oSpine.aGetPoints(), 50 * Vector3.UnitX);
                        Frames aFrames          = new Frames(aPoints, Vector3.UnitY);
                        BasePipe oShape         = new BasePipe(aFrames, 10, 12);
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrToothpaste);
                    }
                }
                catch (Exception e)
                {
                    Library.Log($"Failed run example: \n{e.Message}"); ;
                }
            }

            // functions for generic line modulations
            public static float fGetLineModulation1(float fLengthRatio)
            {
                float fWidth = 10f - 3f * MathF.Cos(8f * fLengthRatio);
                return fWidth;
            }

            public static float fGetLineModulation2(float fLengthRatio)
            {
                float fDepth = 8f - 1f * MathF.Cos(40f * fLengthRatio);
                return fDepth;
            }

            // functions for generic surface modulations
            public static float fGetSurfaceModulation1(float fPhi, float fLengthRatio)
            {
                float fRadius = 12f + 3f * MathF.Cos(5f * fPhi);
                return fRadius;
            }

            public static float fGetSurfaceModulation2(float fPhi, float fLengthRatio)
            {
                fPhi += 1f * MathF.PI * fLengthRatio;
                float fRadius = 10f - 2f * MathF.Cos(3f * fPhi) + 9f * fLengthRatio;
                return fRadius;
            }

            public static float fGetSurfaceModulation3(float fPhi, float fLengthRatio)
            {
                float fRadius = 8f + 5f * MathF.Cos(5f * fPhi);
                return fRadius;
            }

            public static float fGetSurfaceModulation4(float fPhi, float fLengthRatio)
            {
                fPhi += 1f * MathF.PI * fLengthRatio;
                float fRadius = 9f - 1f * MathF.Cos(3f * fPhi) + 7f * fLengthRatio;
                return fRadius;
            }

            public static Vector3 vecGetTransformation(Vector3 vecPt)
            {
                float fNewX = vecPt.Y + 0.2f * vecPt.Z - 50f;
                float fNewY = 0.5f * vecPt.Z + 50f;
                float fNewZ = 0.5f * vecPt.X;
                Vector3 vecNewPt = new Vector3(fNewX, fNewY, fNewZ);
                return vecNewPt;
            }
        }
    }
}
```

### Examples/Ex_BaseRingShowCase.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using PicoGK;
using System.Numerics;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class BaseRingShowCase
        {
            public static void Task()
            {
                try
                {
                    {
                        // basic
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(-50, -50, 0));
                        BaseRing oShape         = new BaseRing(oLocalFrame, 30, 8);
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrFrozen);
                    }

                    {
                        // modulated 0
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(-50, 50, 0));
                        BaseRing oShape         = new BaseRing(oLocalFrame, 30);
                        oShape.SetRadius(new SurfaceModulation(fGetRingRadius0));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrPitaya);
                    }

                    {
                        // modulated 1
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(50, 50, 0));
                        BaseRing oShape         = new BaseRing(oLocalFrame, 30);
                        oShape.SetRadius(new SurfaceModulation(fGetRingRadius1));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrWarning);
                    }

                    {
                        // modulated 2
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(50, -50, 0));
                        BaseRing oShape         = new BaseRing(oLocalFrame, 30);
                        oShape.SetRadius(new SurfaceModulation(fGetRingRadius2));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrBlueberry);
                    }
                }
                catch (Exception e)
                {
                    Library.Log($"Failed run example: \n{e.Message}"); ;
                }
            }

            // functions for ring surface modulations
            static float fGetRingRadius0(float fPhi, float fAlpha)
            {
                float fRadius = 10f - 2f * MathF.Cos(5f * fPhi);
                return fRadius;
            }

            static float fGetRingRadius1(float fPhi, float fAlpha)
            {
                float fRadius = 10f + 3f * MathF.Cos(5f * fAlpha);
                return fRadius;
            }

            static float fGetRingRadius2(float fPhi, float fAlpha)
            {
                fPhi += 1f * fAlpha;
                float fRadius = 10f - 2f * MathF.Cos(5f * fPhi) + 3f * MathF.Cos(5f * fAlpha);
                return fRadius;
            }
        }
    }
}
```

### Examples/Ex_BaseSphereShowCase.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using PicoGK;
using System.Numerics;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class BaseSphereShowCase
        {
            public static void Task()
            {
                try
                {
                    {
                        // basic
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(-100, 0, 0));
                        BaseSphere oShape       = new BaseSphere(oLocalFrame, 40);
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrFrozen);
                    }

                    {
                        // modulated 0
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(0, 0, 0));
                        BaseSphere oShape       = new BaseSphere(oLocalFrame);
                        oShape.SetRadius(new SurfaceModulation(fGetSphereRadius0));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrPitaya);
                    }

                    {
                        // modulated 1
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(150, 0, 0));
                        BaseSphere oShape       = new BaseSphere(oLocalFrame);
                        oShape.SetRadius(new SurfaceModulation(fGetSphereRadius1));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrWarning);
                    }
                }
                catch (Exception e)
                {
                    Library.Log($"Failed run example: \n{e.Message}"); ;
                }
            }

            // functions for sphere surface modulations
            static float fGetSphereRadius0(float fTheta, float fPhi)
            {
                float fRadius = 40f - 10f * MathF.Cos(6f * fPhi);
                return fRadius;
            }

            static float fGetSphereRadius1(float fTheta, float fPhi)
            {
                float fRadius = 40f - 10f * MathF.Cos(6f * fPhi) + 30f * MathF.Cos(2f * fTheta);
                return fRadius;
            }
        }
    }
}
```

### Examples/Ex_BasicLattices.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class BasicLattices
        {
            public static void Task()
            {
                try
                {
                    Lattice oLattice = new Lattice();

                    // add node
                    Vector3 vecPt0 = new Vector3(1, 5, -10);
                    float fRadius0 = 5;
                    oLattice.AddSphere(vecPt0, fRadius0);

                    // add beams
                    Vector3 vecPt1 = new Vector3(5, 3, 0);
                    float fRadius1 = 1;
                    Vector3 vecPt2 = new Vector3(-3, 0, 7);
                    float fRadius2 = 3;
                    oLattice.AddBeam(vecPt1, fRadius1, vecPt2, fRadius2, true);
                    oLattice.AddBeam(vecPt1, fRadius1, vecPt2, fRadius2, false);

                    Sh.PreviewLattice(oLattice, Cp.clrBlueberry);
                }
                catch (Exception e)
                {
                    Library.Log($"Failed run example: \n{e.Message}"); ;
                }
            }
        }
    }
}
```

### Examples/Ex_ImplicitGyroidGenus.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class ImplicitGenusGyroid
        {
            public static void Task()
            {
                // Note: genus shape is very small. Use voxel size 0.01mm for good resolution.
                float fGap              = 0.3f;
                float fExtent           = 2.5f;

                // Step 1: generate SDF
                IImplicit sdfGenus      = new ImplicitGenus(fGap);

                // Step 2: define bounding object
                BBox3 oBBox             = new BBox3(1.2f * new Vector3(-fExtent, -fExtent, -fExtent + 1.5f), 1.2f * new Vector3(fExtent, fExtent, fExtent - 1.5f));

                // Step 3: render the implicit shape into voxels
                Voxels voxGenus         = new Voxels(sdfGenus, oBBox);

                // Step 4: intersect  implicit pattern with the voxel
                IImplicit sdfPattern    = new ImplicitGyroid(1, 0.5f);
                Voxels voxGyroidGenus   = voxGenus.voxIntersectImplicit(sdfPattern);

                // Step 5: visualization
                Sh.PreviewVoxels(voxGyroidGenus, Cp.clrRandom());
                Sh.PreviewVoxels(voxGenus, Cp.clrRandom(), 0.5f);

                //// Step 6: export
                // Sh.ExportVoxelsToSTLFile(voxGenus, Sh.strGetExportPath(Sh.EExport.STL, "Genus"));
            }
        }
    }
}
```

### Examples/Ex_ImplicitGyroidSphere.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class ImplicitGyroidSphere
        {
            public static void Task()
            {
                try
                {
                    // generate SDFs using presets.
                    Vector3 vecCentre       = new Vector3();
                    float fRadius           = 10f;
                    IImplicit sdfSphere     = new ImplicitSphere(vecCentre, fRadius);
                    IImplicit sdfPattern    = new ImplicitGyroid(3, 1);
                    BBox3 oBBox             = new BBox3(1.2f * new Vector3(-fRadius, -fRadius, -fRadius), 1.2f * new Vector3(fRadius, fRadius, fRadius));

                    // render a simple shape into voxels.
                    Voxels voxSphere        = new Voxels(sdfSphere, oBBox);

                    // intersect an implicit pattern with a bounding voxelfield.
                    Voxels voxGyroidSphere  = voxSphere.voxIntersectImplicit(sdfPattern);

                    Sh.PreviewVoxels(voxGyroidSphere,   Cp.clrBillie);
                    Sh.PreviewVoxels(voxSphere,         Cp.clrBubblegum, 0.3f);
                }
                catch (Exception e)
                {
                    Library.Log($"Failed run example: \n{e.Message}"); ;
                }
            }
        }
    }
}
```

### Examples/Ex_ImplicitSuperEllipsoid.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using System.Numerics;
using PicoGK;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class ImplicitSolidEllipsoid
        {
            public static void Task()
            {
                // Note: ellipsoid shape is very small. Use voxel size 0.01mm for good resolution.
                // Note: https://en.wikipedia.org/wiki/Superellipsoid
                // Note: parameter n is fEpsilon1
                // Note: parameter e is fEpsilon2
                try
                {
                    {                    
                        float fAx                   = 1f;
                        float fAy                   = 1f;
                        float fAz                   = 1f;
                        float fEpsilon1             = 3.00f;
                        float fEpsilon2             = 0.25f;
                        Vector3 vecCentre           = new Vector3(0f, 0, 0);

                        // Step 1: generate SDF
                        IImplicit sdfEllipsoid      = new ImplicitSuperEllipsoid(vecCentre, fAx, fAz, fAy, fEpsilon1, fEpsilon2);

                        // Step 2: define bounding object
                        BBox3 oBBox                 = new BBox3(1f * new Vector3(-fAx - vecCentre.X, -fAy - vecCentre.Y, -fAz - vecCentre.Z),
                                                                1f * new Vector3(fAx - vecCentre.X, fAy - vecCentre.Y, fAz - vecCentre.Z));

                        // Step 3: render the implicit shape into voxels
                        Voxels voxEllipsoid         = new Voxels(sdfEllipsoid, oBBox);

                        // Step 4: visualization
                        Sh.PreviewVoxels(voxEllipsoid, Cp.clrRuby);
                    }

                    {                        
                        float fAx                   = 1f;
                        float fAy                   = 1f;
                        float fAz                   = 1f;
                        float fEpsilon1             = 1.50f;
                        float fEpsilon2             = 1.50f;
                        Vector3 vecCentre           = new Vector3(-4, 0, 0);

                        // Step 1: generate SDF
                        IImplicit sdfEllipsoid      = new ImplicitSuperEllipsoid(vecCentre, fAx, fAz, fAy, fEpsilon1, fEpsilon2);

                        // Step 2: define bounding object
                        BBox3 oBBox                 = new BBox3(1f * new Vector3(-fAx - vecCentre.X, -fAy - vecCentre.Y, -fAz - vecCentre.Z),
                                                                1f * new Vector3( fAx - vecCentre.X,  fAy - vecCentre.Y,  fAz - vecCentre.Z));

                        // Step 3: render the implicit shape into voxels
                        Voxels voxEllipsoid         = new Voxels(sdfEllipsoid, oBBox);

                        // Step 4: visualization
                        Sh.PreviewVoxels(voxEllipsoid, Cp.clrBlue);
                    }

                    {
                        float fAx                   = 1f;
                        float fAy                   = 1f;
                        float fAz                   = 1f;
                        float fEpsilon1             = 0.25f;
                        float fEpsilon2             = 0.25f;
                        Vector3 vecCentre           = new Vector3(4, 0, 0);

                        // Step 1: generate SDF
                        IImplicit sdfEllipsoid      = new ImplicitSuperEllipsoid(vecCentre, fAx, fAy, fAz, fEpsilon1, fEpsilon2);

                        // Step 2: define bounding object
                        BBox3 oBBox                 = new BBox3(1f * new Vector3(-fAx - vecCentre.X, -fAy - vecCentre.Y, -fAz - vecCentre.Z),
                                                                1f * new Vector3(fAx - vecCentre.X, fAy - vecCentre.Y, fAz - vecCentre.Z));

                        // Step 3: render the implicit shape into voxels
                        Voxels voxEllipsoid         = new Voxels(sdfEllipsoid, oBBox);

                        // Step 4: visualization
                        Sh.PreviewVoxels(voxEllipsoid, Cp.clrBubblegum);
                    }
                }
                catch (Exception e)
                {
                    Library.Log($"Failed run example: \n{e.Message}"); ;
                }
            }
        }
    }
}
```

### Examples/Ex_LatticeManifoldShowCase.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using PicoGK;
using System.Numerics;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class LatticeManifoldShowCase
        {
            public static void Task()
            {
                try
                {
                    {
                        float fOverhangAngleInDeg   = 45;
                        bool bExtendBothSides       = false;
                        float fLength               = 50;
                        float fRadius               = 5;
                        LocalFrame oLocalFrame      = new LocalFrame(new Vector3(-50, 0, 0), Vector3.UnitY);
                        LatticeManifold oShape      = new LatticeManifold(oLocalFrame, fLength, fRadius, fOverhangAngleInDeg, bExtendBothSides);
                        Voxels oVoxels              = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrYellow);
                    }

                    {
                        float fOverhangAngleInDeg   = 30;
                        bool bExtendBothSides       = true;
                        float fLength               = 50;
                        float fRadius               = 10;
                        LocalFrame oLocalFrame      = new LocalFrame(new Vector3(0, 0, 0), Vector3.UnitY);
                        LatticeManifold oShape      = new LatticeManifold(oLocalFrame, fLength, fRadius, fOverhangAngleInDeg, bExtendBothSides);
                        Voxels oVoxels              = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrCrystal);
                    }

                    {
                        float fOverhangAngleInDeg   = 60;
                        bool bExtendBothSides       = true;
                        float fLength               = 50;
                        float fRadius               = 5;
                        LocalFrame oLocalFrame      = new LocalFrame(new Vector3(50, 0, 0), Vector3.UnitY);
                        LatticeManifold oShape      = new LatticeManifold(oLocalFrame, fLength, fRadius, fOverhangAngleInDeg, bExtendBothSides);
                        Voxels oVoxels              = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrGreen);
                    }

                }
                catch (Exception e)
                {
                    Library.Log($"Failed run example: \n{e.Message}"); ;
                }
            }
        }
    }
}
```

### Examples/Ex_LatticePipeShowCase.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using PicoGK;
using System.Numerics;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class LatticePipeShowCase
        {
            public static void Task()
            {
                try
                {
                    {
                        // basic
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(-50, 0, 0));
                        LatticePipe oShape      = new LatticePipe(oLocalFrame, 60f, 10);
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrYellow);
                    }

                    {
                        // modulated 0
                        LocalFrame oLocalFrame  = new LocalFrame(new Vector3(50, -50, 0));
                        LatticePipe oShape      = new LatticePipe(oLocalFrame, 60);
                        oShape.SetRadius(new LineModulation(fGetLineModulation1));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrFrozen);
                    }

                    {
                        // modulated + spined
                        ISpline oSpine          = new ExampleSpline();
                        Frames aFrames          = new Frames(oSpine.aGetPoints(), Vector3.UnitY);
                        LatticePipe oShape      = new LatticePipe(aFrames);
                        oShape.SetRadius(new LineModulation(fGetLineModulation1));
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrRacingGreen);
                    }

                    {
                        // spined
                        ISpline oSpine          = new ExampleSpline();
                        List<Vector3> aPoints   = SplineOperations.aTranslateList(oSpine.aGetPoints(), 50 * Vector3.UnitX);
                        Frames aFrames          = new Frames(aPoints, Vector3.UnitY);
                        LatticePipe oShape      = new LatticePipe(aFrames, 5f);
                        Voxels oVoxels          = oShape.voxConstruct();
                        Sh.PreviewVoxels(oVoxels, Cp.clrOrchid);
                    }
                }
                catch (Exception e)
                {
                    Library.Log($"Failed run example: \n{e.Message}"); ;
                }
            }

            // functions for generic line modulations
            public static float fGetLineModulation1(float fLengthRatio)
            {
                float fWidth = 10f - 3f * MathF.Cos(8f * fLengthRatio);
                return fWidth;
            }

            public static float fGetLineModulation2(float fLengthRatio)
            {
                float fDepth = 8f - 1f * MathF.Cos(40f * fLengthRatio);
                return fDepth;
            }
        }
    }
}
```

### Examples/Ex_MeshPainterShowCase.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this PicoGK Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using PicoGK;
using System.Numerics;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class MeshPainterShowCase
        {
            public static void Task()
            {
                // Step 1: Generate a three example meshes (e.g. from voxelfields)
                float fRadius               = 50f;
                BaseSphere oSphere1         = new BaseSphere(new LocalFrame(new Vector3(-120, 0, 0)), fRadius);
                BaseSphere oSphere2         = new BaseSphere(new LocalFrame(new Vector3(   0, 0, 0)), fRadius);
                BaseSphere oSphere3         = new BaseSphere(new LocalFrame(new Vector3(+120, 0, 0)), fRadius);
                Mesh msh1                   = new Mesh(oSphere1.voxConstruct());
                Mesh msh2                   = new Mesh(oSphere2.voxConstruct());
                Mesh msh3                   = new Mesh(oSphere3.voxConstruct());


                // Step 2: Show local overhang distribution on first mesh
                float fMinValue             =  0;   // deg
                float fMaxValue             = 90;   // deg
                bool bShowOnlyDownFacing    = false;
                uint nColorSteps            = 50;
                IColorScale xScale1         = new ColorScale3D(new RainboxSpectrum(), fMinValue, fMaxValue);
                MeshPainter.PreviewOverhangAngle(msh1, xScale1, bShowOnlyDownFacing, nColorSteps);


                // Step 3: Show critical overhang areas on second mesh
                float fCritAngle            = 30;   // deg
                float fTransitionSmooth     = 5;
                bShowOnlyDownFacing         = true;
                IColorScale xScale2         = new CustomColorScale2D(Cp.clrGreen, Cp.clrRed, fMinValue, fMaxValue, fCritAngle, fTransitionSmooth);
                MeshPainter.PreviewOverhangAngle(msh2, xScale2, bShowOnlyDownFacing, nColorSteps);

                
                // Step 4: Show custom property on third mesh
                fMinValue                   = 0;    // mm
                fMaxValue                   = 10;   // mm
                IColorScale xScale3         = new LinearColorScale2D(Cp.clrCrystal, Cp.clrPitaya, fMinValue, fMaxValue);
                MeshPainter.PreviewCustomProperty(msh3, xScale3, fGetExampleProperty, nColorSteps);
            }

            /// <summary>
            /// Example function to calculate a custom property of a given triangle.
            /// In this case, the x-coordinate of the triangle is evaluated in a modulus function.
            /// The output value of this function (with respect to the min and max value of the scale) will determine the color
            /// in which the triangle will be displayed.
            /// A, B, C are the input mesh triangle vertices.
            /// </summary>
            public static float fGetExampleProperty(Vector3 vecA, Vector3 vecB, Vector3 vecC)
            {
                Vector3 vecCentre   = (vecA + vecB + vecC) / 3f;
                float fValue        = (MathF.Abs(vecCentre.X) % 10);
                return fValue;
            }
        }
    }
}
```

### Examples/Ex_MeshTrafoShowCase.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this PicoGK Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using PicoGK;
using System.Numerics;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class MeshTrafoShowCase
        {
            public static void Task()
            {
                // Step 1: Generate a simple mesh (e.g. from voxelfields)
                BaseBox oBox                = new BaseBox(new LocalFrame(new Vector3(0, 100, 0)), 50, 40, 30);
                Voxels voxBox               = oBox.voxConstruct();
                Mesh mshBox                 = new Mesh(voxBox);


                // Step 2: Apply a vertex-wise transformation to the mesh
                // Select between the fnMirror and the fnRotate function
                // Mesh mshTrafoBox            = MeshUtility.mshApplyTransformation(mshBox, fnMirror);
                Mesh mshTrafoBox            = MeshUtility.mshApplyTransformation(mshBox, fnRotate);


                // Step 3: Voxelize transformed mesh (if needed)
                Voxels voxTrafoBox          = new Voxels(mshTrafoBox);
                Sh.PreviewVoxels(voxBox,      Cp.clrOrchid, 0.5f);
                Sh.PreviewVoxels(voxTrafoBox, Cp.clrOrchid, 1.0f);
            }

            /// <summary>
            /// Applies a transformation to the input vertex coordinates.
            /// Returns a new transformed point.
            /// This function mirrors the y-coordiante on the xz-plane.
            /// </summary>
            public static Vector3 fnMirror(Vector3 vecPt)
            {
                float fX            = vecPt.X;
                float fY            = vecPt.Y;
                float fZ            = vecPt.Z;
                float fMirrorPlaneY = 0;
                float fNewY         = fMirrorPlaneY - (fY - fMirrorPlaneY);
                Vector3 vecNewPt    = new Vector3(fX, fNewY, fZ);
                return vecNewPt;
            }

            /// <summary>
            /// Applies a transformation to the input vertex coordinates.
            /// Returns a new transformed point.
            /// This function rotates the point 45 deg around the z-axis.
            /// </summary>
            public static Vector3 fnRotate(Vector3 vecPt)
            {
                Vector3 vecAxis     = Vector3.UnitZ;
                float dPhi          = 45f / 180f * MathF.PI;
                Vector3 vecNewPt    = VecOperations.vecRotateAroundAxis(vecPt, dPhi, vecAxis);
                return vecNewPt;
            }
        }
    }
}
```

### Examples/Ex_OverOffsetShowCase.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this PicoGK Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using PicoGK;


namespace Leap71
{
    using ShapeKernel;

    namespace ShapeKernelExamples
    {
        class OverOffsetShowCase
        {
            public static void Task()
            {
                // Step 1: Generate a simple shape with convex and concave corners
                BaseBox oBox_01             = new BaseBox(new LocalFrame(), 10, 40, 30);
                BaseBox oBox_02             = new BaseBox(new LocalFrame(), 40, 40, 10);
                Voxels voxBox               = oBox_01.voxConstruct()
                                                + oBox_02.voxConstruct();
                
                // Step 2: Apply one of the below offset operations
                // Voxels voxNewBox          = voxBox.voxOffset(3f);
                Voxels voxNewBox          = voxBox.voxFillet(3f);
                // Voxels voxNewBox          = voxBox.voxFillet(-3f);
                // Voxels voxNewBox          = voxBox.voxSmoothen(3f);

                // Step 3: Visualize
                Sh.PreviewBoxWireframe(oBox_01, Cp.clrBlack);
                Sh.PreviewBoxWireframe(oBox_02, Cp.clrBlack);
                Sh.PreviewVoxels(voxNewBox, Cp.clrBubblegum, 1.0f);
            }
        }
    }
}
```

### Examples/ExampleSpline.cs

```csharp
//
// SPDX-License-Identifier: CC0-1.0
//
// This example code file is released to the public under Creative Commons CC0.
// See https://creativecommons.org/publicdomain/zero/1.0/legalcode
//
// To the extent possible under law, LEAP 71 has waived all copyright and
// related or neighboring rights to this LEAP 71 ShapeKernel Example Code.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//


using System.Numerics;


namespace Leap71
{
    namespace ShapeKernel
    {
        public class ExampleSpline : ISpline
        {
            protected ControlPointSpline m_oBSpline;

            /// <summary>
            /// This class gives an example of how control point splines can be generated.
            /// See: https://en.wikipedia.org/wiki/B-spline
            /// </summary>
            public ExampleSpline()
            {
                // Define a few control points in space via their x-y-z coordinates.
                List<Vector3> aControlPoints = new List<Vector3>() {
                    new Vector3(0, 0, 0),
                    new Vector3(0, 40, 0),
                    new Vector3(0, 50, 20),
                    new Vector3(0, 60, 60),
                };

                // Use a ControlPointSpline object (B-Spline) to derive a smooth curve from the control points.
                // This curve is continuous and can later be samples into a new point list.
                m_oBSpline = new ControlPointSpline(aControlPoints);
            }

            public List<Vector3> aGetPoints(uint nSamples = 500)
            {
                // Query 500 (or nSamples) point along the B-Spline.
                return m_oBSpline.aGetPoints(nSamples);
            }
        }
    }
}
```

---

## Anhang G: LICENSE

```text
Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
