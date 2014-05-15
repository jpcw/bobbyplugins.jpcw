#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Doc here.
"""

__docformat__ = 'restructuredtext en'

import re


class Plugin():
    """Base Ckass Plugin."""
    order = 10

    def __init__(self, filename, variables, will_continue=True):
        self.filename = filename
        self.variables = variables
        self.will_continue = will_continue

    def get_filename(self):
        raise NotImplementedError  # pragma nocover


class If_A_and_B_Statement(Plugin):
    """If A and B Statement."""
    order = 20

    def get_filename(self):
        """."""
        statement_regex = re.compile(r"\+__if_[^+]+_and_[^+]+__\+")
        statement = statement_regex.search(self.filename)

        if statement:
            variables = statement.group()[6:-3]
            first, second = variables.split('_and_')
            if first and second in self.variables:
                # be sure we have booelan string response
                trues = ['y', 'yes', 'true', '1']
                check_first = str(self.variables[first]).lower() in trues
                check_second = str(self.variables[second]).lower() in trues

                if all((check_first, check_second)):
                    self.filename = re.sub(statement_regex, '',
                                           self.filename)
                else:
                    return None, self.will_continue

            else:
                msg = '%s statement of filename %s' \
                      'was not found in variables %s'
                raise KeyError(msg % (variables, self.filename,
                                      self.variables))
        return self.filename, self.will_continue


class If_A_or_B_Statement(Plugin):
    """If A or B Statement."""
    order = 30

    def get_filename(self):
        """."""
        statement_regex = re.compile(r"\+__if_[^+]+_or_[^+]+__\+")
        statement = statement_regex.search(self.filename)

        if statement:
            variables = statement.group()[6:-3]
            first, second = variables.split('_or_')
            if first and second in self.variables:
                # be sure we have booelan string response
                trues = ['y', 'yes', 'true', '1']
                check_first = str(self.variables[first]).lower() in trues
                check_second = str(self.variables[second]).lower() in trues

                if any((check_first, check_second)):
                    self.filename = re.sub(statement_regex, '',
                                           self.filename)
                else:
                    return None, self.will_continue

            else:
                msg = '%s statement of filename %s' \
                      'was not found in variables %s'
                raise KeyError(msg % (variables, self.filename,
                                      self.variables))
        return self.filename, self.will_continue


class If_Not_Statement(Plugin):
    """If Not Statement."""
    order = 40

    def get_filename(self):
        """."""
        statement_regex = re.compile(r"\+__if_not_[^+]+__\+")
        statement = statement_regex.search(self.filename)

        if statement:
            var = statement.group()[10:-3]
            if var in self.variables:
                # be sure we have booelan string response
                if str(self.variables[var]).lower() in ['n', 'no',
                                                        'false', '0']:
                    self.filename = re.sub(statement_regex, '',
                                           self.filename)
                else:
                    return None, self.will_continue

            else:
                msg = '%s statement of filename %s' \
                      'was not found in variables %s'
                raise KeyError(msg % (var, self.filename, self.variables))
        return self.filename, self.will_continue


class If_Statement(Plugin):
    """If Statement."""
    order = 50

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
                raise KeyError(msg % (var, self.filename, self.variables))
        return self.filename, self.will_continue


# vim:set et sts=4 ts=4 tw=80:
