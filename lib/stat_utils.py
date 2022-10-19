from scipy.stats import hypergeom
from scipy.stats import fisher_exact
import numpy as np
import uniprot
import go
import sys

class GO_ORA_analyser():
    def __init__(self, goOntologyFile, proteomeDirectory, experimentalProteinDirectory):
        print("Loading ontology")
        go.setOntology(goOntologyFile)
        print("Reading whole proteome")
        self.proteomeCollection = uniprot.UniprotCollection(proteomeDirectory)
        print(f"{len(self.proteomeCollection)} Loaded")
        print("reading experimental protein set")
        self.xpCollection=uniprot.UniprotCollection(experimentalProteinDirectory)
        print(f"{len(self.xpCollection)} Loaded")
        self._xp_BP = None
        self._bk_BP = None
        
        self._xp_MF = None 
        self._bk_MF = None
        
        self._xp_CC = None
        self._bk_CC = None
    
    def get_background_proteins(self, name=None, ID=None):
        if not name and not ID:
            raise ValueError("You must specify a GO class name or ID")
        try:
            if name :
                return self._bk_BP.getByName(name).eTag
            return self._bk_BP.getByID(ID).eTag
        except KeyError:
            print(f"Go Term {name if name else ID} not found", file=sys.stderr)
            return None
        
    def get_experimental_proteins(self, name=None, ID=None):
        if not name and not ID:
            raise ValueError("You must specify a GO class name or ID")
        try:
            if name :
                return self._xp_BP.getByName(name).eTag
            return self._bk_BP.getByID(ID).eTag
        except KeyError:
            print(f"Go Term {name if name else ID} not found", file=sys.stderr)
            return None

    def biological_process(self, selectedUniprotList):
        ns = "biological process"
        if not self._xp_BP:
            print(f"Building {ns} GO Tree")
            self._xp_BP = go.createGoTree(ns=ns, 
                                          proteinList=selectedUniprotList, 
                                          uniprotCollection=self.xpCollection)
            _ = self.proteomeCollection.list
            self._bk_BP = go.createGoTree(ns=ns, 
                                          proteinList=_, 
                                          uniprotCollection=self.proteomeCollection
            )
        Fisher_ORA = self._compute_ora(ns, self._xp_BP, self._bk_BP, selectedUniprotList)
        return sorted(
            [ (pValue, cPath.name, cPath.ID, cPath.getMembers() ) for pValue, cPath in Fisher_ORA ],
            key=lambda e:e[0]
        )
        #return self._compute_ora(ns, self._xp_BP, self._bk_BP, selectedUniprotList)
        #pathWayRoot = self._xp_BP.getByName(ns)
        #pathWayBKG  = self._bk_BP.getByName(ns)
        #return computeORA(pathWayRoot, selectedUniprotList, pathWayBKG)
     

    def molecular_function(self, selectedUniprotList):
        ns = "molecular function"
        if not self._xp_MF:
            print(f"{ns} process GO Tree")
            self._xp_MF = go.createGoTree(ns=ns, 
                                          proteinList=selectedUniprotList, 
                                          uniprotCollection=self.xpCollection)
            _ = self.proteomeCollection.list
            self._bk_MF = go.createGoTree(ns=ns, 
                                          proteinList=_, 
                                          uniprotCollection=self.proteomeCollection
            )
        Fisher_ORA = self._compute_ora(ns, self._xp_MF, self._bk_MF, selectedUniprotList)
        return sorted(
            [ (pValue, cPath.name, cPath.ID, cPath.getMembers() ) for pValue, cPath in Fisher_ORA ],
            key=lambda e:e[0]
        )
        #return self._compute_ora(ns, self._xp_MF, self._bk_MF, selectedUniprotList)
        #pathWayRoot = self._xp_MF.getByName(ns)
        #pathWayBKG  = self._bk_MF.getByName(ns)
        #return computeORA(pathWayRoot, selectedUniprotList, pathWayBKG)
     
    def cellular_component(self, selectedUniprotList):
        ns = "cellular component"
        if not self._xp_CC:
            print(f"{ns} process GO Tree")
            self._xp_CC = go.createGoTree(ns=ns, 
                                          proteinList=selectedUniprotList, 
                                          uniprotCollection=self.xpCollection)
            _ = self.proteomeCollection.list
            self._bk_CC = go.createGoTree(ns=ns, 
                                          proteinList=_, 
                                          uniprotCollection=self.proteomeCollection
            )
        
        Fisher_ORA = self._compute_ora(ns, self._xp_CC, self._bk_CC, selectedUniprotList)
        return sorted(
            [ (pValue, cPath.name, cPath.ID, cPath.getMembers() ) for pValue, cPath in Fisher_ORA ],
            key=lambda e:e[0]
        )
        #return self._compute_ora(ns, self._xp_CC, self._bk_CC, selectedUniprotList)
       # pathWayRoot = self._xp_CC.getByName(ns)
        #pathWayBKG  = self._bk_CC.getByName(ns)
        #return computeORA(pathWayRoot, selectedUniprotList, pathWayBKG)
      
    def _compute_ora(self, ns, tree_xp, tree_bk, selectedProteinList):
        pathWayRoot = tree_xp.getByName(ns)
        
        #Définition du terme GO regroupant tout le protéome
        pathWayBKG = tree_bk.getByName(ns)
    #    print(pathWayRoot)
    #    print(pathWayBKG)
        #Calcul de l'enrichissement en termes GO successifs parmi les protéines surabondantes (ici, saList)
        oraScores = computeORA(pathWayRoot, selectedProteinList, pathWayBKG)

        return oraScores


#xpGoTree_MF = go.createGoTree(ns="molecular function", proteinList=xpProtList, uniprotCollection=uniprotCollection)
#fullEcoliGoTree_MF = go.createGoTree(ns="molecular function", proteinList=K12.list, uniprotCollection=K12)

#xpGoTree_CC = go.createGoTree(ns="cellular component", proteinList=xpProtList, uniprotCollection=uniprotCollection)
#fullEcoliGoTree_CC = go.createGoTree(ns="cellular component", proteinList=K12.list, uniprotCollection=K12)

# Calcul la probabilité d'observer au moins k protéines membres de ce pathway 
# parmi la liste de protéines fournie

def computeSelfORA(node, proteinList):
    
    ORA = []
    
    # universe is all uniprotID found in the annotation tree
    universe = set(node.getMembers()) 
    N = len(universe)
    # nSet is the observed set   
    nSet = set(proteinList)
    n = len(nSet)
    for cPath in node.walk():       
        Kstates = set(cPath.getMembers())
        K = len( Kstates )
        print(f"{cPath.name} has {K} members")
        
        k_obs = Kstates & nSet
        k = len(k_obs)
        
        p = righEnd_pValue(N, n, K, k)
        
        ORA.append( (p, cPath) )
        print(f"{cPath.name} [{K} -> {k}/{n}] = {p}")
    return ORA
    
def righEnd_pValue(N, n, K, k):
    
#print(f"N={N}, n={n}, K={K}, k={k}")

#The hypergeometric distribution models drawing objects from a bin. 
#N is the total number of objects, K is total number of Type I objects. 
#The random variate represents the number of Type I objects in N 
#drawn without replacement from the total population.

# Right-end tail of the CDF is P(X>=k)
    p_x = hypergeom(N, K, n).cdf([k - 1])
    return 1.00 - p_x[0]

def computeORA(node, proteinList, nodeBKG, verbose=False):
    Fisher, CDF = computeORA_BKG(node, proteinList, nodeBKG, verbose=verbose)
    return Fisher

def computeORA_BKG(node, proteinList, nodeBKG, verbose=False): # IDEM, mais avec un autre arbre de reference
    
    ORA_Fisher = []
    ORA_CDF = []

    universe = set(nodeBKG.getMembers())
    o = len(universe)

    # nSet is the observed set   
    nSet = set(proteinList)
    n = len(nSet)
    
    pathwayPotential = 0
    pathwayReal = 0
    
    for cPath in node.walk():
        pathwayPotential += 1
        #verbose = cPath.name == 'enzyme binding'
        if verbose:
            print(cPath.name)

        # Table de contingence
        #
        #        | Pa  | non_PA |
        # -----------------------
        #    SA  |     |        |
        #  nonSA |     |        |

        
        # l'intersection entre les protéines porteuse de l'annotation courante et 
        # la liste des protéines sur-abondante
        # => nombre de succès observés, "k"
        Kstates = set(cPath.getMembers())
        k_obs = Kstates & nSet
        if not k_obs:
            if verbose:
                print("k_obs == 0")
            continue
        k = len(k_obs)
        pathwayReal += 1
        # Pour estimer le nombre de protéines non surAbondantes appartenant au pathway ou non
        # Nous utilisons la proporition de protéines du pathway ou non dans le protéome entier
        bkgPath = nodeBKG.getByName(cPath.name)
        if not bkgPath:
            continue
        #    raise ValueError(f"{cPath.name} not found in BKG")
        bkgPathFreq = len( set(bkgPath.getMembers()) ) / len(universe)  # Fraction du protéomes appartenant à ce Pathway
        nSA_Pa = int ( (o - k) * bkgPathFreq )
        nSA_nPa = int( (o - k) - nSA_Pa )
        
        TC = [
            [ k ,  len(proteinList) - k],
            [ nSA_Pa ,  nSA_nPa]
        ]
        
        oddsratio, pValue = fisher_exact(TC, alternative="greater")
        p = righEnd_pValue(o, n, len( set(bkgPath.getMembers()) ), k)

        if verbose:
            print(f"{cPath.name} {TC} p={pValue} // pL={p}")

        _ = cPath.getMembers()
        ORA_Fisher.append( (pValue, cPath) ) 
        ORA_CDF.append( ( p, cPath) ) 
        
        cPath.set(Fisher=pValue, Hpg=p)

    print(f"Evaluated {pathwayReal} / {pathwayPotential} Pathways, based on {n} proteins")
    return ORA_Fisher, ORA_CDF
