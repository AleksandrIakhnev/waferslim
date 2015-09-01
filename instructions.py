'''
Instruction classes that invoke actions on some underlying "system under test".

The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009-2010 by the author(s). All rights reserved
'''
import logging

_BAD_INSTRUCTION = 'INVALID_STATEMENT'
_NO_CLASS = 'NO_CLASS'
_NO_CONSTRUCTION = 'COULD_NOT_INVOKE_CONSTRUCTOR'
_NO_INSTANCE = 'NO_INSTANCE'
_NO_METHOD = 'NO_METHOD_IN_CLASS'


class Instruction(object):
    ''' Base class for instructions '''

    def __init__(self, instruction_id, params):
        ''' Specify the id of this instruction, and its params.
        Params must be a list. '''
        if not isinstance(params, list):
            raise TypeError('%r is not a list' % params)
        self._id = instruction_id
        self._params = params

    def instruction_id(self):
        ''' Return the id of this instruction '''
        return self._id

    def __repr__(self):
        ''' Return a meaningful representation of the Instruction '''
        return '%s %s: %s' % (type(self).__name__, self._id, self._params)

    def execute(self, execution_context, results):
        ''' Base execute() is only called when the instruction type
        was unrecognised -- fail with _BAD_INSTRUCTION '''
        results.failed(self, '%s %s' % (_BAD_INSTRUCTION, self._params[0]))


class Import(Instruction):
    ''' An "import <path or module context>" instruction '''

    def execute(self, execution_context, results):
        ''' Adds an imported path or module context to the execution context'''
        path = self._params[0]
        execution_context.import_path(path)
        results.completed(self)

    def _ispath(self, possible_path):
        ''' True if this is a path, False otherwise '''
        return possible_path.find('/') != -1 or possible_path.find('\\') != -1


class Make(Instruction):
    ''' A "make <instance>, <class>, <args>..." instruction '''

    def execute(self, execution_context, results):
        ''' Create a class instance and add it to the execution context '''
        try:
            target = execution_context.get_type(self._params[1])
        except (TypeError, ImportError) as error:
            cause = '%s %s %s' % (_NO_CLASS, self._params[1], error.args[0])
            results.failed(self, cause)
            raise
            return

        args = execution_context.to_args(self._params, 2)
        try:
            instance = target(*args)
            execution_context.store_instance(self._params[0], instance)
            results.completed(self)
        except TypeError as error:
            cause = '%s %s %s' % (_NO_CONSTRUCTION,
                                  self._params[1], error.args[0])
            results.failed(self, cause)


class Call(Instruction):
    ''' A "call <instance>, <function>, <args>..." instruction '''

    def execute(self, execution_context, results):
        ''' Delegate to _invoke_call then record results on completion '''
        result, is_ok = self._invoke(execution_context, results, self._params)
        if is_ok:
            results.completed(self, result)

    def _invoke(self, execution_context, results, params):
        ''' Get an instance from the execution context and invoke a method:
        -  try to invoke the named method on the instance
        -  try to invoke the named method on the system under test
        -  try to invoke the named method via libraries
        '''
        instance_name, target_name = params[0], params[1]
        instance = execution_context.get_instance(instance_name)
        try:
            if instance is not None:
                target = execution_context.target_for(instance, target_name)
                if target is not None:
                    args = execution_context.to_args(params, 2)
                    result = target(*args)
                    return (result, True)
                else:
                    cause = '%s %s %s' % (_NO_METHOD, target_name,
                                          type(instance).__name__)
                    results.failed(self, cause)
            else:  # instance is None
                results.failed(self, '%s %s' % (_NO_INSTANCE, instance_name))
        except KeyError:
            logging.warning('Method %s not found in class %s', target_name, instance_name)
        return (None, False)


class CallAndAssign(Call):
    ''' A "callAndAssign <symbol>, <instance>, <function>, <args>..."
    instruction '''

    def execute(self, execution_context, results):
        ''' Delegate to _invoke_call then set variable and record results
        on completion '''
        params_copy = []
        params_copy.extend(self._params)
        symbol_name = params_copy.pop(0)

        result, is_ok = self._invoke(execution_context, results, params_copy)
        if is_ok:
            execution_context.store_symbol(symbol_name, result)
            results.completed(self, result)
