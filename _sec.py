import sys
sys.path.insert(0, "ant-nest-reservoir")
import build, cadquery as cq, vtk

base = build.make_base()
glass = build.make_glass()
cq.exporters.export(build.make_hub(), "ant-nest-reservoir/output/_hub.stl")
half = cq.Workplane("XY").transformed(offset=(80, 40, -20)).box(400, 200, 40)
cq.exporters.export(base.intersect(half), "ant-nest-reservoir/output/_sb.stl")
cq.exporters.export(glass.intersect(half), "ant-nest-reservoir/output/_sg.stl")


def actor(path, rgb):
    r = vtk.vtkSTLReader(); r.SetFileName(path); r.Update()
    m = vtk.vtkPolyDataMapper(); m.SetInputConnection(r.GetOutputPort())
    a = vtk.vtkActor(); a.SetMapper(m); p = a.GetProperty()
    p.SetColor(*rgb); p.SetInterpolationToPhong(); p.SetSpecular(0.2); p.SetDiffuse(0.9); p.SetAmbient(0.35)
    return a


def render(parts, out, pos, foc, zoom, size=(1500, 1000)):
    ren = vtk.vtkRenderer(); ren.SetBackground(0.16, 0.17, 0.20); ren.SetBackground2(0.05, 0.05, 0.07); ren.GradientBackgroundOn()
    for path, rgb in parts: ren.AddActor(actor(path, rgb))
    vtk.vtkLightKit().AddLightsToRenderer(ren)
    win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.AddRenderer(ren); win.SetSize(*size)
    cam = ren.GetActiveCamera(); cam.SetPosition(*pos); cam.SetFocalPoint(*foc); cam.SetViewUp(0, 1, 0)
    ren.ResetCamera(); cam.Zoom(zoom); win.Render()
    w2i = vtk.vtkWindowToImageFilter(); w2i.SetInput(win); w2i.Update()
    wr = vtk.vtkPNGWriter(); wr.SetFileName(out); wr.SetInputConnection(w2i.GetOutputPort()); wr.Write(); print("wrote", out)


render([("ant-nest-reservoir/output/_sb.stl", (0.80, 0.82, 0.88)),
        ("ant-nest-reservoir/output/_sg.stl", (0.55, 0.85, 0.75))],
       "ant-nest-reservoir/output/preview-section.png", (70, 60, 340), (80, 38, 0), 1.7)
render([("ant-nest-reservoir/output/base.stl", (0.80, 0.82, 0.88)),
        ("ant-nest-reservoir/output/_hub.stl", (0.92, 0.72, 0.45))],
       "ant-nest-reservoir/output/preview-assembly.png", (240, 220, 260), (75, 35, 0), 1.3)
