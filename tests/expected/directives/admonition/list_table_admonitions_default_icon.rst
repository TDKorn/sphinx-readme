.. |.sphinx-readme+readme_admonition_icons| replace:: ``readme_admonition_icons``
.. _.sphinx-readme+readme_admonition_icons: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html#confval-readme_admonition_icons
.. |.sphinx-readme+readme_default_admonition_icon| replace:: ``readme_default_admonition_icon``
.. _.sphinx-readme+readme_default_admonition_icon: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html#confval-readme_default_admonition_icon


Generic Admonitions
============================


.. list-table::
   :header-rows: 1
   
   * - 📝 Admonition Title
   * - This is an admonition with the note class.


This is outside of the admonition


.. list-table::
   :header-rows: 1
   
   * - 🔥 Custom Admonition Classes
   * - This is an admonition with a custom class. You can add icons for custom admonition classes
       and override predefined classes by setting the |.sphinx-readme+readme_admonition_icons|_ confval



.. list-table::
   :header-rows: 1
   
   * - 😱 Overriding Predefined Icons for Default Admonition Classes
   * - This is an admonition with the ``danger`` class.

       However, the icon has been overridden to use "😱" instead of the default value of "☣"



.. list-table::
   :header-rows: 1
   
   * - ✨ Admonition Without a Class
   * - This is an admonition with no class. It uses the |.sphinx-readme+readme_default_admonition_icon|_
       as an icon



.. list-table::
   :header-rows: 1
   
   * - ✨ Admonition With an Undefined Class
   * - This is an admonition with a class that's not in the |.sphinx-readme+readme_admonition_icons|_ mapping.

       Since the icon can't be found, it uses the |.sphinx-readme+readme_default_admonition_icon|_.



Specific Admonitions
======================

The default specific admonitions are any of: "attention", "caution", "danger", "error", "hint", "important", "note", "tip", "warning"


.. list-table::
   :header-rows: 1
   
   * - 🔔️ Attention
   * - Attention!



.. list-table::
   :header-rows: 1
   
   * - ⚠️ Caution
   * - Caution!



.. list-table::
   :header-rows: 1
   
   * - 😱 Danger
   * - Danger!

       This should also use the overridden icon.



.. list-table::
   :header-rows: 1
   
   * - ⛔ Error
   * - Error!



.. list-table::
   :header-rows: 1
   
   * - 🧠 Hint
   * - Hint!



.. list-table::
   :header-rows: 1
   
   * - 📢 Important
   * - Important!



.. list-table::
   :header-rows: 1
   
   * - 📝 Note
   * - Note!



.. list-table::
   :header-rows: 1
   
   * - 💡 Tip
   * - Tip!



.. list-table::
   :header-rows: 1
   
   * - 🚩 Warning
   * - Warning!




.. list-table::
   :header-rows: 1
   
   * - 💡 Tip
   * - This is a multi-line tip!

       Here's the second line.


This is outside the admonition


.. list-table::
   :header-rows: 1
   
   * - 🚩 Warning
   * - This is a single line warning written on multiple lines.
       There is no blank line before the second line!



.. list-table::
   :header-rows: 1
   
   * - 📝 Note
   * - This is a note admonition. The content is two lines below the directive.



.. list-table::
   :header-rows: 1
   
   * - 🔔️ Attention
   * - This is an attention admonition. The content is
       directly below the directive.


Nested Admonitions
=====================


.. list-table::
   :header-rows: 1
   
   * - 📝 Admonition Title
   * - This is a generic admonition with the note class.

       The admonition text is multiple lines long.


       .. list-table::
          :header-rows: 1
   
          * - 💡 Nested Admonitions
          * - Nested admonitions are admonitions that are nested.


       This is back in the original admonition


This is outside of the admonition



.. list-table::
   :header-rows: 1
   
   * - 💡 Admonition Title
   * - This is a generic admonition with the tip class.

       The admonition text is multiple lines long.


       .. list-table::
          :header-rows: 1
   
          * - 📢 Important
          * - This is a nested specific admonition.

              It's nested.


       This is back in the original admonition


This is outside of the admonition



.. list-table::
   :header-rows: 1
   
   * - 🧠 Hint
   * - This is a specific admonition.

       Here is another line.


       .. list-table::
          :header-rows: 1
   
          * - ⚠️ Caution
          * - This is a nested specific admonition.

              It's nested within another specific admonition.


       This is back in the original admonition


This is outside of the admonition



.. list-table::
   :header-rows: 1
   
   * - 🧠 Hint
   * - This is a specific admonition.

       Here is another line.


       .. list-table::
          :header-rows: 1
   
          * - 🔥 This is a nested generic admonition.
          * - It's nested within the specific admonition.


       This is back in the original admonition


This is outside of the admonition



Admonitions in Only Directives
================================


.. list-table::
   :header-rows: 1
   
   * - 🧠 Generic Admonition in an Only Directive
   * - This is nested in an only directive.

       Here's another line.


       .. list-table::
          :header-rows: 1
   
          * - 🔥 Generic Admonition Nested in a Generic Admonition Nested in an Only Directive
          * - There's a lot of nesting going on here


       This is back in the first admonition.



.. list-table::
   :header-rows: 1
   
   * - ✨ Generic Admonition With No Class in an Only Directive
   * - This is nested in an only directive.



.. list-table::
   :header-rows: 1
   
   * - 📝 Note
   * - this is a specific admonition that is nested in an only directive

       here's the second line



.. list-table::
   :header-rows: 1
   
   * - 💡 Tip
   * - this is another specific admonition that is nested
       in an only directive, with a different format



End of file nested admonition
==============================


.. list-table::
   :header-rows: 1
   
   * - 🧠 Hint
   * - blah


       .. list-table::
          :header-rows: 1
   
          * - 🧠 Hint
          * - this nested admonition is at the end of the file with no newline after it


