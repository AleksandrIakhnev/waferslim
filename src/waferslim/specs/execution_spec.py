'''
BDD-style Lancelot specifications for the behaviour of the core library classes
'''

import lancelot, sys, types
from lancelot.comparators import Type, SameAs, ExceptionValue
from waferslim.execution import Instruction, ExecutionContext, \
                                InstructionException, NoSuchClassException, \
                                NoSuchConstructorException, \
                                NoSuchInstanceException, \
                                NoSuchMethodException, \
                                Make, Import, Call, CallAndAssign
from waferslim.specs.spec_classes import ClassWithNoArgs, ClassWithOneArg, \
                                         ClassWithTwoArgs

class ExecutionContextBehaviour(object):
    ''' Related Specs for ExecutionContext behaviour '''
    
    @lancelot.verifiable
    def get_builtin_type(self):
        ''' get_type() should return any requested builtin type '''
        spec = lancelot.Spec(ExecutionContext())
        spec.get_type('dict').should_be(dict)
        spec.get_type('str').should_be(str)

    @lancelot.verifiable
    def get_imported_module(self):
        ''' get_module() should return a requested module. 
        The same module should be returned on successive invocations. 
        The same module should be returned from different contexts '''
        spec = lancelot.Spec(ExecutionContext())
        spec.get_module('waferslim').should_be(Type(types.ModuleType))
        spec.get_module('waferslim.specs').should_be(Type(types.ModuleType))
        
        same_context = ExecutionContext()
        for name in ('waferslim', 'waferslim.specs.spec_classes'):
            spec.get_module(name).should_be(sys.modules[name])
            module = same_context.get_module(name)
            spec = lancelot.Spec(same_context)
            spec.get_module(name).should_be(SameAs(module))
        
        different_context = ExecutionContext()
        module = different_context.get_module('waferslim.examples')
        spec = lancelot.Spec(ExecutionContext())
        spec.get_module('waferslim.examples').should_be(SameAs(module))

    @lancelot.verifiable
    def get_module_type(self):
        ''' get_type() should return a requested module type, given the fully
        qualified name including module. The same type should be returned on 
        successive invocations. The same type should be returned from
        different contexts. '''
        _types = {}
        _types['waferslim.specs.spec_classes.ClassWithNoArgs'] \
             = ClassWithNoArgs
        _types['waferslim.specs.spec_classes.ClassWithOneArg'] \
             = ClassWithOneArg
        _types['waferslim.specs.spec_classes.ClassWithTwoArgs'] \
             = ClassWithTwoArgs
        
        execution_context = ExecutionContext()
        spec = lancelot.Spec(execution_context)
        for name, _type in _types.items():
            spec.get_type(name).should_be(_type)
            
            same_type = execution_context.get_type(name)
            spec.get_type(name).should_be(SameAs(same_type))
            
            different_context_type = ExecutionContext().get_type(name)
            spec.get_type(name).should_be(SameAs(different_context_type))
            
    @lancelot.verifiable
    def raises_exceptions(self):
        ''' Requesting a non-existent module should raise ImportError.
        Requesting a non-existent type should raise TypeError.'''
        spec = lancelot.Spec(ExecutionContext())
        spec.get_module('none.such').should_raise(ImportError)
        spec.get_type('none.such.Type').should_raise(ImportError)
        spec.get_type('NoneSuchType').should_raise(TypeError)
        spec.get_type('waferslim.Mint').should_raise(TypeError)
            
    @lancelot.verifiable
    def stores_instance(self):
        ''' store_instance(name, value) should put the name,value pair in the
        instances dict where it can be retrieved by get_instance(name). 
        instances should be isolated across execution contexts'''
        spec = lancelot.Spec(ExecutionContext())
        spec.get_instance('wafer thin').should_raise(KeyError)

        spec.when(spec.store_instance('wafer thin', 'mint'))
        spec.then(spec.get_instance('wafer thin')).should_be('mint')

        spec = lancelot.Spec(ExecutionContext())
        spec.get_instance('wafer thin').should_raise(KeyError)
        
class BaseInstructionBehaviour(object):
    ''' Related Specs for base Instruction behaviour '''
    
    @lancelot.verifiable
    def params_must_be_list(self):
        ''' The params constructor arg must be a list '''
        new_instance_with_bad_parms = lambda: Instruction('id', 'params')
        spec = lancelot.Spec(new_instance_with_bad_parms)
        spec.__call__().should_raise(TypeError)

        new_instance_with_list_parms = lambda: Instruction('id', ['params'])
        spec = lancelot.Spec(new_instance_with_list_parms)
        spec.__call__().should_not_raise(Exception)
        
    @lancelot.verifiable
    def stores_id_and_params(self):
        ''' The id and params constructor args should be assigned to fields.
        The instruction id should be accessible through a method. '''
        class FakeInstruction(Instruction):
            ''' Fake Instruction to get fields from '''
            def execute(self, execution_context, results):
                ''' Get the fields '''
                return self._params
        spec = lancelot.Spec(FakeInstruction('an_id', ['param1', 'param2']))
        spec.instruction_id().should_be('an_id')
        spec.execute(object(), object()).should_be(['param1', 'param2'])
             
@lancelot.verifiable
def make_creates_instance():
    ''' Make.execute() should instantiate the class & add it to context '''
    package = 'waferslim.specs.spec_classes'
    classes = {ClassWithNoArgs:[],
               ClassWithOneArg:[1],
               ClassWithTwoArgs:['a', 'b']}
    for target in classes.keys():
        name = target.__name__
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        params = [name, '%s.%s' % (package, name), classes[target]]
        make_instruction = Make(name, params)
        spec = lancelot.Spec(make_instruction)
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_type(params[1]).will_return(target),
            execution_context.store_instance(name, Type(target)),
            results.completed_ok(make_instruction)
        )

class MakeExceptionBehaviour(object):
    ''' Exception-related Specs for Make-instruction behaviour '''

    @lancelot.verifiable
    def handles_wrong_args(self):
        ''' NoSuchConstructorException indicates incorrect constructor args '''
        wrong_params = ['creosote', 'FakeClass',
                        ['some unwanted', 'constructor args']
                       ]
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        a_class = ClassWithNoArgs
        make_instruction = Make('wrong params', wrong_params)
        spec = lancelot.Spec(make_instruction)
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_type('FakeClass').will_return(a_class),
            results.raised(make_instruction, 
                           ExceptionValue(NoSuchConstructorException))
        )

    @lancelot.verifiable
    def handles_bad_type(self):
        ''' NoSuchClassException indicates unknown type '''
        wrong_params = ['creosote', 'FakeClass',
                        ['some unwanted', 'constructor args']
                       ]
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        make_instruction = Make('wrong params', wrong_params)
        spec = lancelot.Spec(make_instruction)
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_type('FakeClass').will_raise(TypeError('x')),
            results.raised(make_instruction, 
                           ExceptionValue(NoSuchClassException))
        )

    @lancelot.verifiable
    def handles_bad_import(self):
        ''' NoSuchClassException also indicates import problem '''
        wrong_params = ['creosote', 'FakeClass',
                        ['some unwanted', 'constructor args']
                       ]
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        make_instruction = Make('wrong params', wrong_params)
        spec = lancelot.Spec(make_instruction)
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_type('FakeClass')
                .will_raise(ImportError('y')),
            results.raised(make_instruction, 
                           ExceptionValue(NoSuchClassException))
        )          

@lancelot.verifiable
def call_invokes_method():
    ''' Call instruction should get an instance from context and execute a
    callable method on it, returning the results '''
    methods = {'method_0':[],
               'method_1':[1],
               'method_2':['a', 'b']}
    for target in methods.keys():
        instance = lancelot.MockSpec(name='instance')
        result = ','.join([str(arg) for arg in methods[target]])
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        params = ['instance', 'method', methods[target]]
        call_instruction = Call('id_90', params)
        spec = lancelot.Spec(call_instruction)
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_instance(params[0]).will_return(instance),
            instance.method(*tuple(params[2])).will_return(result),
            results.completed(call_instruction, result)
            )

class CallExceptionBehaviour(object):
    ''' Exception-related Specs for Call-instruction behaviour '''

    @lancelot.verifiable
    def handles_bad_instance(self):
        ''' NoSuchInstanceException indicates bad instance name in Call ''' 
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        params = ['bad_instance', 'method', 'args']
        call_instruction = Call('id_9A', params)
        spec = lancelot.Spec(call_instruction)
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_instance(params[0]).will_raise(KeyError),
            results.raised(call_instruction, 
                           NoSuchInstanceException(params[0]))
            )

    @lancelot.verifiable
    def handles_bad_method(self):
        ''' NoSuchMethodException indicates bad method name for Call target ''' 
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        params = ['instance', 'bad_method', 'args']
        instance = ClassWithNoArgs()
        msg = '%s %s' % (params[1], type(instance))
        
        call_instruction = Call('id_9B', params)
        spec = lancelot.Spec(call_instruction)
        
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_instance(params[0]).will_return(instance),
            results.raised(call_instruction, NoSuchMethodException(msg))
            )

lancelot.grouping(ExecutionContextBehaviour)
lancelot.grouping(BaseInstructionBehaviour)
lancelot.grouping(MakeExceptionBehaviour)
lancelot.grouping(CallExceptionBehaviour)

if __name__ == '__main__':
    lancelot.verify()