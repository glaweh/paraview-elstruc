sourcedict = GetSources()
if (len(sourcedict) != 1):
    raise RuntimeError('Only the density file should be loaded')
density_vtk = sourcedict.values()[0]
SetActiveSource(density_vtk)
RenameSource("Input Densities")

import re
(filebase, filebase_rel) = \
    re.compile("^(.*/([^/]+))-[^/-]+\.vtk$").match(density_vtk.FileNames[0]).groups()
at_vtk = LegacyVTKReader(FileNames= filebase + '-atoms.vtk',registrationName="Input Atoms")
at_vtk.UpdatePipeline()
at_vtk.UpdatePipelineInformation()
density_vtk.UpdatePipeline()
density_vtk.UpdatePipelineInformation()
GetDisplayProperties(density_vtk).Representation='Outline'
Hide(density_vtk)

t=Transform(at_vtk)
GetDisplayProperties(t).Representation='Outline'
Hide(t)
atoms_trans = [t]

atoms_group=GroupDatasets(registrationName="Atoms")
GetDisplayProperties(atoms_group).Representation='Outline'
atoms_group.Input=atoms_trans
Hide(atoms_group)
SetActiveSource(atoms_group)
CovalentSpheres=Glyph(atoms_group,GlyphType='Sphere',registrationName="Covalent Spheres")
CovalentSpheres.Scalars='Covalent_radius'
CovalentSpheres.ScaleMode = 'scalar'
CovalentSpheres.SetScaleFactor=1
CovalentSpheres.UpdatePipeline
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
SetActiveSource(atoms_group)
Nuclei = Glyph(atoms_group,GlyphType='Sphere',registrationName="Nuclei")
dp=GetDisplayProperties(Nuclei)
dp.LookupTable = GetLookupTableForArray("Nuclear_charge", 1,
        RGBPoints = [1, 0, 0, 1, 100, 1, 0, 0],
        ColorSpace = "HSV")
dp.ColorAttributeType = 'POINT_DATA'
dp.ColorArrayName = 'Nuclear_charge'
Show(Nuclei)

t=Transform(density_vtk)
GetDisplayProperties(t).Representation='Outline'
Hide(t)
density_trans=[t]

densities=density_vtk.GetDataInformation().DataInformation.GetPointDataInformation()
dos_offset = -42.0
calc_function = 'd_vol'
offset_pattern = re.compile('^([+-]\d+\.\d+)_dos$')
for i in range(0,densities.GetNumberOfArrays()):
    this_dos_name   = densities.GetArrayInformation(i).GetName()
    m = offset_pattern.match(this_dos_name)
    if (m == None):
        continue
    this_dos_offset = float(m.group(1))
    dao = abs(this_dos_offset) - abs(dos_offset)
    if (dao > 0.001):
        continue
    elif (dao > -0.001):
        if (this_dos_offset > 0):
            continue
    dos_offset = this_dos_offset
    calc_function = this_dos_name + '/d_vol'

density_group=GroupDatasets(registrationName="Densities")
GetDisplayProperties(density_group).Representation='Outline'
density_group.Input=density_trans
Hide(density_group)

SetActiveSource(density_group)
LCalc = Calculator(density_group,registrationName="Localization Calculator",
        ResultArrayName = "Localization", Function = calc_function)
LCalc.UpdatePipeline()
LCalc.UpdatePipelineInformation()
dp=GetDisplayProperties(LCalc)
dp.Representation='Outline'
Hide(LCalc)

heatmap = [
   0.00000000000000000, 0.0, 0.0, 0.0,
   0.19999999999999999, 0.9019607843137255, 0.0, 0.0,
   0.39999999999999997, 0.9019607843137255, 0.9019607843137255, 0.0,
   0.50000000000000000, 1.0, 1.0, 1.0]

calcrange = LCalc.GetDataInformation().DataInformation.GetPointDataInformation().GetArrayInformation('CalcDensity').GetComponentRange(0)

scale = (calcrange[1]-calcrange[0])/(heatmap[12]-heatmap[0])
heatmap[0]  = calcrange[0]
heatmap[12] = calcrange[1]
heatmap[4]  = calcrange[0]+heatmap[4]*scale
heatmap[8]  = calcrange[0]+heatmap[8]*scale

# loop over slices
lt = GetLookupTableForArray( "Localization", 1, Discretize=1,
        RGBPoints=heatmap,
        UseLogScale=0, VectorComponent=0, NanColor=[0.0, 0.4980392156862745, 1.0],
        NumberOfTableValues=256, ColorSpace='RGB',
        VectorMode='Component',
        HSVWrap=0, ScalarRangeInitialized=1.0,
        LockScalarRange=1 )

SetActiveSource(LCalc)
s1 = Slice(LCalc,registrationName="Slice1")
s1.SliceType.Normal=[1.0,0,0]
dp=GetDisplayProperties(s1)
dp.LookupTable = lt
dp.ColorAttributeType = 'POINT_DATA'
dp.ColorArrayName = 'Localization'
Show(s1)

SetActiveSource(LCalc)
s2 = Slice(registrationName="Slice2")
s2.UpdatePipeline()
s2.SliceType.Normal=[0,1.0,0]
s2.SliceType.Origin=[0.214890843075848,3.13861703522885,0.0350842611973924]
dp=GetDisplayProperties(s2)
dp.LookupTable = lt
dp.ColorAttributeType = 'POINT_DATA'
dp.ColorArrayName = 'Localization'
Show(s2)

SetActiveSource(LCalc)
s3 = Slice(LCalc,registrationName="Slice3")
s3.SliceType.Normal=[0,0,1.0]
s3.SliceType.Origin=[0,0,3.45009528519176]
dp=GetDisplayProperties(s3)
dp.LookupTable = lt
dp.ColorAttributeType = 'POINT_DATA'
dp.ColorArrayName = 'Localization'
Show(s3)

SetActiveSource(None)
Render()
