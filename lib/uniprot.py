'''

'''
import glob
import os
import xml.etree.ElementTree as ET


class UniprotCollection():
    def __init__(self, directory):
        try :
            os.path.isabs(directory)
            os.path.exists(directory)
        except:
            print("{directory} must be absolute and valid directory path")
            
        self.root = directory
        self.index = [os.path.splitext(os.path.basename(f))[0] for f in glob.glob(f"{directory}/*.xml")]
    def get(self, _id):
        if _id in self.index:
            return Uniprot(self.root + '/' + _id + '.xml', _id)
        return None

    @property
    def list(self):
        return self.index
    
    def __len__(self):
        return len(self.index)
    
class Uniprot():
    def __init__(self, file, _id):
        self.source = file
        self.id = _id
        self._GO = None
        self._xmlRoot = None
      
    @property
    def GO(self):
        if not self._GO:
            self._GO = {'biological process' : {}, 'molecular function' : {}, 'cellular component':{}}
            for e in self.xmlRoot.findall("{http://uniprot.org/uniprot}entry/{http://uniprot.org/uniprot}dbReference[@type='GO']"):
                goID = e.attrib['id']
                label = e.find("{http://uniprot.org/uniprot}property[@type='term']").attrib['value']
                if label.startswith("P:"):
                    ns = 'biological process'
                elif label.startswith("F:"):
                    ns = 'molecular function'
                elif label.startswith("C:"):
                    ns = 'cellular component'
                else :
                    throw ('Unknown GO ns ' + label[:2])
                            
                self._GO[ns][goID] = label[2:]
        return self._GO
    
    @property
    def xmlRoot(self):
        if not self._xmlRoot:
            tree = ET.parse(self.source)
            self._xmlRoot = tree.getroot()
        return self._xmlRoot
