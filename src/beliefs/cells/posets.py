#from .cell import *
from beliefs.cells import *
import networkx as nx
import logging
from networkx.algorithms.shortest_paths.generic import has_path

class PartialOrderedCell(Cell):
    """
    Generalizes the LinearOrderedCell to include represent po-sets.  Instead of
    being initialized with a list, this requires an instance of nx.DiGraph: a
    directed graph.

    A linear order has these properties:

     (1) Reflexive a <= a
     (2) Antisymmetric:  a <= b and b <=a  implies a == b
     (3) Transitivity:  a <= b  and b <=c implies a <= c
     (4) Linearity:  a <= b or b <= a

    A partial order does not require the linearity property (4).  Namely, some
    elements are incomparable, represented as a || b.  This corresponds to two
    nodes that are not linked by a directed path.

    Generalization domain is a rooted directed graph with one component.  The
    (set of) root node(s) is the Upper generalization boundary, the set of Leaf
    nodes is the lower generalization boundary. 

    Contradictions mean that there is a directed path between one of the lower
    boundaries and the root.
    """
    domain_map = {}
    def __init__(self, dag, lower=None, upper=None):
        """
        Dag represents the generalization structure.
        
        The actual values are kept in two sets:  upper and lower
        """
        assert self.__class__ != PartialOrderedCell, "Don't instantiate this class--subclass it!"
        domain = self.get_domain()
        if domain is None:
            self.set_domain(dag)
            domain = dag

        self.values = set()
        self.__values_computed = False
        
        roots = set()
        
        for node in domain.nodes():
            # find the root nodes
            if len(domain.predecessors(node)) == 0:
                # add root nodes to upper generalization bound
                roots.add(node)
        self.roots = frozenset(roots)
        
        if not (lower is None or upper is None):
            # TODO(dustin): check that all members of lower/upper
            # are in graph and are consistent
            self.lower = lower
            self.upper = upper
        else:
            self.upper = set()
            self.lower = set()

    @classmethod
    def set_domain(clz, dag):
        """ Sets the domain.  Should only be called once per class instantiation. """
        logging.info("Setting domain for poset %s" % clz.__name__)
        if not nx.is_directed_acyclic_graph(dag):
            raise CellConstructionFailure("Must be directed and acyclic")

        if not nx.is_weakly_connected(dag):
            raise CellConstructionFailure("Must be connected")
        clz.domain_map[clz] = dag
        
    @classmethod
    def get_domain(clz):
        """ Returns the class domain. """
        return clz.domain_map.get(clz, None)
        
    @classmethod
    def has_domain(clz):
        """ Returns True iff the class' domain is specified """
        return clz in clz.domain_map
        
    def get_values(self):
        """
        Returns positive members of the poset
        """
        if not self.__values_computed:
            self.__compute_values()
        return  set(self.values)

    def get_boundaries(self):
        """
        Returns just the upper and lower boundaries
        [upper, lower] representing the most general positive
        boundaries and the most specific lower boundaries
        """
        if not self.__values_computed:
            self.__compute_values()
        return set(self.upper), set(self.lower)
   
    def compute_upper_bound(self):
        """
        We have to compute the new upper boundary (nub) starting from the
        root nodes.  If a path exists between a root node and another entry in
        `self.upper` we can ignore the root node because it has been
        specialized by one of its successors.
        """
        nub = set()
        for root in self.roots - self.upper:
            found = False
            for up in self.upper - self.roots:
                domain = self.get_domain()
                if has_path(domain, root, up):
                    found = True
                    break
            if not found:
                nub.add(root)
        return nub | (self.upper - self.roots)
        
    def __compute_values(self):
        seen = set()
        nub = self.compute_upper_bound() - self.lower
        agenda = list(nub)
        while len(agenda) != 0:
            to_visit = agenda.pop(0)
            domain = self.get_domain()
            for child in domain.successors(to_visit):
                if not (child in seen \
                     or child in self.lower \
                     or child in agenda):
                     seen.add(child)
                     agenda.append(child)
        # if a node is in both sets, it meens our boundary is collapsed
        conflated = self.lower.intersection(self.upper)
        self.values = seen.union(nub) - conflated
        self.__values_computed = True

    def is_domain_equal(self, other):
        """
        Computes whether two Partial Orderings have the same generalization
        structure.
        """
        assert isinstance(other, PartialOrderedCell), "must coerce first"
        domain = self.get_domain()
        other_domain = other.get_domain()
        # if they share the same instance of memory for the domain
        if domain == other_domain:
            return True
        else:
            return False
            # same domain, slow version
            #return len(set(domain).symmetric_difference(set(other_domain))) == 0
        
        
    def is_equal(self, other):
        """
        Computes whether two Partial Orderings contain the same information
        """
        if not isinstance(other, PartialOrderedCell):
            other = self.coerce(other)
        if self.is_domain_equal(other)  \
            and len(self.upper.symmetric_difference(other.upper)) == 0 \
            and len(self.lower.symmetric_difference(other.lower)) == 0:
            return True
        return False
    
    def is_entailed_by(self, other):
        """
        Returns True iff Other 
        (a) has the same domain,
        (b) the same or more specific 'upper' bound; and 
        (c) the same or more general 'lower' bound. 
        
        Approach: Looks for ways to rule out entailment.  If none are found, 
        returns True
        """

        
        if not self.is_domain_equal(other):
            return False
        
        """        
        First we compare the similarity between upper bounds, 
         (1) if Self's upper bound is empty, Other's upper bound will always
            be as or more specific.
         (2) if Self's upper bound is a subset of Other's, Other will always
            be as or more specific.
            
         To prove the other has a more specific upper bound, we eliminate
            cases where it does not.  The first condition ensures the above
            two cases are not true.   Then, for each element in Other's upper
            bound (that is not in Self's),
            
         (3) if, for all elements in other's upper bound, we cannot find a member
           in the complete upper bound that is more general (has path from self[i]
           to other[j]), we return False, indicating Other does not entail
           Self.
        """
        domain = self.get_domain()
        self_full_upper = self.compute_upper_bound()
        if not (len(self.upper) == 0 \
             or other.upper.issuperset(self.upper)):
            for self_up in self_full_upper - other.upper:
                found = False
                # find a more specific member for each member
                # of self.upper that's not in other.upper
                for other_up in other.upper - self_full_upper:
                    if has_path(domain, self_up, other_up):
                        found = True
                        break
                if found:
                    break
                else:
                    return False  # none was found     
        """        
        Other must also share the same or more general 'lower' bound. 

         (3) if, for all elements in other's lower bound, we cannot find a member
           in the complete upper bound that is more general (has path from self[i]
           to other[j]), we stop.

        """
        if not (len(self.lower) == 0 \
            or self.lower.issubset(other.lower)):
            for self_lo in self.lower - other.lower:
                found = False
                for other_lo in other.lower - self.lower:
                    if has_path(domain, self_lo, other_lo):
                        found =True
                        break
                if found:
                    break
                else:
                    return False  # none was found
                    
        # if we got this far, we should have an entailment!
        return True

    
    def is_contradictory(self, other):
        """
        Does the merge yield the empty set? 
        """
        if not self.is_domain_equal(other):
            return True
        # what would happen if the two were combined? 
        test_lower = self.lower.union(other.lower)
        test_upper = self.upper.union(other.upper)
        # if there is a path from lower to upper nodes, we're in trouble:
        domain = self.get_domain()
        for low in test_lower:
            for high in test_upper:
                if low != high and has_path(domain, low, high):
                    return True
        # lastly, build a merged ordering and see if it has 0 members
        test = self.__class__()
        test.lower = test_lower
        test.upper = test_upper
        return len(test) == 0

    def coerce(self, other, is_positive=True):
        """
        Only copies a pointer to the new domain's cell
        """
        if isinstance(other, PartialOrderedCell):
            if self.is_domain_equal(other):
                return other
            else:
                msg = "Cannot merge partial orders with different domains!"
                raise CellConstructionFailure(msg)
        if isinstance(other, LinearOrderedCell):
            # convert other's domain to a chain/dag
            # first ensure domain has same size and elements
            raise NotImplemented("Please Implement me!")
        domain = self.get_domain()
        if other in domain:
            c = self.__class__()
            if not is_positive:
                # add value to lower (negative example)
                c.lower = set([other])
                c.upper = set()
            else:
                # add value to upper (positive example)
                c.upper = set([other])
                c.lower = set()
            return c
        else:       
            raise CellConstructionFailure("Could not coerce value that is"+
                    " outside order's domain . (Other = %s) " % (str(other),))

    def merge(self, other, is_positive=True):

        other = self.coerce(other, is_positive)
        # the above coercion forces equal domains, and raises an 
        # exception otherwise
        if self.is_equal(other):
            pass
        elif other.is_entailed_by(self):
            # this is the case where the other contains all of the values
            # we have and more, so we don't gain anything by keeping it around
            pass  # do nothing
        elif self.is_entailed_by(other):
            # TODO: what if other has a size of 0, do we still merge?
            # replace self with other
            self.lower = other.lower
            self.upper = other.upper
            self.__values_computed = False
            return self
        elif self.is_contradictory(other):
            raise Contradiction("Cannot merge partial orders")
        else:
            # merge the two
            def add_single_value(val, is_positive):
                if not is_positive:
                    # lower generalization boundaries
                    # replace val with its parents
                    if not val in self.lower:
                        self.lower.add(val)
                        self.__values_computed = False        
                else:
                    # raise specialization boundaries
                    if not val in self.upper:
                        self.upper.add(val)
                        self.__values_computed = False

            for general in other.upper:
                add_single_value(general, True)
            for specific in other.lower:
                add_single_value(specific, False)

        if len(self) == 0:
            raise Contradiction("Partial Ordering has No Members")
            
        return self


    def size(self):
        """
        Return the number of members in the partial ordering (between and
        including the boundaries)
        """
        return len(self.get_values())

    def to_dot(self):
        """
        Outputs a version that can be deisplayed or seralized
        """
        return {'lower': list(self.lower),
                'upper': list(self.upper)}

    def __repr__(self):
        output = ""
        output += "\t\tUPPER = " + ','.join(self.upper) + "\n"
        output += "\t\tLOWER = " + ','.join(self.lower) + "\n"
        output += "\t\tVALUES = "
        values = self.get_values()
        output += ",".join(list(values)[0:6])
        if len(values) > 6:
            output += "... (and %i others)" % (len(values)-5)
        return output
   
    __str__ = __repr__  
    __len__ = size

    def get_refinement_options(self):
        """ Returns possible specializations for the upper values in the taxonomy """
        domain = self.get_domain()
        for upper_value in self.upper:
            for suc in domain.successors(upper_value):
                yield suc

    def get_relaxation_options(self):
        """ Returns possible generalizations for the upper values in the taxonomy """
        domain = self.get_domain()
        for upper_value in self.upper:
            for suc in domain.predecessors(upper_value):
                yield suc

if __name__ == '__main__':

    class TestPOC(PartialOrderedCell):
        # partial ordered test
        def __init__(self):
            dag = None
            if not self.has_domain():
                # only initialize once
                dag = nx.DiGraph()
                dag.add_edge("thing", "person")
                dag.add_edge("person", "actress")
                dag.add_edge("person", "director")
                dag.add_edge("director", "good-director")
                dag.add_edge("director", "bad-director")
                dag.add_edge("person", "writer")
                dag.add_edge("person", "producer")
                dag.add_edge("thing", "vehicle")
                dag.add_edge("vehicle", "car")
                dag.add_edge("vehicle", "truck")
                
            PartialOrderedCell.__init__(self, dag)

    t = TestPOC()
    t.merge("person")
    print list(t.get_refinement_options())
    print list(t.get_relaxation_options())
