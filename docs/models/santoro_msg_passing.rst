.. _santoro_msg_passing:

#########################
The message passing model
#########################

************************
Theorical representation
************************

The book titled "Design and Analysis of Distributed Algorithms" by Nicola Santoro provides an in-depth exploration of
the fundamental concepts and principles underlying distributed computing systems. It begins by defining a distributed
computing environment as a system composed of multiple computational entities, each of which may be referred to as a
process, processor, switch, agent, or by other names depending on the context and the system being modeled. These
entities work collaboratively, often communicating over a network, to achieve a common goal such as solving a problem
or performing a specific task.


Each entity within a distributed computing environment possesses its own local memory, which includes various registers
used to maintain its status and the values it processes. For instance, the status register (`status(x)`) indicates the
current state of an entity, while the input value register (`value(x)`) stores values pertinent to the computations or
tasks the entity is performing. Entities are equipped with the capabilities to perform local storage and processing,
send and receive messages to and from other entities, reset alarm clocks, and alter their status based on certain
conditions or events.

Actions and reactions
=====================

This model emphasizes that entities in a distributed environment react to external events. These events could include
the arrival of a message, the ringing of an alarm clock, or spontaneous impulses generated within the system. When an
entity encounters an event, it executes a sequence of operations known as an action, which is performed without
interruption and within a finite time frame. The specific behavior of an entity is thus determined by its current status
and the type of event it is reacting to. This behavior is often defined through a set of rules or protocols that outline
the appropriate responses for each combination of status and event.

Communication
=============

Communication between entities in a distributed computing environment is primarily achieved through the transmission and
reception of messages. Each entity has a defined set of neighbors to which it can send messages (`out_neighbors(x)`) and
from which it can receive messages (`out_neighbors(x)`). The communication topology of the environment is typically
represented by a directed graph, where nodes symbolize entities and edges represent the communication links. This
graphical representation helps in understanding the relationships and communication pathways between different entities
within the system.

Axioms and restrictions
=======================

The model also outlines several axioms that are fundamental to the operation of such distributed computing environments. One
such axiom is the principle of finite communication delays, which states that, in the absence of failures, any message
transmitted between entities will be delivered within a finite amount of time. Another axiom is local orientation, which
implies that entities are capable of distinguishing between their neighbors, thereby enabling them to direct messages to
specific entities and to know from which entity a message has been received.


In addition to these axioms, the book discusses various optional restrictions that may apply to distributed environments.
Restrictions are additional properties or capabilities that define specific characteristics of the system, potentially
limiting or enhancing its operation. These restrictions can pertain to communication properties, reliability, and
synchrony, among other factors. For example, some systems may enforce message ordering, ensuring that messages sent to
the same neighbor arrive in the order they were dispatched. Other systems may adhere to the principle of reciprocal
communication, which requires that communication links be bidirectional, meaning that each entity capable of sending a
message must also be able to receive a message in return.


Reliability is another critical aspect of distributed computing environments covered in the model. Systems may
incorporate mechanisms for fault detection, allowing entities to detect the failure of links or other entities.
Different levels of reliability can be defined based on the system's tolerance to failures. For instance, a system with
guaranteed delivery ensures that messages are always delivered without any corruption. In contrast, a system
characterized by partial reliability might guarantee that no failures occur during execution, whereas a totally reliable
system would be completely free from failures.

Bottom line
===========

In summary, the model provides a comprehensive abstraction of the various architecture components, entities, behaviors,
communication protocols, axioms, and potential restrictions of distributed systems. It explores how entities
operate within these environments, emphasizing predictable behavior through clearly defined rules and protocols that
govern their interactions and responses to events. The focus on communication, reliability, and fault tolerance
underscores the complexities and challenges inherent in designing and managing distributed computing systems.



**********************
PyDistSim equivalences
**********************

This framework provides a Python implementation of the message passing model described by Santoro. It offers a set of
classes and functions that enable users to define and simulate distributed computing environments, create entities,
specify communication topologies, and model interactions between entities. The framework is designed to facilitate the
development and analysis of distributed algorithms, allowing users to explore various scenarios and test the behavior of
entities under different conditions.

Protocols and algorithms can be implemented by subclassing the :class:`NodeAlgorithm` class and defining the appropriate
methods to handle every action.

The entities in the PyDistSim framework are represented by the :class:`Node` class, which encapsulates the local memory
and processing capabilities of an entity within a distributed environment. In particular, the :attr:`Node.status` attribute models the
current state of each entity.

Restrictions can be enforced by adding them to the :attr:`NodeAlgorithm.algorithm_restrictions` attribute. This
attribute is a list of classes (:class:`Restriction`) representing all the restrictions
that the algorithm must follow.
