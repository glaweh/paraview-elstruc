from   paraview.simple import *
import PyQt4.QtGui
import re
import os

if (len(GetSources()) != 0):
    PyQt4.QtGui.QMessageBox.critical(None,'Error','Please start with a clean pipeline')
    raise RuntimeError('Please start with a clean pipeline')

filebase = ''

def ImportEspressoPP():
    density_filename=str(PyQt4.QtGui.QFileDialog.getOpenFileName(None,
            "Select density file",
            '',
            "All files (*.*);;VTK (*.vtk *.VTK)",
            "VTK (*.vtk *.VTK)"))
    global filebase
    (filebase, filebase_rel) = \
        re.compile("^(.*/([^/]+))-[^/-]+\.vtk$").match(density_filename).groups()
    density_vtk = LegacyVTKReader(FileNames= density_filename ,registrationName="Input Densities")
    density_vtk.UpdatePipeline()
    density_vtk.UpdatePipelineInformation()
    GetDisplayProperties(density_vtk).Representation='Outline'
    Hide(density_vtk)
    at_vtk = LegacyVTKReader(FileNames= filebase + '-atoms.vtk',registrationName="Input Atoms")
    at_vtk.UpdatePipeline()
    at_vtk.UpdatePipelineInformation()
    GetDisplayProperties(at_vtk).Representation='Outline'
    Hide(at_vtk)
    return filebase

def SetupAtomPipeline():
    at_vtk = FindSource("Input Atoms")
    if (at_vtk == None):
        raise RuntimeError('Missing "Input Atoms"')
    SetActiveSource(at_vtk)
    t=Transform(at_vtk,registrationName="tAtm %d, %d, %d" % (0,0,0))
    GetDisplayProperties(t).Representation='Outline'
    t.UpdatePipeline()
    t.UpdatePipelineInformation()
    Hide(t)
    atoms_group=GroupDatasets(registrationName="Atoms")
    GetDisplayProperties(atoms_group).Representation='Outline'
    atoms_group.Input=[t]
    Hide(atoms_group)
    atoms_group.UpdatePipeline()
    atoms_group.UpdatePipelineInformation()
    atoms_clip = Clip(atoms_group,registrationName="Clip")
    atoms_clip.ClipType='Box'
    atoms_clip.UpdatePipeline()
    atoms_clip.UpdatePipelineInformation()
    GetDisplayProperties(atoms_clip).Representation='Outline'
    Hide(atoms_clip)
    SetActiveSource(atoms_clip)
    CovalentSpheres=Glyph(atoms_clip,GlyphType='Sphere',registrationName="Covalent Spheres")
    CovalentSpheres.Scalars='Covalent_radius'
    CovalentSpheres.ScaleMode = 'scalar'
    CovalentSpheres.SetScaleFactor=1
    CovalentSpheres.GlyphType.PhiResolution=16
    CovalentSpheres.GlyphType.ThetaResolution=16
    CovalentSpheres.GlyphType.Radius=1
    dp=GetDisplayProperties(CovalentSpheres)
    dp.LookupTable = GetLookupTableForArray("Nuclear_charge", 1,
            RGBPoints = [1, 0, 0, 1, 100, 1, 0, 0],
            ColorSpace = "HSV")
    dp.ColorAttributeType = 'POINT_DATA'
    dp.ColorArrayName = 'Nuclear_charge'
    dp.Opacity = 0.4
    Hide(CovalentSpheres)
    SetActiveSource(atoms_clip)
    Nuclei = Glyph(atoms_clip,GlyphType='Sphere',registrationName="Nuclei")
    dp=GetDisplayProperties(Nuclei)
    dp.LookupTable = GetLookupTableForArray("Nuclear_charge", 1,
            RGBPoints = [1, 0, 0, 1, 100, 1, 0, 0],
            ColorSpace = "HSV")
    dp.ColorAttributeType = 'POINT_DATA'
    dp.ColorArrayName = 'Nuclear_charge'
    Show(Nuclei)

def SetupDensityPipeline():
    density_vtk = FindSource("Input Densities")
    if (density_vtk == None):
        raise RuntimeError('Missing "Input Densities"')
    SetActiveSource(density_vtk)
    t=Transform(density_vtk,registrationName="tDen %d, %d, %d" % (0,0,0) )
    GetDisplayProperties(t).Representation='Outline'
    t.UpdatePipeline()
    t.UpdatePipelineInformation()
    Hide(t)
    density_group=GroupDatasets(registrationName="Densities")
    GetDisplayProperties(density_group).Representation='Outline'
    density_group.Input=[t]
    Hide(density_group)
    density_group.UpdatePipeline()
    density_group.UpdatePipelineInformation()
    calc_function=DefaultDensity(density_group)
    if (calc_function == ''):
        calc_function = '1'
    SetActiveSource(density_group)
    DCalc = Calculator(density_group,registrationName="Density Calculator",
            ResultArrayName = "CalcDensity", Function = calc_function)
    DCalc.UpdatePipeline()
    DCalc.UpdatePipelineInformation()
    GetDisplayProperties(DCalc).Representation='Outline'
    Show(DCalc)
    SetupDensitySlices(DCalc,"CalcDensity")

def SetupDensitySlices(data,field):
    heatmap = [
       0.00000000000000000, 0.0, 0.0, 0.0,
       0.19999999999999999, 0.9019607843137255, 0.0, 0.0,
       0.39999999999999997, 0.9019607843137255, 0.9019607843137255, 0.0,
       0.50000000000000000, 1.0, 1.0, 1.0]
    calcrange = data.GetDataInformation().DataInformation.GetPointDataInformation().GetArrayInformation('CalcDensity').GetComponentRange(0)
    scale = (calcrange[1]-calcrange[0])/(heatmap[12]-heatmap[0])
    heatmap[0]  = calcrange[0]
    heatmap[12] = calcrange[1]
    heatmap[4]  = calcrange[0]+heatmap[4]*scale
    heatmap[8]  = calcrange[0]+heatmap[8]*scale
    lt = GetLookupTableForArray( field, 1, Discretize=1,
        RGBPoints=heatmap,
        UseLogScale=0, VectorComponent=0, NanColor=[0.0, 0.4980392156862745, 1.0],
        NumberOfTableValues=256, ColorSpace='RGB',
        VectorMode='Component',
        HSVWrap=0, ScalarRangeInitialized=1.0,
        LockScalarRange=1 )
    # Workaround: if theres no overlap between slice and data, PV fails to see
    # the input field used for coloring
    #
    # calculate the center
    src = FindSource('Input Densities')
    density_info   = src.GetClientSideObject().GetOutput()
    density_extent = density_info.GetExtent()
    at = [ [42,42,42],[42,42,42],[42,42,42] ]
    density_info.GetPoint(density_extent[1],0,0,at[0],1)
    density_info.GetPoint(0,density_extent[3],0,at[1],1)
    density_info.GetPoint(0,0,density_extent[5],at[2],1)
    center = [
            (at[0][0]+at[1][0]+at[2][0])/2,
            (at[0][1]+at[1][1]+at[2][1])/2,
            (at[0][2]+at[1][2]+at[2][2])/2
        ]
    # loop over slices
    f = open(filebase + '-cutplanes.tsv')
    i = 0
    for line in f:
        sp = map(float,line.split())
        SetActiveSource(data)
        i=i+1
        s=Slice(data,registrationName="Plane%d" % i)
        s.SliceType.Normal=[ sp[0],sp[1],sp[2] ]
        # Workaround1: shift Slice origin to cell center before assigning
        # ColorArrayName
        s.SliceType.Origin=center
        s.UpdatePipelineInformation()
        dp=GetDisplayProperties(s)
        dp.LookupTable = lt
        dp.ColorAttributeType = 'POINT_DATA'
        dp.ColorArrayName = field
        # Workaround2: shift Slice origin to the desired point
        s.SliceType.Origin=[ sp[3],sp[4],sp[5] ]
        Hide(s)

def DefaultDensity(density_group):
    densities=density_group.GetDataInformation().DataInformation.GetPointDataInformation()
    result = ''
    dos_offset = -42.0
    offset_pattern = re.compile('^([pm])(\d+\.\d+)_dos$')
    for i in range(0,densities.GetNumberOfArrays()):
        this_dos_name   = densities.GetArrayInformation(i).GetName()
        m = offset_pattern.match(this_dos_name)
        if (m == None):
            continue
        this_dos_offset = float(m.group(2))
        if (m.group(1) == 'm'):
            this_dos_offset = -this_dos_offset
        dao = abs(this_dos_offset) - abs(dos_offset)
        if (dao > 0.001):
            continue
        elif (dao > -0.001):
            if (this_dos_offset > 0):
                continue
        dos_offset = this_dos_offset
        result = this_dos_name
    return result

ImportEspressoPP()
SetupAtomPipeline()
SetupDensityPipeline()
SetActiveSource(None)
Render()
