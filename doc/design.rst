****************************************************
Software Design
****************************************************

.. _priority-handle-set-section:

Priority Handle Set
-------------------

We have a number of places where we want to have a 
`chain-of-responsibility <https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern>`_, with the addition of an ordering based on a priority order. We
also want to be able to modify the handles, starting with a default set of
handles. So for example while reading a NitfFile we would like to process
images using a set of handles (e.g., read JPEG 2000, read using numpy arrays,
etc.), that we could potentially change for a particular NitfFile (e.g.,
add a special reader for an unusual format).

To support this, we have a class PriorityHandleSet. This is very similar to
a `priority queue <https://en.wikipedia.org/wiki/Priority_queue>`_ except that
we:

* Don't want to actually pop from a queue, rather we iterate through the stored
  items.
* The items aren't totally ordered. We iterate through items with the same
  priority in an arbitrary order
* We want to have a default list of handlers, that can then be modified.

The design for this is shown in :numref:`priority_handle_set`.

.. _priority_handle_set:
.. uml::
   :caption: Priority Handle Set

   abstract class PriorityHandleSet {
      +add_handle(h, priority_order=0)
      +discard_handle(h)
      {static} add_default_handle(cls, h, priority_order=0)
      {static} discard_default_handle(cls, h, priority_order=0)
      {static} default_handle_set()
      +handle(*args, **keywords)
      {abstract} handle_h(h, *args, **keywords)
   }
   note top
      This class also adds the normal python
      magic functions to be able to iterate like
      a set.

      Higher numbers in the priority order are
      returned first.

      We also have proper copy semantics, so you
      can call copy.copy(t.default_handle_set())
      to get a copy of the default set that can be
      modified.
   end note

   class NitfDesHandleSet
   note top
      Process NitfDes
   end note

   class NitfImageHandleSet
   note right
      Process NitfImage
   end note

   PriorityHandleSet <|-- NitfDesHandleSet
   PriorityHandleSet <|-- NitfImageHandleSet

The PriorityHandleSet has members for adding and removing "Handles". A handle
is purposely vague, it is any object that the derived class wants to be.
And in some cases the object is actually a class - so for example
NitfImageHandleSet uses handles that are classes derived from NitfImage.

The function handle forwards work to the function handle_h, as shown in
:numref:`handle_sequence`

.. _handle_sequence:
.. uml::
   :caption: handler_set:DerivedFromPriorityHandleSet sequence diagram

   caller -> "handler_set:DerivedFromPriorityHandleSet" as hset: 1 handle(*args, **keywords)
   loop h:HandleObjects
       hset -> hset : 1.1 handle_h(h,*args,**keywords)
       alt h couldn't handle
          hset -> hset: return (False, None)
       else h could handle
          hset -> hset: return (True, res)
       end
       note right hset
          Continue looping until the
	  first h can handle the args
       end note
   end
   
