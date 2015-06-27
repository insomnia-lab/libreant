Libreant architecture
=======================

Libreant is meant to be a distributed system.
Actually, you can even think of nodes as standalone-systems.
A node is not aware of other nodes. It is a single point of distribution with no 
knowledge of other points. 

The system that binds the nodes together is the aggregator; an aggregator acts only
as a client with respect to the nodes. Therefore multiple aggregators can coexist.
This also implies that the node administration does not involve the management of 
the aggregation mechanism and of the aggregators themselves.
Similarly, it is possible to run an aggregator without running a libreant node.
As a consequence, a node cannot choose whether to be aggregated or not.

The aggregation mechanism is based on Opensearch_, and relies on two mandatory fields:

 - the Opensearch description_

 - the Opensearch response_

meaning that this entries are mandatory on a node in order to be aggregated.
The result component heavily relies on the relevance_ extension of the response spec.

We blindly trust this relevance field, so a malicious node could bias the overall 
result, simply increasing the relevance fields of its entries.
In this way, the management of the aggregators implies also the task of checking
the fairness of the aggregated nodes.


How to set up an aggregator
----------------------------

1. Install Libreant. Follow the instructions on :ref:`dev-installation`.

2. Launch Libreant setting the ``AGHERANT_DESCRIPTIONS`` configuration parameters.
   Its value should be a list of URLs. Each URL represents the Opensearch
   description. For Libreant it's located in ``/description.xml``, so a typical URL looks
   like::
 
       http://your.doma.in/description.xml

   and a typical invocation looks like::

       libreant --agherant-descriptions "http://your.doma.in/description.xml http://other.node/description.xml"
   
   If you want to aggregate the same libreant instance that you are running, there's a shortcut: just use ``SELF``. Here's an example::

       libreant --agherant-descriptions "SELF http://other.node/description.xml"

   .. note::

       Through `agherant` command line program, it's possible to run an aggregator without launching the whole libreant software


.. _Opensearch: http://www.opensearch.org/Home
.. _description: http://www.opensearch.org/Specifications/OpenSearch/1.1#OpenSearch_description_document
.. _response: http://www.opensearch.org/Specifications/OpenSearch/1.1#OpenSearch_response_elements
.. _relevance: http://www.opensearch.org/Specifications/OpenSearch/Extensions/Relevance/1.0 
