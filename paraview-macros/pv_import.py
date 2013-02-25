at_vtk = LegacyVTKReader(FileNames='MgB2-atoms.vtk',registrationName="Input Atoms")
at_vtk.UpdatePipeline()
at_vtk.UpdatePipelineInformation()
loc_vtk = LegacyVTKReader(FileNames='MgB2-localization.vtk',registrationName="Input Densities") 
loc_vtk.UpdatePipeline()
loc_vtk.UpdatePipelineInformation()
GetDisplayProperties(loc_vtk).Representation='Outline'
Hide(loc_vtk)

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

t=Transform(loc_vtk)
GetDisplayProperties(t).Representation='Outline'
Hide(t)
density_trans=[t]

density_group=GroupDatasets(registrationName="Densities")
GetDisplayProperties(density_group).Representation='Outline'
density_group.Input=density_trans
Hide(density_group)

SetActiveSource(density_group)
LCalc = Calculator(density_group,registrationName="Localization Calculator",
        ResultArrayName = "Localization", Function = "+0.01_dos")
LCalc.UpdatePipeline()
LCalc.UpdatePipelineInformation()
dp=GetDisplayProperties(LCalc)
dp.Representation='Outline'
Hide(LCalc)

# loop over slices
lt = GetLookupTableForArray( "Localization", 1, Discretize=1,
        RGBPoints=[
            0.0000, 0.0, 0.0, 0.0,
            0.0012, 0.9019607843137255, 0.0, 0.0,
            0.0024, 0.9019607843137255, 0.9019607843137255, 0.0,
            0.0030, 1.0, 1.0, 1.0],
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
