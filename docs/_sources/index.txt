.. myUROP documentation master file, created by
   sphinx-quickstart on Fri Feb 22 00:16:14 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Beliefs
==================================

Here are :py:class:`Cell` data containers, :ref:`cell` subclasses that are designed to accumulate and maintain the consistency of *partial information*:

- :py:class:`bools.BoolCell` three-valued logic of `True`, `False` and `Unknown`.
- :py:class:`dicts.DictCell` a labeled set, like a Python `dict` that pairs attributes with cell values.
- :py:class:`numeric.IntervalCell` a bounded interval or cardinal number
- :py:class:`sets.SetIntersectionCell` a set, unordered collection of symbols, where merges are intersective and information is thereby monotonically decreasing
- :py:class:`lists.LinearOrderedCell` a bounded sequence of ordered symbols
- :py:class:`lists.PrefixCell` allows maintains sequences with shared elements
- :py:class:`posets.PartialOrderedCell` maintains a taxonomy of information


This library is being developed at <https://github.com/EventTeam/beliefs>.

All modules
==================================

.. toctree::
   :maxdepth: 2

   beliefstate
   bools
   colors
   dicts
   lists
   sets 
   numeric
   posets
   setCells
   spatial
   strings
   



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

