#!/usr/bin/env python

##Copyright 2008-2015 Jelle Feringa (jelleferinga@gmail.com)
##
##This file is part of pythonOCC.
##
##pythonOCC is free software: you can redistribute it and/or modify
##it under the terms of the GNU Lesser General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##pythonOCC is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU Lesser General Public License for more details.
##
##You should have received a copy of the GNU Lesser General Public License
##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

'''
TODO:
Hide WireExplorer...
BRepTools.Map3DEdges()
History:
        20-01-2009:    initial version
        23-03-2009:    completed and updated for modular pythonOCC build
        23-04-2009:    fixed a reference issue ( fixed using ReInit )
'''
from __future__ import print_function

import sys
import itertools

from OCC.TopAbs import *
from OCC.TopExp import *
from OCC.TopoDS import *
from OCC.TopTools import *
from OCC.BRepTools import *
from OCC.BRep import *
__all__ = ['Topo', 'WireExplorer']


class WireExplorer(object):
    '''   '''
    def __init__(self, wire):
        assert isinstance(wire, TopoDS_Wire), 'not a TopoDS_Wire'
        self.wire = wire
        self.wire_explorer = BRepTools_WireExplorer(self.wire)
        self.done = False

    def _reinitialize(self):
        self.wire_explorer = BRepTools_WireExplorer(self.wire)
        self.done = False

    def _loop_topo(self, edges=True):
        if self.done:
            self._reinitialize()
        topologyType = topods_Edge if edges else topods_Vertex
        seq = []
        hashes = []  # list that stores hashes to avoid redundancy
        occ_seq = TopTools_ListOfShape()
        while self.wire_explorer.More():
            # loop edges
            if edges:
                current_item = self.wire_explorer.Current()
            # loop vertices
            else:
                current_item = self.wire_explorer.CurrentVertex()
            current_item_hash = current_item.__hash__()
            if not current_item_hash in hashes:
                hashes.append(current_item_hash)
                occ_seq.Append(current_item)
            self.wire_explorer.Next()

        # Convert occ_seq to python list
        occ_iterator = TopTools_ListIteratorOfListOfShape(occ_seq)
        while occ_iterator.More():
            topo_to_add = topologyType(occ_iterator.Value())
            seq.append(topo_to_add)
            occ_iterator.Next()
        self.done = True
        return iter(seq)

    def ordered_edges(self):
        return self._loop_topo(edges=True)

    def ordered_vertices(self):
        return self._loop_topo(edges=False)


class Topo(object):
    '''
    sketch for a pythonic topology wrapper
    note that `myShape` should be self, which is in return a occ.TopoShape
    with this
    '''
    def __init__(self, myShape):
        self.myShape = myShape

    def _loop_topo(self, topologyType, topologicalEntity=None, topologyTypeToAvoid=None):
        '''
        this could be a faces generator for a python TopoShape class
        that way you can just do:
        for face in srf.faces:
            processFace(face)
        '''
        topoTypes = {TopAbs_VERTEX:      topods_Vertex,
                     TopAbs_EDGE:        topods_Edge,
                     TopAbs_FACE:        topods_Face,
                     TopAbs_WIRE:        topods_Wire,
                     TopAbs_SHELL:       topods_Shell,
                     TopAbs_SOLID:       topods_Solid,
                     TopAbs_COMPOUND:    topods_Compound,
                     TopAbs_COMPSOLID:   topods_CompSolid}
        assert topologyType in topoTypes.keys(), '%s not one of %s' % (topologyType, topoTypes.keys())   
        self.topExp = TopExp_Explorer()
        # use self.myShape if nothing is specified
        if topologicalEntity is None and topologyTypeToAvoid is None:
            self.topExp.Init(self.myShape, topologyType)
        elif topologicalEntity is None and topologyTypeToAvoid is not None:
            self.topExp.Init(self.myShape, topologyType, topologyTypeToAvoid)
        elif topologyTypeToAvoid is None:
            self.topExp.Init(topologicalEntity, topologyType)
        elif topologyTypeToAvoid:
            self.topExp.Init(topologicalEntity, topologyType, topologyTypeToAvoid)
        seq = []
        hashes = []  # list that stores hashes to avoid redundancy
        occ_seq = TopTools_ListOfShape()
        while self.topExp.More():
            current_item = self.topExp.Current()
            current_item_hash = current_item.__hash__()
            if not current_item_hash in hashes:
                hashes.append(current_item_hash)
                occ_seq.Append(current_item)
            self.topExp.Next()
        # Convert occ_seq to python list
        occ_iterator = TopTools_ListIteratorOfListOfShape(occ_seq)
        while occ_iterator.More():
            topo_to_add = topoTypes[topologyType](occ_iterator.Value())
            seq.append(topo_to_add)
            occ_iterator.Next()
        return iter(seq)

    def faces(self):
        '''
        loops over all faces
        '''
        return self._loop_topo(TopAbs_FACE)

    def _number_of_topo(self, iterable):
        n = 0
        for i in iterable:
            n += 1
        return n

    def number_of_faces(self):
        return self._number_of_topo(self.faces())

    def vertices(self):
        '''
        loops over all vertices
        '''
        return self._loop_topo(TopAbs_VERTEX)

    def number_of_vertices(self):
        return self._number_of_topo(self.vertices())

    def edges(self):
        '''
        loops over all edges
        '''
        return self._loop_topo(TopAbs_EDGE)

    def number_of_edges(self):
        return self._number_of_topo(self.edges())

    def wires(self):
        '''
        loops over all wires
        '''
        return self._loop_topo(TopAbs_WIRE)

    def number_of_wires(self):
        return self._number_of_topo(self.wires())

    def shells(self):
        '''
        loops over all shells
        '''
        return self._loop_topo(TopAbs_SHELL, None)

    def number_of_shells(self):
        return self._number_of_topo(self.shells())

    def solids(self):
        '''
        loops over all solids
        '''
        return self._loop_topo(TopAbs_SOLID, None)

    def number_of_solids(self):
        return self._number_of_topo(self.solids())

    def comp_solids(self):
        '''
        loops over all compound solids
        '''
        return self._loop_topo(TopAbs_COMPSOLID)

    def number_of_comp_solids(self):
        return self._number_of_topo(self.comp_solids())

    def compounds(self):
        '''
        loops over all compounds
        '''
        return self._loop_topo(TopAbs_COMPOUND)

    def number_of_compounds(self):
        return self._number_of_topo(self.compounds())

    def ordered_vertices_from_wire(self, wire):
        '''
        @param wire: TopoDS_Wire
        '''
        we = WireExplorer(wire)
        return we.ordered_vertices()

    def number_of_ordered_vertices_from_wire(self, wire):
        return self._number_of_topo(self.ordered_vertices_from_wire(wire))

    def ordered_edges_from_wire(self, wire):
        '''
        @param wire: TopoDS_Wire
        '''
        we = WireExplorer(wire)
        return we.ordered_edges()

    def number_of_ordered_edges_from_wire(self, wire):
        return self._number_of_topo(self.ordered_edges_from_wire(wire))

    def _map_shapes_and_ancestors(self, topoTypeA, topoTypeB, topologicalEntity):
        '''
        using the same method
        @param topoTypeA:
        @param topoTypeB:
        @param topologicalEntity:
        '''
        topo_set = set()
        _map = TopTools_IndexedDataMapOfShapeListOfShape()
        topexp_MapShapesAndAncestors(self.myShape, topoTypeA, topoTypeB, _map)
        results = _map.FindFromKey(topologicalEntity)
        if results.IsEmpty():
            yield None
        topoTypes = {TopAbs_VERTEX:      topods_Vertex,
                     TopAbs_EDGE:        topods_Edge,
                     TopAbs_FACE:        topods_Face,
                     TopAbs_WIRE:        topods_Wire,
                     TopAbs_SHELL:       topods_Shell,
                     TopAbs_SOLID:       topods_Solid,
                     TopAbs_COMPOUND:    topods_Compound,
                     TopAbs_COMPSOLID:   topods_CompSolid}
        topology_iterator = TopTools_ListIteratorOfListOfShape(results)
        while topology_iterator.More():
            topo_entity = topoTypes[topoTypeB](topology_iterator.Value())
            # return the entity if not in set
            # to assure we're not returning entities several times
            if not topo_entity in topo_set:
                yield topo_entity
            topo_set.add(topo_entity)
            topology_iterator.Next()

    def _number_shapes_ancestors(self, topoTypeA, topoTypeB, topologicalEntity):
        '''returns the number of shape ancestors
        If you want to know how many edges a faces has:
        _number_shapes_ancestors(self, TopAbs_EDGE, TopAbs_FACE, edg)
        will return the number of edges a faces has
        @param topoTypeA:
        @param topoTypeB:
        @param topologicalEntity:
        '''
        topo_set = set()
        _map = TopTools_IndexedDataMapOfShapeListOfShape()
        topexp_MapShapesAndAncestors(self.myShape, topoTypeA, topoTypeB, _map)
        results = _map.FindFromKey(topologicalEntity)
        if results.IsEmpty():
            return None
        topology_iterator = TopTools_ListIteratorOfListOfShape(results)
        while topology_iterator.More():
            topo_set.add(topology_iterator.Value())
            topology_iterator.Next()
        return len(topo_set)

#==========================================================================
# EDGE <-> FACE
#==========================================================================
    def faces_from_edge(self, edge):
        return self._map_shapes_and_ancestors(TopAbs_EDGE, TopAbs_FACE, edge)

    def number_of_faces_from_edge(self, edge):
        return self._number_shapes_ancestors(TopAbs_EDGE, TopAbs_FACE, edge)

    def edges_from_face(self, face):
        return self._loop_topo(TopAbs_EDGE, face)

    def number_of_edges_from_face(self, face):
        cnt = 0
        for i in self._loop_topo(TopAbs_EDGE, face):
            cnt += 1
        return cnt

#===========================================================================
# VERTEX <-> EDGE
#===========================================================================
    def vertices_from_edge(self, edg):
        return self._loop_topo(TopAbs_VERTEX, edg)

    def number_of_vertices_from_edge(self, edg):
        cnt = 0
        for i in self._loop_topo(TopAbs_VERTEX, edg):
            cnt += 1
        return cnt

    def edges_from_vertex(self, vertex):
        return self._map_shapes_and_ancestors(TopAbs_VERTEX, TopAbs_EDGE, vertex)

    def number_of_edges_from_vertex(self, vertex):
        return self._number_shapes_ancestors(TopAbs_VERTEX, TopAbs_EDGE, vertex)

#===========================================================================
# WIRE <-> EDGE
#===========================================================================
    def edges_from_wire(self, wire):
        return self._loop_topo(TopAbs_EDGE, wire)

    def number_of_edges_from_wire(self, wire):
        cnt = 0
        for i in self._loop_topo(TopAbs_EDGE, wire):
            cnt += 1
        return cnt

    def wires_from_edge(self, edg):
        return self._map_shapes_and_ancestors(TopAbs_EDGE, TopAbs_WIRE, edg)

    def number_of_wires_from_edge(self, edg):
        return self._number_shapes_ancestors(TopAbs_EDGE, TopAbs_WIRE, edg)

#===========================================================================
# WIRE <-> FACE
#===========================================================================
    def wires_from_face(self, face):
        return self._loop_topo(TopAbs_WIRE, face)

    def number_of_wires_from_face(self, face):
        cnt = 0
        for i in self._loop_topo(TopAbs_WIRE, face):
            cnt += 1
        return cnt

    def faces_from_wire(self, wire):
        return self._map_shapes_and_ancestors(TopAbs_WIRE, TopAbs_FACE, wire)

    def number_of_faces_from_wires(self, wire):
        return self._number_shapes_ancestors(TopAbs_WIRE, TopAbs_FACE, wire)

#===========================================================================
# VERTEX <-> FACE
#===========================================================================
    def faces_from_vertex(self, vertex):
        return self._map_shapes_and_ancestors(TopAbs_VERTEX, TopAbs_FACE, vertex)

    def number_of_faces_from_vertex(self, vertex):
        return self._number_shapes_ancestors(TopAbs_VERTEX, TopAbs_FACE, vertex)

    def vertices_from_face(self, face):
        return self._loop_topo(TopAbs_VERTEX, face)

    def number_of_vertices_from_face(self, face):
        cnt = 0
        for i in self._loop_topo(TopAbs_VERTEX, face):
            cnt += 1
        return cnt

#===========================================================================
# FACE <-> SOLID
#===========================================================================
    def solids_from_face(self, face):
        return self._map_shapes_and_ancestors(TopAbs_FACE, TopAbs_SOLID, face)

    def number_of_solids_from_face(self, face):
        return self._number_shapes_ancestors(TopAbs_FACE, TopAbs_SOLID, face)

    def faces_from_solids(self, solid):
        return self._loop_topo(TopAbs_FACE, solid)

    def number_of_faces_from_solids(self, solid):
        cnt = 0
        for i in self._loop_topo(TopAbs_FACE, solid):
            cnt += 1
        return cnt


def dumpTopology(shape, level=0):
    """
     Print the details of an object from the top down
    """
    brt = BRep_Tool()
    s = shape.ShapeType()
    print("." * level, end="")
    print(shapeTypeString(shape), end="")
    if s == TopAbs_VERTEX:
        pnt = brt.Pnt(topods_Vertex(shape))
        print("<Vertex: %s %s %s>" % (pnt.X(), pnt.Y(), pnt.Z()))
    it = TopoDS_Iterator(shape)
    while it.More():
        shp = it.Value()
        it.Next()
        dumpTopology(shp, level + 1)


def shapeTypeString(shape):
    st = shape.ShapeType()
    s = "?"
    if st == TopAbs_VERTEX:
        s = "Vertex"
    if st == TopAbs_SOLID:
        s = "Solid"
    if st == TopAbs_EDGE:
        s = "Edge"
    if st == TopAbs_FACE:
        s = "Face"
    if st == TopAbs_SHELL:
        s = "Shell"
    if st == TopAbs_WIRE:
        s = "Wire"
    if st == TopAbs_COMPOUND:
        s = "Compound."
    if st == TopAbs_COMPSOLID:
        s = "Compsolid."
    return s + ":" + str(shape.HashCode(23232232))
