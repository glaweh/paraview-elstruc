super_dim = [ 1, 2, 2]

density_info   = density_vtk.GetClientSideObject().GetOutput()
density_extent = density_info.GetExtent()
at = [ [42,42,42],[42,42,42],[42,42,42] ]
density_info.GetPoint(density_extent[1],0,0,at[0],1)
density_info.GetPoint(0,density_extent[3],0,at[1],1)
density_info.GetPoint(0,0,density_extent[5],at[2],1)

density_group.Input=[]
for t in density_trans:
    Delete(t)
atoms_group.Input=[]
for t in atoms_trans:
    Delete(t)
density_trans = []
atoms_trans = []
for i in range(0,super_dim[0]):
    for j in range(0,super_dim[1]):
        for k in range(0,super_dim[2]):
            delta = [ 0.0,0.0,0.0 ]
            for ii in range(0,3):
                delta[ii] = i*at[0][ii] + j*at[1][ii] + k * at[2][ii]
            SetActiveSource(density_vtk)
            t=Transform(density_vtk,registrationName="tDen %d, %d, %d" % (i,j,k) )
            t.Transform.Translate=delta
            GetDisplayProperties(t).Representation='Outline'
            Hide(t)
            density_trans.append(t)
            SetActiveSource(at_vtk)
            t=Transform(at_vtk,registrationName="tAtm %d, %d, %d" % (i,j,k))
            t.Transform.Translate=delta
            GetDisplayProperties(t).Representation='Outline'
            Hide(t)
            atoms_trans.append(t)

density_group.Input=density_trans
atoms_group.Input=atoms_trans
SetActiveSource(None)
Render()
