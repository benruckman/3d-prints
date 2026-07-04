import sys, vtk

# usage: python3 _view.py out.png file1.stl:r,g,b file2.stl:r,g,b ...
OUT = sys.argv[1]
SPECS = sys.argv[2:] or ["ant-nest-reservoir/output/base.stl:0.75,0.77,0.83"]

readers = []
gb = [1e9, -1e9, 1e9, -1e9, 1e9, -1e9]
actors = []
for spec in SPECS:
    path, _, col = spec.partition(":")
    rgb = tuple(float(x) for x in col.split(",")) if col else (0.75, 0.77, 0.83)
    r = vtk.vtkSTLReader(); r.SetFileName(path); r.Update(); readers.append(r)
    b = r.GetOutput().GetBounds()
    gb = [min(gb[0], b[0]), max(gb[1], b[1]), min(gb[2], b[2]),
          max(gb[3], b[3]), min(gb[4], b[4]), max(gb[5], b[5])]
    m = vtk.vtkPolyDataMapper(); m.SetInputConnection(r.GetOutputPort())
    a = vtk.vtkActor(); a.SetMapper(m); p = a.GetProperty()
    p.SetColor(*rgb); p.SetInterpolationToPhong(); p.SetSpecular(0.2); p.SetDiffuse(0.9); p.SetAmbient(0.35)
    actors.append(a)
    e = vtk.vtkActor(); e.SetMapper(m); e.GetProperty().SetRepresentationToWireframe()
    e.GetProperty().SetColor(0.12, 0.12, 0.14); e.GetProperty().SetLineWidth(1.0)
    actors.append(e)

cx=(gb[0]+gb[1])/2; cy=(gb[2]+gb[3])/2; cz=(gb[4]+gb[5])/2
print("bounds X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f"%tuple(gb))
R=max(gb[1]-gb[0], gb[3]-gb[2], gb[5]-gb[4])*1.5

ren=vtk.vtkRenderer(); ren.SetBackground(0.18,0.19,0.22); ren.SetBackground2(0.05,0.05,0.07); ren.GradientBackgroundOn()
for a in actors: ren.AddActor(a)
vtk.vtkLightKit().AddLightsToRenderer(ren)
win=vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.AddRenderer(ren); win.SetSize(1500,950)
cam=ren.GetActiveCamera(); cam.SetPosition(cx-R*0.6, cy+R*0.9, cz+R); cam.SetFocalPoint(cx,cy,cz); cam.SetViewUp(0,1,0)
ren.ResetCamera(); win.Render()
w=vtk.vtkWindowToImageFilter(); w.SetInput(win); w.Update()
p=vtk.vtkPNGWriter(); p.SetFileName(OUT); p.SetInputConnection(w.GetOutputPort()); p.Write(); print("wrote",OUT)
