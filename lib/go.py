from pyproteinsExt import ontology

class ontologyGO():
    def __init__(self, owlFile):
        self.onto = ontology.Ontology(file=owlFile)
        print('Loaded')
        
    def getLineage(self, goID):
        lin = self.onto._getLineage(goID)
        if not lin:
            return None
        return [ (t.id[0], t.label[0]) for t in lin[:-1] ]


import re, json, copy

class Node():

    def __init__(self, ID, name):
        self.ID = ID 
        self.name = name
        self.eTag =  [] # List of elements actually carrying the annotation ("tagged by the nodeName/annotation")
        self.leafCount =  0
        self.children =  []
        self.features = {}

    def set(self, **kwargs):
        for k,v in kwargs.items():
            self.features[k] = v

    def __getattr__(self, key):
      #  print(key)
    #   if key not in self.features:
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
    #print(">", node["name"])
        yield self
        for c in self.children:
            yield from c.traverse()
        
    def _as_newick(self):
        #_self = node['name'].replace(" ", "_")
        _self = self.name.replace(',',' ').replace('(', '[').replace(')', ']').replace('\'', '_').replace(':', '_')
        
        if len(self.children) == 0:
            return _self

        return '(' + ','.join([ c._as_newick() for c in self.children ]) + ')' + _self
            
    def getByName(self, name):
        regExp = name.replace(' ', '.').replace('[', '.').replace(']', '.').replace('_', '.').replace(')', '\)').replace('(', '\(')
        regExp = regExp.replace('+', '.')
        #if node['name'] == name:
        #print(regExp)
        if re.search("^" + regExp + "$", self.name):
            return self
        for c in self.children:
            v = c.getByName(name)
            if v:
                return v
        return None

    def getMembers(self):
        buff = copy.copy(self.eTag)
        for n in self.children:
            buff += n.getMembers()
        
        return buff

    def _collapseNode(self):
        if len(self.children) == 0: # Leave or a node carrying actual protein, return it
            return self
        
        if len(self.children) == 1 and len(self.eTag) == 0 :
            return self.children[0]._collapseNode()
        
        self.children = [ n._collapseNode() for n in self.children ]
        return self

    def __repr__(self):
        d = { k : v for k,v in self.__dict__.items()  if not k == "children" }
        d["children"] = [ c.name for c in self.children ]
        return str(d)

    def __str__(self):
        return self.__repr__()

    def mayDrop(self, predicate):
        #print(self.name)
        if not predicate(self):
            #print(f"{self.name} is droped !")
            return None
        self.children = [ c for c in self.children if c.mayDrop(predicate) ]
        return self

    def leafCountUpdate(self):
        self.leafCount = len(self.getMembers())
        for c in self.children:
            c.leafCountUpdate()
    
def collapseTree(_root):
    root = copy.deepcopy(_root)
    root.children = [ n._collapseNode() for n in root.children ]
    return root
    

def insertLineage(root, lineage, eName):
    cNode = root
    for (goID, name) in reversed(lineage):
        mNode = cNode.hasChild(goID)
        if not mNode:
            #print(f"{goID},{name} NOT found under {cNode['ID']},{cNode['name']}")
            mNode = Node(goID, name)
            cNode.children.append(mNode)
        else :
            #print(f"{goID},{name} found under {cNode['ID']},{cNode['name']}")
            pass
        cNode = mNode
        cNode.leafCount += 1
    cNode.eTag.append(eName)
    cNode.leafCount -= 1


def getMembersByName(root, name):
    node = root.getByName(name)
    #print(node)
    m = node.getMembers()
    s = set(m)
    if not len(s) == len(m):
        print(f"Warning : Current subTree holds multiple occurences of eTag")

    return list(s)


class AnnotationTree():
    def __init__(self, collapse=False):
        self.collapsable = collapse
        pass
    def read(self,uniprotIDList, uniprotCollection, go, annotType='biological process'):      
        enumNS = {
            'biological process' : 'GO:0008150',
            'molecular function' : 'GO:0003674',
            'cellular component' : 'GO:0005575'
        }
        
        if annotType not in enumNS:
            raise KeyError (f"annotation type \"{annotType}\" is not allowed (${enumNS})")
        
        self.root = Node('0000', 'root')

        self.root.children.append( Node(enumNS[annotType], annotType) )
               
                #{ 'ID' : '0000',
                #    'name': 'root',
                #    'children': [
                #    { 'ID' : enumNS[annotType], ## This is wrong
                #    'name' : annotType,
                #    'eTag' : [],
                #    'leafCount' : 0,
                #    'children' :  []
                #    }
                #]
                #}
        i=0
        for p in uniprotIDList:
            u = uniprotCollection.get(p)
            bp = list((u.GO[annotType]).keys())
            if bp:
                i += 1          
            for term in bp:
                lineage = [(term, u.GO[annotType][term])] + go.getLineage(term)
                insertLineage(self.root, lineage, p)
                
        print(f"Annotation {annotType} extracted from {i} / {len(uniprotCollection)} uniprot entries parsed")
        
        if self.collapsable:
            print("Applying true path collapsing")
            self.root = collapseTree(self.root)

    def traverse(self):
        return self.root.traverse() 
    
    def as_json(self): # Should be collapsible
        return json.dumps(self.root)

    def as_newick(self, collapse=True):
        return '(' + self.root._as_newick() + ');'

    def getByName(self, name):
        n = self.root.getByName(name)
        if not n:
            raise KeyError(f"No node named \"{name}\" in current tree")
        return n

    def collapse(self):
        t = AnnotationTree()
        t.root = collapseTree(self.root)
        t.collapsable = True
        return t

    def getMembersByName(self, name):
        node = self.root.getByName(name)
        #print(node)
        m = node.getMembers()
        s = set(m)
        if not len(s) == len(m):
            print(f"Warning : Current subTree holds multiple occurences of eTag")

        return list(s)

    def getMembers(self):
        return self.root.getMembers()


    def newRoot(self, name):
        t = AnnotationTree()
        t.root = Node('0000', 'root')
        nr = self.getByName(name)
        if not nr:
            raise KeyError(f"No node named {name} in mother tree")
        t.root.children.append(nr)
        t.collapsable = self.collapsable
        return t


    def drop(self, predicate):
        t = AnnotationTree()
        t.root = copy.deepcopy(self.root)
        t.root.children = [ c for c in t.root.children if c.mayDrop(predicate) ]
        t.leafCountUpdate()
        return t.collapse()
       # return collapseTree(t)
    
    def leafCountUpdate(self):
        for c in self.root.children:
            c.leafCountUpdate()