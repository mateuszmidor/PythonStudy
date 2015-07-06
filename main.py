'''
Created on 06-07-2015

@author: mateusz

Dependency injection by substituting the parent example.

Based on https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
, or actually the pycon video https://www.youtube.com/watch?v=EiOglTERPEo
'''


class DoughFactory(object):
    ''' Just a regular dough factory '''
    def get_dough(self):
        print("Regular dough delivered")
        
        
class BiomolecularDoughFactory(DoughFactory):
    ''' Special dough factory '''
    def get_dough(self):
        print("Biomolecular dough delivered")
        
                
                    
class PizzaFactory(DoughFactory): 
    ''' Pizzeria using DoughFactory '''       
    def get_pizza(self):
        super(PizzaFactory, self).get_dough()
        print("Pizza produced!")

        
class BiomolecularPizzaFactory(PizzaFactory, BiomolecularDoughFactory):
    ''' 
    Here comes in the magic. This pizza factory will use BiomolecularDoughFactory
    instead of DoughFactory thanks to inheritance tree linearisation Method Resolution Order (MRO)
    '''
    pass    

        
if __name__ == '__main__':
    # get your biomolecular pizza
    pizzeria = BiomolecularPizzaFactory()
    pizzeria.get_pizza()
    
    # see the method resolution order
    help(BiomolecularPizzaFactory)
    