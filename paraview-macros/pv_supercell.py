from paraview.simple import *
import PyQt4.QtGui
import re

def SetupSupercell():
    super_dim   = [ 2, 2, 2]
    density_vtk = FindSource("Input Densities")
    if (density_vtk == None):
        PyQt4.QtGui.QMessageBox.critical(None,'Error','Cannot find "Input Densities" in pipeline.')
        raise RuntimeError('Cannot find "Input Densities" in pipeline.')
    density_group = FindSource("Densities")
    if (density_group == None):
        PyQt4.QtGui.QMessageBox.critical(None,'Error','Cannot find "Densities" in pipeline.')
        raise RuntimeError('Cannot find "Densities" in pipeline.')
    atoms_vtk = FindSource("Input Atoms")
    if (atoms_vtk == None):
        PyQt4.QtGui.QMessageBox.critical(None,'Error','Cannot find "Input Atoms" in pipeline.')
        raise RuntimeError('Cannot find "Input Atoms" in pipeline.')
    atoms_group = FindSource("Atoms")
    if (atoms_group == None):
        PyQt4.QtGui.QMessageBox.critical(None,'Error','Cannot find "Atoms" in pipeline.')
        raise RuntimeError('Cannot find "Atoms" in pipeline.')
    density_info   = density_vtk.GetClientSideObject().GetOutput()
    density_extent = density_info.GetExtent()
    at = [ [42,42,42],[42,42,42],[42,42,42] ]
    density_info.GetPoint(density_extent[1],0,0,at[0],1)
    density_info.GetPoint(0,density_extent[3],0,at[1],1)
    density_info.GetPoint(0,0,density_extent[5],at[2],1)
    (v,s)=PyQt4.QtGui.QInputDialog.getInteger(None,'N1','N1',2,1,4)
    if (not s):
        raise RuntimeError('User abort.')
    super_dim[0]=v
    (v,s)=PyQt4.QtGui.QInputDialog.getInteger(None,'N2','N2',2,1,4)
    if (not s):
        raise RuntimeError('User abort.')
    super_dim[1]=v
    (v,s)=PyQt4.QtGui.QInputDialog.getInteger(None,'N3','N3',2,1,4)
    if (not s):
        raise RuntimeError('User abort.')
    super_dim[2]=v
    i=0
    for t in density_group.Input.GetData():
        if (i==0):
            i=1
            continue
        density_group.Input.remove(t)
        Delete(t)
    i=0
    for t in atoms_group.Input.GetData():
        if (i==0):
            i=1
            continue
        atoms_group.Input.remove(t)
        Delete(t)
    for i in range(0,super_dim[0]):
        for j in range(0,super_dim[1]):
            for k in range(0,super_dim[2]):
                if (i==0 and j==0 and k==0):
                    continue
                delta = [ 0.0,0.0,0.0 ]
                for ii in range(0,3):
                    delta[ii] = i*at[0][ii] + j*at[1][ii] + k * at[2][ii]
                SetActiveSource(density_vtk)
                t=Transform(density_vtk,registrationName="tDen %d, %d, %d" % (i,j,k) )
                t.Transform.Translate=delta
                GetDisplayProperties(t).Representation='Outline'
                Hide(t)
                density_group.Input.append(t)
                SetActiveSource(atoms_vtk)
                t=Transform(atoms_vtk,registrationName="tAtm %d, %d, %d" % (i,j,k))
                t.Transform.Translate=delta
                GetDisplayProperties(t).Representation='Outline'
                Hide(t)
                atoms_group.Input.append(t)
    # update stuff due to buggy gui feedback
    s=GetSources()
    filter_plane = re.compile("^Plane")
    for k in s.keys():
        if (filter_plane.match(k[0])):
            n=s[k].SliceType.Normal.GetData()
            s[k].SliceType.Normal=[1,0,0]
            s[k].SliceType.Normal=n
    SetActiveSource(None)
    Render()

SetupSupercell()
