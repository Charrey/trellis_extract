import pytrellis
import database

pytrellis.load_database(database.get_db_root())
chip = pytrellis.Chip("LFE5U-12F")
graph = chip.get_routing_graph()
tile = graph.tiles[pytrellis.Location(12, 6)]

def rid_to_arc(routingId):
    return graph.tiles[routingId.loc].arcs[routingId.id]

def rid_to_wire(routingId):
    return graph.tiles[routingId.loc].wires[routingId.id]

def rid_to_bel(bel):
    return graph.tiles[bel.loc].bels[bel.id]

routingBelIds = dict()
routingPortIds = dict()
routingArcIds = dict()
routingWiresIds = dict()
foreignRoutingWiresIds = dict()
counter = 0

toBeMatched = set()
for arc in [x.data() for x in tile.arcs if x.data().source.loc == tile.loc and (
        x.data().sink.loc == tile.loc or x.data().sink.loc == pytrellis.Location(13, 6))]:
    if arc.sink.loc == pytrellis.Location(13, 6) and arc.sink.id not in foreignRoutingWiresIds:
        toBeMatched.add(arc.sink.id)
toBeMatchedCounter = 0

with open("/media/sf_Shared_folder/singleTile.dot", "w") as file:
    file.write("strict digraph G {\n")
    for bel in [x.data() for x in tile.bels]:
        assert bel.name not in routingBelIds
        routingBelIds[bel.name] = counter
        file.write("\t" + str(counter) + " [label=\"" + graph.to_str(bel.type) + "\"];\n")
        counter += 1
        for port in [x for x in bel.pins]:
            assert (bel.name, port.key()) not in routingPortIds
            routingPortIds[(bel.name, port.key())] = counter
            assert port.data().wire.loc == tile.loc
            file.write("\t" + str(routingPortIds[(bel.name, port.key())]) + " [label=\"port\"];\n")
            if port.data().dir == pytrellis.PortDirection.PORT_IN:
                assert port.key() in [z.pin for z in list(rid_to_wire(port.data().wire).belsUphill)]  # this is weird
                file.write(
                    "\t" + str(routingPortIds[(bel.name, port.key())]) + " -> " + str(routingBelIds[bel.name]) + ";\n")
            elif port.data().dir == pytrellis.PortDirection.PORT_OUT:
                assert port.key() in [z.pin for z in list(rid_to_wire(port.data().wire).belsDownhill)]  # this is weird
                file.write(
                    "\t" + str(routingBelIds[bel.name]) + " -> " + str(routingPortIds[(bel.name, port.key())]) + ";\n")
            else:
                assert False
            counter += 1
    for wire in [x.data() for x in tile.wires]:
        labelText = "wire"
        if wire.id in toBeMatched:
            labelText = "matchfrom_" + str(toBeMatchedCounter)
            toBeMatchedCounter += 1
        assert len(wire.belsDownhill) > 0 or len(wire.belsUphill) > 0 or len(wire.uphill) > 0 or len(wire.downhill) > 0
        assert len([x for x in list(wire.uphill) + list(wire.downhill) if x.loc == tile.loc]) > 0
        assert wire.id not in routingWiresIds
        routingWiresIds[wire.id] = counter
        file.write("\t" + str(counter) + " [label=\"" + labelText + "\", name=\"" + graph.to_str(wire.id) + "\"];\n")
        counter += 1
        for pin in wire.belsDownhill:  # remember, this is illogical. Downhill means itś coming from below.
            file.write(
                "\t" + str(routingPortIds[(pin.bel.id, pin.pin)]) + " -> " + str(routingWiresIds[wire.id]) + ";\n")
        for pin in wire.belsUphill:  # remember, this is illogical. Uphill means itś goin up.
            file.write(
                "\t" + str(routingWiresIds[wire.id]) + " -> " + str(routingPortIds[(pin.bel.id, pin.pin)]) + ";\n")
    toBeMatchedCounter = 0
    for arc in [x.data() for x in tile.arcs if x.data().source.loc == tile.loc and (
            x.data().sink.loc == tile.loc or x.data().sink.loc == pytrellis.Location(13, 6))]:
        assert arc.id not in routingArcIds
        routingArcIds[arc.id] = counter
        file.write("\t" + str(counter) + " [label=\"arc\", configurable=\"" + str(1 if arc.configurable else 0) + "\"];\n")
        counter += 1
        file.write("\t" + str(routingWiresIds[arc.source.id]) + " -> " + str(routingArcIds[arc.id]) + ";\n")
        if arc.sink.loc == pytrellis.Location(13, 6) and arc.sink.id not in foreignRoutingWiresIds:
            if arc.sink.id not in foreignRoutingWiresIds:
                assert arc.sink.id not in foreignRoutingWiresIds
                foreignRoutingWiresIds[arc.sink.id] = counter
                file.write("\t" + str(foreignRoutingWiresIds[arc.sink.id]) + " [label=\"matchto_" + str(toBeMatchedCounter) + "\", name=\"" + graph.to_str(arc.sink.id) + "\"];\n")
                counter += 1
                toBeMatchedCounter += 1
            file.write("\t" + str(routingArcIds[arc.id]) + " -> " + str(foreignRoutingWiresIds[arc.sink.id]) + ";\n")
        else:
            file.write("\t" + str(routingArcIds[arc.id]) + " -> " + str(routingWiresIds[arc.sink.id]) + ";\n")
    file.write("}")