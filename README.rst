.. contents::

Introduction
============

Flexibles rendering plugins for `mrbobby <https://github.com/jpcw/mr.bobby>`_

Plugins
========

If_Statement
--------------

Add an **+__if_any.var__+** statement pattern to influence rendering. 

For example foo/**+__if_render.me__+**\+author+/+age+.bobby  given variables :

 + author =  Foo 
 + age = 12 


if **render.me** is True:

    foo/Foo/12 will be rendered 

else:

    foo/ will be rendered. 
    
Please notice that only **('y', 'yes', 'true', True, 1)** are True, anything else will be considred as False.



Tests
=====

bobbyplugins.jpcw is continuously 

+ tested on Travis |travisstatus|_ 

+ coverage tracked on coveralls.io |coveralls|_.

.. |travisstatus| image:: https://api.travis-ci.org/jpcw/bobbyplugins.jpcw.png
.. _travisstatus:  http://travis-ci.org/jpcw/bobbyplugins.jpcw


.. |coveralls| image:: https://coveralls.io/repos/jpcw/bobbyplugins.jpcw/badge.png
.. _coveralls: https://coveralls.io/r/jpcw/bobbyplugins.jpcw



