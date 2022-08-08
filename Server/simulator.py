import random
from Simulator.brain import *

from flask import Flask, jsonify, make_response
from flask_cors import CORS
import json
import gzip
# random.seed(19)




app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
def hello_world():
    return "<p>Home Page</p>"


def generate_population(sz):
    choices = np.random.choice(ALL_CELLS, size=sz, replace=False)
    arr = [Creature(ele['x'], ele['y'], [random.randint(1, int("ffffffff",16)) for _ in range(BRAIN_SIZE)]) for ele in choices]
    for ele in arr:
        grid.GRID_CELLS[ele.x][ele.y].isOccupied = True
    return arr


def load_data():
    try:
        with open("data.dat", "rb") as f:
            creatures,gens = pickle.load(f)
    except:
        gens = 0
        creatures = []
    return creatures,gens


def save_data(data):
    with open("data.dat", "wb") as f:
        pickle.dump(data, f)


@app.route("/test", methods=['POST'])
def test():
    global subsequent, gens
    arr = []
    n = 1
    # if subsequent: n = 1
    itera = 0
    surv = 1000
    while itera < n:
        if subsequent:
            surv = run_natural_selection()
            gens+=1
        for i in range(300):
            temp = []
            if itera == n-1:
                for elem in creatures:
                    temp.append({'x': elem.x, 'y': elem.y, 'g': elem.genomeCol})

                arr.append(temp)
            for elem in creatures:
                elem.think()
        subsequent = True
        itera += 1

    stats = surv
    content = gzip.compress(json.dumps({"d":arr, "s":[stats, gens]}).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response


@app.route("/save", methods=['GET'])
def save():
    print("Saving")
    save_data([creatures, gens])
    return jsonify(0)


def reproduce(ele, mutate_this=True):
    gene = ele.genome[:]
    # ele.genome_copied += 1
    mutate = 0
    if mutate_this:
        mutate = applyMutations(gene)

    return Creature(ele.x, ele.y, gene), mutate


def run_natural_selection():
    global creatures, ALL_CELLS
    choices = np.random.choice(ALL_CELLS, size=POPULATION, replace=False)
    for ele in grid.GRID_CELLS:
        for bele in ele:
            bele.isOccupied = False
    # choices = random.sample(ALL_CELLS, k=POPULATION)
    brr = []
    surv = 0
    for ele in creatures:
        if condition(ele):
            surv += 1
            brr.append(ele)

    creatures = brr
    brr = []
    random.shuffle(creatures)
    mutated_genes = 0
    for ele in creatures:
        cret, mut = reproduce(ele)
        brr.append(cret)

    for ele in creatures:
        rg = random.randint(0,2)
        for _ in range(rg):
            cret, mut = reproduce(ele)
            mutated_genes += mut
            brr.append(cret)

    while len(brr) < POPULATION:
        chc = random.choice(creatures)
        rep, mut = reproduce(chc)
        mutated_genes += mut
        brr.append(rep)

    random.shuffle(brr)
    if len(brr) > POPULATION:
        brr = brr[:POPULATION]
    for i,ele in enumerate(brr):
        ele.x = choices[i]['x']
        ele.y = choices[i]['y']
        # print(ele.genome)
    print(f"Mutated Genes in generation {gens}: {mutated_genes}")
    creatures = brr
    return surv


def randomBitFlip(genome):
    elementIndex = random.randint(0, len(genome) - 1)
    flipper = random.randint(0, 7)
    chance = random.random()
    if chance < 0.2: # sourceType
        genome[elementIndex] ^= (1 << 31)
    elif chance < 0.4: # sinkType
        genome[elementIndex] ^= (1 << 23)
    elif chance < 0.6: # sourceID
        genome[elementIndex] ^=  (1 << (flipper+24))
    elif chance < 0.8: # sinkID
        genome[elementIndex] ^= (1 << (flipper+16))
    else: # weight
        genome[elementIndex] ^= (1 << random.randint(1, 15))


def applyMutations(genome):
    noOfGenes = len(genome)
    mutated = 0
    while noOfGenes > 0:
        if mutationCond(1/1000):
            randomBitFlip(genome)
            mutated += 1
        noOfGenes -= 1
    return mutated


# def mutation(ele):
#     return 25 < ele.genome_copied == random.randint(1, 1000)


def mutationCond(prob):
    return random.random() < prob


def condition(ele):
    val = 16
    return ele.x > 128-val
    # return (64 - val < ele.y < 64 + val) and (64 - val < ele.x < 64 + val)
    # return ( (ele.x < val) or (ele.x >= (128 - val))) and ( (ele.y < val) or (ele.y >= (128 - val)))
    # return ele.y < val and ele.x < val
    # return ele.y < 30 and ( 40 <= ele.x <= 80 )


if __name__ == '__main__':
    gens = 0
    subsequent = False
    LOAD_DATA = True
    if LOAD_DATA:
        creatures, gens = load_data()
    else:
        creatures = generate_population(POPULATION)
        gens = 0

    app.run()




