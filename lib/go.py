from pyproteinsExt import ontology
import uuid, os, pickle


GO_ONTOLOGY = None

def setOntology(file):
    global GO_ONTOLOGY
    GO_ONTOLOGY = OntologyGO(file)

def ontologyDump(name, location):
    name = str( uuid.uuid4() ) if not name else name
    location = os.getcwd() if not location else location
    fName = location + '/' + name + '.sqlite3'
    print (f"Trying to open {fName}")
    ontology.default_world.set_backend(filename = fName)
    ontology.default_world.save()



# DAG implemnetaion requires memoizing visited node
# -> Any external accessor must be at the tree level, not at the node level avoid memoizing conflict
# Memoizing can be with a node heap or a node attribute
# We try the second one

# Check and raise Error at the 1st encountered cycle in
# the subtree of provided node 
import copy
def _checkCycle(rootNode, cNode, _path):
    path = copy.deepcopy(_path)
    path.append(cNode.ID)
    for child in cNode.children:
        if child.ID == rootNode.ID:
            pathString = '->'.join(path) + '->' + child.ID
            print (pathString)
            raise ValueError(f"{rootNode.name} has a cycle {pathString}")

def checkCycle(rootNode, verbose=False):
    if verbose:
        print(f"Checking {rootNode.ID}")

    for child in rootNode.children:
        _checkCycle(rootNode, child, [rootNode.ID])
    
    for child in rootNode.children:
        checkCycle(child)


class OntologyGO():
    def __init__(self, owlFile):
        self.onto = ontology.Ontology(file=owlFile)
        print('Loaded')
        
    def getLineage(self, goID):
        lin = self.onto._getLineage(goID)
        if not lin:
            return None
        return [ (t.id[0], t.label[0]) for t in lin[:-1] ]

# Basic pseudo set
class kNodes():
    def __init__(self):
        self.data = {}
    
    def __len__(self):
        return len(self.data)
        
    def __iter__(self):
        for k,v in self.data.items():
            yield v
    
    def  __contains__(self, node):
        return node in self.data
    
    def add(self, node):
        if not node in self:
            self.data[node] = node
        return self.data[node]
    def clear(self):
        self.data = {}
    

def ascend(cNode, nodeSet, rootSet):#;tree):
    #print(f"-->{cNode.ID}")
    for _p in cNode.oNode.is_a:
        # non ascendant is_a element
        #http://www.ontobee.org/ontology/RO?iri=http://purl.obolibrary.org/obo/BFO_0000051
    
        if str(_p).startswith('obo.BFO_0000051'):
            continue
        
        try : # trying to dereference Restriction wrapper
            p = _p.value
        except AttributeError:
            p = _p

        # cNode is terminal node
        if str(p) == "owl.Thing" :
            if len(cNode.oNode.is_a)> 1:
                raise TypeError(f"Terminal node having multiple parent: {cNode}")
            #print(f"Adding {cNode} as root")
            rootSet.add(cNode)
            return

        #print(f"{p}")
        # the current pNode is already registred, we eventually register cNode as one of its children
        # But won't keep on ascending
        pNode =  Node(p.id[0], p.label[0], p)
        toStop = True  if pNode in nodeSet else False
       
        # register current parent node
        pNode = nodeSet.add( pNode )
        pNode.isDAGelem = True
        #pNode.heap = tree.nodeHeap
        if not pNode.hasChild(cNode.ID):
            pNode.children.append(cNode)
        
        if not toStop:
            ascend(pNode, nodeSet, rootSet)#, tree)


import re, json, copy
class Node():

    def __init__(self, ID, name, oNode=None):
        self.ID = ID 
        self.name = name
        self.eTag =  [] # List of elements actually carrying the annotation ("tagged by the nodeName/annotation")
        self.leafCount =  0
        self.children =  []
        self.features = {}
        self.oNode = oNode
        self.isDAGelem = False
        #self.heap = None

    def __deepcopy__(self, memo):
        # Deepcopy only the id attribute, then construct the new instance and map
        # the id() of the existing copy to the new instance in the memo dictionary
        memo[id(self)] = newself = self.__class__(copy.deepcopy(self.ID, memo), copy.deepcopy(self.name, memo), copy.deepcopy(self.oNode, memo))
        # Now that memo is populated with a hashable instance, copy the other attributes:
        newself.eTag = copy.deepcopy(self.eTag, memo)
        # Safe to deepcopy now, because backreferences to self will
        # be remapped to newself automatically
        newself.children = copy.deepcopy(self.children, memo)
        newself.features = copy.deepcopy(self.features, memo)
        newself.isDAGelem = copy.deepcopy(self.isDAGelem, memo)
        newself.oNode = copy.deepcopy(self.oNode, memo)
        #newself.heap = copy.deepcopy(self.heap, memo)

        return newself

    def __hash__(self):
        return hash(self.ID)
    
    def __eq__(self, other):
        return hash(self) == hash(other)

# We may have to memo these 3   
    def as_DAG(self):
        return {
            'id' : self.ID,
            'children' : [ c.as_DAG() for c in self.children ]
        }

    def _as_DAG_strat(self, flat):
        if len(self.children) == 0 :
            return

        for c in self.children:
            if not c.ID in flat:
                flat[c.ID] = { "id" : c.ID, "parentIds" : set() }
            flat[c.ID]["parentIds"].add(self.ID)
        
        for c in self.children:
            c._as_DAG_strat(flat)
    
    def as_DAG_strat(self):
        #stHeap = kNodes()
        flat = { self.ID : { "id": self.ID, "parentIds" : [] } }
        #stHeap.add(self)

        self._as_DAG_strat(flat)
        
        return [ { "id" : v["id"], "parentIds" : list( v["parentIds"] )}  for k,v in flat.items() ]

    @property
    def pvalue(self):
        if 'Fisher' in self.features:
            return self.features['Fisher']
        return None
        

    def set(self, **kwargs):
        for k,v in kwargs.items():
            self.features[k] = v

    def __getattr__(self, key):
      #  print(key)
    #   if key not in self.features:
        if key == "ID":
            print(dir(self))
            return self.__getattribute__(key)

        if key == "features":
            raise AttributeError(key)
        try:
            return self.features[key]
        except KeyError:
            raise AttributeError(key)

        #return self.features[key]
    
    def __dir__(self):
        return super().__dir__() + [str(k) for k in self.features.keys()]
    
    def hasChild(self, ID):
    # print(node)
        for child in self.children:
            if child.ID == ID:
                return child
        return None
    
   
    def traverse(self):
        yield self
        for c in self.children:
            yield from c.traverse()
     
    # Memoized version of traverse
    def walk(self):
        wHeap = kNodes()
        return self._walk(wHeap)

    def _walk(self, wHeap):
        if self.isDAGelem and self in wHeap:
            return        
        wHeap.add(self) 
        yield self
        for c in self.children:
            yield from c._walk(wHeap)

    def _as_newick(self):
        #_self = node['name'].replace(" ", "_")
        _self = self.name.replace(',',' ').replace('(', '[').replace(')', ']').replace('\'', '_').replace(':', '_')
        
        if len(self.children) == 0:
            return _self

        return '(' + ','.join([ c._as_newick() for c in self.children ]) + ')' + _self
            
    def getByName(self, name):
        regExp = name.replace(' ', '.').replace('[', '.').replace(']', '.').replace('_', '.').replace(')', '\)').replace('(', '\(')
        regExp = regExp.replace('+', '.')
        if re.search("^" + regExp + "$", self.name):
            return self
        for c in self.children:
            v = c.getByName(name)
            if v:
                return v
        return None

    def getByID(self, ID):       
        if self.ID == ID:
            return self
        for c in self.children:
            v = c.getByID(ID)
            if v:
                return v
        return None


# Memoization implies the leaves of the subtree are already registred
# API to perform search at current node, we clear the heap

    def getMembers(self, nr=False):
        getMemberHeap = kNodes()
        getMemberHeap.add(self)

        buff = copy.copy(self.eTag)
        for n in self.children:
            buff += n._getMembers(getMemberHeap)
        
        return buff if not nr else list(set(buff))

    def _getMembers(self, _heap):
        if self.isDAGelem and self in _heap:
            return []        
        _heap.add(self)
        buff = copy.copy(self.eTag)
        for n in self.children:
            buff += n._getMembers(_heap)
        
        return buff


    def _collapseNode(self, _ctHeap):
        if self.isDAGelem and self in _ctHeap:
            #print(f"{self.name} already visited")
            return self

        _ctHeap.add(self)
        #print(f"collapsing {self.name}")
        if len(self.children) == 0: # Leave or a node carrying actual protein, return it
            return self
        
        if len(self.children) == 1 and len(self.eTag) == 0 :
            return self.children[0]._collapseNode(_ctHeap)
       
        self.children = [ n._collapseNode(_ctHeap) for n in self.children]
        
        return self

    def __repr__(self):
        d = { k : v for k,v in self.__dict__.items()  if not k == "children" }
        d["children"] = [ c.name for c in self.children ]
        return str(d)

    def __str__(self):
        return self.__repr__()

    def mayDrop(self, predicate, _noDropHeap):
        #print(f"Testing {self.name}")
        if not predicate(self):
        #   print(f"{self.name} is droped !")
            return None

        if self in _noDropHeap:
            return self
        _noDropHeap.add(self)

        self.children = [ c for c in self.children if c.mayDrop(predicate, _noDropHeap) ]

        return self

    def _leafCountUpdate(self, _lcHeap):
      #  print(f"lcu {self.name} {len(_lcHeap)}")
        if self.isDAGelem and self in _lcHeap:
            #print(f"{self.name} already updated")
            return self
        _lcHeap.add(self)

        self.leafCount = len(self.getMembers())
        #print(f"{self.name} leafCount is {self.leafCount}")

        for c in self.children:
            c._leafCountUpdate(_lcHeap)
    
def collapseTree(_root):
    root = copy.deepcopy(_root)
    ctHeap = kNodes()
    root.children = [ n._collapseNode(ctHeap) for n in root.children ]
    return root
    

def insertLineage(root, lineage, eName):
    cNode = root
    for (goID, name) in reversed(lineage):
        mNode = cNode.hasChild(goID)
        if not mNode:
            #print(f"{goID},{name} NOT found under {cNode['ID']},{cNode['name']}")
            mNode = Node(goID, name, None)
            cNode.children.append(mNode)
        else :
            #print(f"{goID},{name} found under {cNode['ID']},{cNode['name']}")
            pass
        cNode = mNode
        cNode.leafCount += 1
    cNode.eTag.append(eName)
    cNode.leafCount -= 1

'''
def getMembersByName(root, name):
    node = root.getByName(name)
    #print(node)
    m = node.getMembers()
    s = set(m)
    if not len(s) == len(m):
        print(f"Warning : Current subTree holds multiple occurences of eTag")

    return list(s)
'''

def deserializeGoTree(fPickle, owlFile):
    global GO_ONTOLOGY
    if not GO_ONTOLOGY:
        setOntology(owlFile)
    
    fp = open(fPickle, 'rb')
    _self = pickle.load(fp)
    fp.close()
    for n in _self.walk():
        if n.oNode is None:
            print(f"Root found skipping::{n}\n")
            continue
        if isinstance(n.oNode, str):
            termID = n.oNode#.replace('obo.', '').replace('_', ':')
            termObj = GO_ONTOLOGY.onto.onto.search_one(id=termID)

            if termObj is None:
                raise TypeError(f"No GO Term matching::{termID}::From::{n}\n")
            n.oNode =  termObj

    return _self

def createGoTree(ns=None, proteinList=None, uniprotCollection=None, collapse=True) :
    if not ns:
        raise ValueError("Specify a namespace \"ns\"")
    if not proteinList:
        raise ValueError("Specify a list of proteins \"proteinList\"")
    if not uniprotCollection:
        raise ValueError("Specify a collection of uniport elements \"uniprotCollection\"")

    print(f"Extracting {ns} ontology")

    xpGoTree = AnnotationTree(ns, collapse=True)
    xpGoTree.extract(proteinList, uniprotCollection)
    return xpGoTree

class AnnotationTree():
    def __init__(self, annotType,  collapse=False):

        enumNS = {
            'biological process' : 'GO:0008150',
            'molecular function' : 'GO:0003674',
            'cellular component' : 'GO:0005575'
        }
        
        if annotType not in enumNS:
            raise KeyError (f"annotation type \"{annotType}\" is not allowed ({enumNS}) {{ {enumNS.keys()} }}")

        self.collapsable = collapse
        self.isDAG = False
        #self.nodeHeap = kNodes()
        self.root = Node('0000', 'root') 
        #self.root.heap = self.nodeHeap
        self.NS = (annotType, enumNS[annotType])

    # Serialization requires pickling of object instance
    # Ontology related term will be saved as string
    # The ontology object will have to be reimported for deserialization

    def makePickable(self):
        _self = copy.deepcopy(self)
        for n in _self.walk():
            n.oNode = str(n.oNode).replace('obo.', '').replace('_', ':') if not n.oNode is None else None
        return _self
    
    def extract(self, *args):
        self.read_DAG(*args)

    def read_DAG(self,uniprotIDList, uniprotCollection):      
        self.isDAG = True
        global GO_ONTOLOGY
        if GO_ONTOLOGY is None:
            print("Please set GO_ONTOLOGY")
            return
      
        
        ontologyNode = GO_ONTOLOGY.onto.onto.search_one(id=self.NS[1])
        if not ontologyNode:
            raise ValueError(f"id {enumNS[annotType]} not found in ontology")
      #  self.root.children.append( Node(enumNS[annotType], annotType, oNode=ontologyNode) )

        nodeSet = kNodes()
        rootSet = kNodes()

        i=0
        for p in uniprotIDList:
           # print(f"Adding {p}")
            u = uniprotCollection.get(p)
            bp = list((u.GO[self.NS[0]]).keys())
            if bp:
                i += 1          
            for term in bp:
                cLeaf = GO_ONTOLOGY.onto.onto.search_one(id=term)
                if not cLeaf:
                    cLeaf = GO_ONTOLOGY.onto.onto.search_one(hasAlternativeId=term)
                    if not cLeaf:
                        #print(f"{u.GO[annotType][term]} {term} not found")
                        raise KeyError(f"{u.GO[self.NS[0]][term]} {term} not found")
                # Add a new node to set of fetch existing one
                bottomNode = nodeSet.add( Node(cLeaf.id[0], cLeaf.label[0], cLeaf) )
                bottomNode.eTag.append(p)
                bottomNode.isDAGelem = True
                #bottomNode.heap = self.nodeHeap
                #print(f"rolling up for {bottomNode.ID}")
                ascend(bottomNode, nodeSet, rootSet)#, self)
                
                
        #if len(rootSet) > 1:
        #    raise ValueError(f"Too many roots ({len(rootSet)}) {list(rootSet)}")
        for n in rootSet:
            if n.ID == self.NS[1]:
                self.root.children.append(n)
        if self.collapsable:
            print("Applying true path collapsing")
            self.root = collapseTree(self.root)
            #self.nodeHeap = self.root.heap
            
            
        n, l, p = self.dimensions
        print(f"{n} GO terms, {l} leaves, {p} proteins")

    def read(self,uniprotIDList, uniprotCollection):      
        global GO_ONTOLOGY
        if GO_ONTOLOGY is None:
            print("Please set GO_ONTOLOGY")
            return
        
        self.root.children.append( Node(self.NS[1], self.NS[0]) )
               
        i=0
        for p in uniprotIDList:
            u = uniprotCollection.get(p)
            bp = list((u.GO[self.NS[0]]).keys())
            if bp:
                i += 1          
            for term in bp:
                lineage = [(term, u.GO[self.NS[0]][term])] + GO_ONTOLOGY.getLineage(term)
                insertLineage(self.root, lineage, p)
                
        print(f"Annotation {self.NS[0]} extracted from {i} / {len(uniprotCollection)} uniprot entries parsed")
        
        if self.collapsable:
            print("Applying true path collapsing")
            self.root = collapseTree(self.root)
          #  self.nodeHeap = self.root.heap
    @property 
    def dimensions(self):
        nNodes = 0
        for n in self.root.walk():
            nNodes +=1
        leafTotal = self.root.getMembers()
        leafTotal_nr = set(leafTotal)

        return nNodes, len(leafTotal), len(leafTotal_nr)

    def traverse(self):
        return self.root.traverse() 
    
    def walk(self):
        return self.root.walk() 
    
    def as_json(self): # Should be collapsible
        return json.dumps(self.root)

    def as_newick(self, collapse=True):
        return '(' + self.root._as_newick() + ');'

    def getByName(self, name):
        n = self.root.getByName(name)
        if not n:
            raise KeyError(f"No node named \"{name}\" in current tree")
        return n

    def getByID(self, ID):
        n = self.root.getByID(ID)
        if not n:
            raise KeyError(f"No node w/ ID \"{ID}\" in current tree")
        return n

    def collapse(self):
        t = AnnotationTree(self.NS[0])
        t.isDAG = self.isDAG
      

        t.root = collapseTree(self.root)
       # t.nodeHeap = t.root.heap
        t.collapsable = True
        return t

    def getMembersByName(self, name, nr=True):
        node = self.root.getByName(name)
        m = node.getMembers()
        if nr:
            s = set(m)
            return list(set(m)) 

        return list(m)
       
    def getMembersByID(self, name, nr=True):
        node = self.root.getByID(name)
        #print(node)
        m = node.getMembers()
        if nr:
            return list(set(m))
        
        return list(m)

    def getMembers(self):
        return self.root.getMembers(nr=True)

    def newRoot(self,  name=None, ID=None):
        if not name and not ID:
            raise ValueError("Provide name or ID")

        t = AnnotationTree(self.NS[0])
        t.isDAG = self.isDAG
        t.collapsable = self.collapsable

        field = "name" if not name is None else "ID"
        value = name if not name is None else ID
        fn = self.getByName if not name is None else self.getByID

        nr = fn(value)

        if not nr:
            raise KeyError(f"No node with {field} {value} in mother tree")
        t.root.children.append(nr)
        
        return t

# A node may effectively be tested more than once
# Given the operation cost associated with False predicate (terminate&return None), heap is unecessary
# Given the operation cost associated with True predicate we effectively test the below tree once again
    def drop(self, predicate, noCollapse=False):
        t = AnnotationTree(self.NS[0])
        t.isDAG = self.isDAG
        t.collapsable = self.collapsable
 
        noDropHeap = kNodes() # To store success and avoid restest subtree

        t.root = copy.deepcopy(self.root)
        t.root.children = [ c for c in t.root.children if c.mayDrop(predicate, noDropHeap) ]

        if not noCollapse:
            t = t.collapse()
        t.leafCountUpdate()

        return t
       
    def leafCountUpdate(self):
        lcHeap = kNodes()

     #   if self.isDAG:
     #       print(f"clearing heap")
     #       self.nodeHeap.clear()
     #       print(f"heap size: {len(self.nodeHeap)}")
        for c in self.root.children:
            c._leafCountUpdate(lcHeap)

    def as_DAG_strat(self):
        return self.root.as_DAG_strat()
