.. |.sphinx-readme+readme_admonition_icons| replace:: ``readme_admonition_icons``
.. _.sphinx-readme+readme_admonition_icons: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html#confval-readme_admonition_icons
.. |.sphinx-readme+readme_default_admonition_icon| replace:: ``readme_default_admonition_icon``
.. _.sphinx-readme+readme_default_admonition_icon: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html#confval-readme_default_admonition_icon


Generic Admonitions
============================


.. raw:: html

   <table>
       <tr align="left">
           <th>

📝 Admonition Title

.. raw:: html

   </th>
   <tr><td>

This is an admonition with the note class.

.. raw:: html

   </td></tr>
   </table>


This is outside of the admonition


.. raw:: html

   <table>
       <tr align="left">
           <th>

🔥 Custom Admonition Classes

.. raw:: html

   </th>
   <tr><td>

This is an admonition with a custom class. You can add icons for custom admonition classes
and override predefined classes by setting the |.sphinx-readme+readme_admonition_icons|_ confval

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

😱 Overriding Predefined Icons for Default Admonition Classes

.. raw:: html

   </th>
   <tr><td>

This is an admonition with the ``danger`` class.

However, the icon has been overridden to use "😱" instead of the default value of "☣"

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

✨ Admonition Without a Class

.. raw:: html

   </th>
   <tr><td>

This is an admonition with no class. It uses the |.sphinx-readme+readme_default_admonition_icon|_
as an icon

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

✨ Admonition With an Undefined Class

.. raw:: html

   </th>
   <tr><td>

This is an admonition with a class that's not in the |.sphinx-readme+readme_admonition_icons|_ mapping.

Since the icon can't be found, it uses the |.sphinx-readme+readme_default_admonition_icon|_.

.. raw:: html

   </td></tr>
   </table>



Specific Admonitions
======================

The default specific admonitions are any of: "attention", "caution", "danger", "error", "hint", "important", "note", "tip", "warning"


.. raw:: html

   <table>
       <tr align="left">
           <th>

🔔️ Attention

.. raw:: html

   </th>
   <tr><td>

Attention!

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

⚠️ Caution

.. raw:: html

   </th>
   <tr><td>

Caution!

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

😱 Danger

.. raw:: html

   </th>
   <tr><td>

Danger!

This should also use the overridden icon.

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

⛔ Error

.. raw:: html

   </th>
   <tr><td>

Error!

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

🧠 Hint

.. raw:: html

   </th>
   <tr><td>

Hint!

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

📢 Important

.. raw:: html

   </th>
   <tr><td>

Important!

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

📝 Note

.. raw:: html

   </th>
   <tr><td>

Note!

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

💡 Tip

.. raw:: html

   </th>
   <tr><td>

Tip!

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

🚩 Warning

.. raw:: html

   </th>
   <tr><td>

Warning!

.. raw:: html

   </td></tr>
   </table>




.. raw:: html

   <table>
       <tr align="left">
           <th>

💡 Tip

.. raw:: html

   </th>
   <tr><td>

This is a multi-line tip!

Here's the second line.

.. raw:: html

   </td></tr>
   </table>


This is outside the admonition


.. raw:: html

   <table>
       <tr align="left">
           <th>

🚩 Warning

.. raw:: html

   </th>
   <tr><td>

This is a single line warning written on multiple lines.
There is no blank line before the second line!

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

📝 Note

.. raw:: html

   </th>
   <tr><td>

This is a note admonition. The content is two lines below the directive.

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

🔔️ Attention

.. raw:: html

   </th>
   <tr><td>

This is an attention admonition. The content is
directly below the directive.

.. raw:: html

   </td></tr>
   </table>


Nested Admonitions
=====================


.. raw:: html

   <table>
       <tr align="left">
           <th>

📝 Admonition Title

.. raw:: html

   </th>
   <tr><td>

This is a generic admonition with the note class.

The admonition text is multiple lines long.


.. raw:: html

   <table>
       <tr align="left">
           <th>

💡 Nested Admonitions

.. raw:: html

   </th>
   <tr><td>

Nested admonitions are admonitions that are nested.

.. raw:: html

   </td></tr>
   </table>


This is back in the original admonition

.. raw:: html

   </td></tr>
   </table>


This is outside of the admonition



.. raw:: html

   <table>
       <tr align="left">
           <th>

💡 Admonition Title

.. raw:: html

   </th>
   <tr><td>

This is a generic admonition with the tip class.

The admonition text is multiple lines long.


.. raw:: html

   <table>
       <tr align="left">
           <th>

📢 Important

.. raw:: html

   </th>
   <tr><td>

This is a nested specific admonition.

It's nested.

.. raw:: html

   </td></tr>
   </table>


This is back in the original admonition

.. raw:: html

   </td></tr>
   </table>


This is outside of the admonition



.. raw:: html

   <table>
       <tr align="left">
           <th>

🧠 Hint

.. raw:: html

   </th>
   <tr><td>

This is a specific admonition.

Here is another line.


.. raw:: html

   <table>
       <tr align="left">
           <th>

⚠️ Caution

.. raw:: html

   </th>
   <tr><td>

This is a nested specific admonition.

It's nested within another specific admonition.

.. raw:: html

   </td></tr>
   </table>


This is back in the original admonition

.. raw:: html

   </td></tr>
   </table>


This is outside of the admonition



.. raw:: html

   <table>
       <tr align="left">
           <th>

🧠 Hint

.. raw:: html

   </th>
   <tr><td>

This is a specific admonition.

Here is another line.


.. raw:: html

   <table>
       <tr align="left">
           <th>

🔥 This is a nested generic admonition.

.. raw:: html

   </th>
   <tr><td>

It's nested within the specific admonition.

.. raw:: html

   </td></tr>
   </table>


This is back in the original admonition

.. raw:: html

   </td></tr>
   </table>


This is outside of the admonition



Admonitions in Only Directives
================================


.. raw:: html

   <table>
       <tr align="left">
           <th>

🧠 Generic Admonition in an Only Directive

.. raw:: html

   </th>
   <tr><td>

This is nested in an only directive.

Here's another line.


.. raw:: html

   <table>
       <tr align="left">
           <th>

🔥 Generic Admonition Nested in a Generic Admonition Nested in an Only Directive

.. raw:: html

   </th>
   <tr><td>

There's a lot of nesting going on here

.. raw:: html

   </td></tr>
   </table>


This is back in the first admonition.

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

✨ Generic Admonition With No Class in an Only Directive

.. raw:: html

   </th>
   <tr><td>

This is nested in an only directive.

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

📝 Note

.. raw:: html

   </th>
   <tr><td>

this is a specific admonition that is nested in an only directive

here's the second line

.. raw:: html

   </td></tr>
   </table>



.. raw:: html

   <table>
       <tr align="left">
           <th>

💡 Tip

.. raw:: html

   </th>
   <tr><td>

this is another specific admonition that is nested
in an only directive, with a different format

.. raw:: html

   </td></tr>
   </table>



End of file nested admonition
==============================


.. raw:: html

   <table>
       <tr align="left">
           <th>

🧠 Hint

.. raw:: html

   </th>
   <tr><td>

blah


.. raw:: html

   <table>
       <tr align="left">
           <th>

🧠 Hint

.. raw:: html

   </th>
   <tr><td>

this nested admonition is at the end of the file with no newline after it

.. raw:: html

   </td></tr>
   </table>


.. raw:: html

   </td></tr>
   </table>

