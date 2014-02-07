#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Doc here.
"""

__docformat__ = 'restructuredtext en'

import re


class If_Statement():
    """If Statement."""
    order = 10

    def __init__(self, filename, variables, will_continue=True):
        self.filename = filename
        self.variables = variables
        self.will_continue = will_continue

    def get_filename(self):
        """."""
        statement_regex = re.compile(r"\+__if_[^+]+__\+")
        statement = statement_regex.search(self.filename)

        if statement:
            var = statement.group()[6:-3]
            if var in self.variables:
                # be sure we have booelan string response
                if str(self.variables[var]).lower() in ['y', 'yes',
                                                        'true', '1']:
                    self.filename = re.sub(statement_regex, '',
                                           self.filename)
                else:
                    return None, self.will_continue

            else:
                msg = '%s statement of filename %s' \
                      'was not found in variables %s'
                raise KeyError(msg % (var, self.filename, self. variables))
        return self.filename, self.will_continue

# vim:set et sts=4 ts=4 tw=80:
