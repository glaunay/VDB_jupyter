from scipy.stats import hypergeom
from scipy.stats import fisher_exact
import numpy as np

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

        
        ORA_Fisher.append( (pValue, cPath) ) 
        ORA_CDF.append( ( p, cPath) ) 
        
        cPath.set(Fisher=pValue, Hpg=p)

    print(f"Evaluated {pathwayReal} / {pathwayPotential} Pathways, based on {n} proteins")
    return ORA_Fisher, ORA_CDF
