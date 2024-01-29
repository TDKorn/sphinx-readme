Generic Admonitions
============================

.. admonition:: Admonition Title
   :class: note

   This is an admonition with the note class.

This is outside of the admonition

.. admonition:: Custom Admonition Classes
   :class: custom

   This is an admonition with a custom class. You can add icons for custom admonition classes
   and override predefined classes by setting the :external:confval:`readme_admonition_icons` confval

.. admonition:: Overriding Predefined Icons for Default Admonition Classes
   :class: danger

   This is an admonition with the ``danger`` class.

   However, the icon has been overridden to use "😱" instead of the default value of "☣"

.. admonition:: Admonition Without a Class

   This is an admonition with no class. It uses the :external:confval:`readme_default_admonition_icon`
   as an icon

.. admonition:: Admonition With an Undefined Class
   :class: undefined

   This is an admonition with a class that's not in the :external:confval:`readme_admonition_icons` mapping.

   Since the icon can't be found, it uses the :external:confval:`readme_default_admonition_icon`.


Specific Admonitions
======================

The default specific admonitions are any of: "attention", "caution", "danger", "error", "hint", "important", "note", "tip", "warning"

.. attention:: Attention!

.. caution:: Caution!

.. danger:: Danger!

   This should also use the overridden icon.

.. error:: Error!

.. hint:: Hint!

.. important:: Important!

.. note:: Note!

.. tip:: Tip!

.. warning:: Warning!


.. tip:: This is a multi-line tip!

   Here's the second line.

This is outside the admonition

.. warning:: This is a single line warning written on multiple lines.
   There is no blank line before the second line!

.. note::

   This is a note admonition. The content is two lines below the directive.

.. attention::
   This is an attention admonition. The content is
   directly below the directive.

Nested Admonitions
=====================

.. admonition:: Admonition Title
   :class: note

   This is a generic admonition with the note class.

   The admonition text is multiple lines long.

   .. admonition:: Nested Admonitions
      :class: tip

      Nested admonitions are admonitions that are nested.

   This is back in the original admonition

This is outside of the admonition


.. admonition:: Admonition Title
   :class: tip

   This is a generic admonition with the tip class.

   The admonition text is multiple lines long.

   .. important:: This is a nested specific admonition.

      It's nested.

   This is back in the original admonition

This is outside of the admonition


.. hint:: This is a specific admonition.

   Here is another line.

   .. caution:: This is a nested specific admonition.

      It's nested within another specific admonition.

   This is back in the original admonition

This is outside of the admonition


.. hint:: This is a specific admonition.

   Here is another line.

   .. admonition:: This is a nested generic admonition.
      :class: custom

      It's nested within the specific admonition.

   This is back in the original admonition

This is outside of the admonition



Admonitions in Only Directives
================================

.. only:: readme

   .. admonition:: Generic Admonition in an Only Directive
      :class: hint

      This is nested in an only directive.

      Here's another line.

      .. admonition:: Generic Admonition Nested in a Generic Admonition Nested in an Only Directive
         :class: custom

         There's a lot of nesting going on here

      This is back in the first admonition.

.. only:: readme

   .. admonition:: Generic Admonition With No Class in an Only Directive

      This is nested in an only directive.

.. only:: readme

   .. note:: this is a specific admonition that is nested in an only directive

      here's the second line

.. only:: readme

   .. tip::

      this is another specific admonition that is nested
      in an only directive, with a different format


End of file nested admonition
==============================

.. hint:: blah

   .. hint:: this nested admonition is at the end of the file with no newline after it