def extractData(genome):
    weight = int("00000000000000001111111111111111", 2) & genome
    sink_id = (int("00000000011111110000000000000000", 2) & genome) >> 16
    sink_type = (int("00000000100000000000000000000000", 2) & genome) >> 23
    source_id = (int("01111111000000000000000000000000", 2) & genome) >> 24
    source_type = (int("10000000000000000000000000000000", 2) & genome) >> 31
    # print([source_type, source_id, sink_type, sink_id, weight])
    if weight & (1 << 15):
        weight = weight ^ int("1111111111111111", 2)
        weight += 1
        weight = -weight
    return source_type, source_id, sink_type, sink_id, weight / 8192

arr = [[1, 21, [3249486400, 3973643456, 1564088291, 2651036644, 1306811208]],
[1, 24, [250026247, 762909962, 2640032043, 22611345, 678000061]]]

for ele in arr:
    for bele in ele[2]:
        x = extractData(bele)
        print(x)
    print()
