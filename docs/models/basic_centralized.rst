.. _basic_centralized:

#################
Centralized model
#################

************************
Theorical representation
************************

Centralized computing is a model in which all computational tasks, data storage, and resource management are handled by a
single central server or a small cluster of servers. This contrasts sharply with distributed computing, where multiple
independent entities work together across a network to perform tasks and store data.

In a centralized computing environment, all resources, such as processing power, memory, and storage, are consolidated in
one central location. Users typically access these resources through terminals or thin clients, which depend entirely on
the central server for processing power and data storage. This setup allows for a more straightforward architecture
because all computing happens in one place, avoiding the complexities involved in synchronizing and managing multiple
independent systems.



**********************
PyDistSim equivalences
**********************

Even though PyDistSim is not designed to simulate centralized systems, it can be used to simulate the setup phase of a
distributed system, where a central entity distributes the initial state to all other entities.

Simple centralized algorithms can be implemented by subclassing the :class:`NetworkAlgorithm` class.
