import networkx as nx
from models import *
from collections import defaultdict

def getZero():
    return 0

if __name__ == "__main__":

    G: nx.MultiDiGraph = nx.nx_pydot.read_dot('cfg.dot')

    # Calculate post-dominators using dominators of a reversed graph of CFG
    RevG = G.reverse()
    post_doms = nx.algorithms.immediate_dominators(RevG, 'END')

    branches = []
    with open('branches.txt', 'r') as branchesFile:
        for line in branchesFile.readlines():
            branches.append(line.strip("\n"))

    trace = []
    with open('trace.txt', 'r') as traceFile:
        for line in traceFile.readlines():
            trace.append(line.strip("\n"))

    instanceTrackerMap = defaultdict(getZero)
    control_dependence_stack = []

    control_dependence = defaultdict(set)

    for instr in trace:
        # first check for merge - because merge doesn't depend on the predicate at the top of the stack - since it is merging
        # Catch here being that you are trusting your CFG which will not cover all merges depending on paths coverage
        if G.in_degree(instr) > 1:
            if len(control_dependence_stack) > 0:
                while len(control_dependence_stack) > 0:
                    peeked: CdgStackEntry = control_dependence_stack[-1]
                    if (peeked.ipd == instr):
                        control_dependence_stack.pop()
                        instanceTrackerMap[peeked.address] = peeked.instance - 1
                    else:
                        break
        # then get the control dependencies - if stack is empty, instruction depends on START
        peeked: CdgStackEntry = control_dependence_stack[-1] if control_dependence_stack else CdgStackEntry('START', None, None)
        control_dependence[instr].add(peeked.address)
        # then check for branch and add entry to stack and update instance numbers
        # Catch here being that you are trusting your CFG which will not cover all branches depending on paths coverage 
        # In this case we are using branches that we have gotten from PIN, so it will be accurate - but our post-doms 
        # depend on CFG which again depends on paths taken
        if instr in branches:
            newStackEntry = CdgStackEntry(instr, instanceTrackerMap[instr], post_doms[instr])
            control_dependence_stack.append(newStackEntry)
            instanceTrackerMap[instr] = instanceTrackerMap[instr] + 1

    outG = nx.MultiDiGraph()

    for controlled in (control_dependence.keys()):
        controllers = control_dependence[controlled]
        for controller in controllers:
            outG.add_edge(controlled, controller)
    
    nx.nx_pydot.write_dot(outG, 'cdg.dot')