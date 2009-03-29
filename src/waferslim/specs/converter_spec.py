'''
BDD-style Lancelot specifications for the behaviour of the core library classes
'''

from waferslim.converters import register_converter, converter_for, \
    convert_arg, convert_result, Converter, StrConverter, \
    TrueFalseConverter, YesNoConverter, FromConstructorConverter, \
    DateConverter, TimeConverter, DatetimeConverter, IterableConverter, \
    TableTableConstants
import lancelot, datetime, threading
from lancelot.comparators import FloatValue, Type

class Fake(object):
    ''' Fake class whose str() value is determined by the constructor '''
    def __init__(self, str_value):
        ''' Specify value to return from str() '''
        self.str_value = str_value
    def __str__(self):
        ''' Return the specified str() value '''
        return self.str_value

@lancelot.verifiable
def base_converter_to_string():
    ''' Base Converter class should use str() as default implementation '''
    fake = Fake('Six bottles of Chateau Latour')
    spec = lancelot.Spec(Converter())
    spec.to_string(fake).should_be(fake.str_value)

@lancelot.verifiable
def base_converter_from_string():
    ''' Base Converter class should raise NotImplementedError '''
    spec = lancelot.Spec(Converter())
    spec.from_string('anything').should_raise(NotImplementedError)

@lancelot.verifiable
def default_converter_for():
    ''' If no registered converter exists for the type of value being converted
    then the base Converter class should be used. '''
    fake = Fake('And a double Jeroboam of champagne')
    spec = lancelot.Spec(converter_for)
    spec.converter_for(fake).should_be(Type(Converter))
    spec.converter_for(Fake).should_be(Type(Converter))
    
@lancelot.verifiable
def registered_converter_for_():
    ''' converter_for() should supply the registered converter for the type
    of value being converted if it exists. '''
    fake = Fake('I think I can only manage six crates today')
    register_converter(Fake, Converter())
    spec = lancelot.Spec(converter_for)
    spec.converter_for(fake).should_be(Type(Converter))
    spec.converter_for(Fake).should_be(Type(Converter))
    
@lancelot.verifiable
def register_converter_checks_attrs():
    ''' register_converter() will not accept a converter_instance without
    both to_string() and from_string() methods.'''
    converter = Fake("I'll have the lot")
    fake_method = lambda value: value
    spec = lancelot.Spec(register_converter)
    spec.register_converter(converter).should_raise(TypeError)

    converter.to_string = fake_method
    spec.register_converter(Fake, converter).should_raise(TypeError)

    del(converter.to_string)
    converter.from_string = fake_method
    spec.register_converter(Fake, converter).should_raise(TypeError)

    converter.to_string = fake_method
    converter.from_string = fake_method
    spec.register_converter(Fake, converter).should_not_raise(TypeError)
    
@lancelot.verifiable
def converters_are_thread_local():
    ''' Registered converters should be thread-local: a converter registered
    in one thread should be isolated from those registered in other threads'''
    def yes_no():
        ''' method to register a converter in a separate thread ''' 
        register_converter(bool, YesNoConverter())
        other_converter = converter_for(bool)
        lancelot.Spec(other_converter).it().should_be(Type(YesNoConverter))
    yes_no_thread = threading.Thread(target=yes_no)
    yes_no_thread.start()
    yes_no_thread.join()
    lancelot.Spec(converter_for(bool)).it().should_be(Type(TrueFalseConverter))
    
@lancelot.verifiable
def str_converter_behaviour():
    ''' StrConverter to_string() and from_string() should be the value
    as there is no actual conversion to do. '''
    spec = lancelot.Spec(StrConverter())
    spec.to_string('do come in').should_be('do come in')
    spec.from_string('mr death').should_be('mr death')

@lancelot.verifiable
def yesno_converter_behaviour():
    ''' YesNoConverter to_string() should be yes/no; from_string() should be
    True for any mixed case equivalent to yes; False otherwise. '''
    spec = lancelot.Spec(YesNoConverter())
    spec.to_string(True).should_be('yes')
    spec.to_string(False).should_be('no')
    spec.from_string('yes').should_be(True)
    spec.from_string('Yes').should_be(True)
    spec.from_string('True').should_be(False)
    spec.from_string('true').should_be(False)
    spec.from_string('no').should_be(False)
    spec.from_string('No').should_be(False)
    spec.from_string('false').should_be(False)
    spec.from_string('False').should_be(False)
    spec.from_string('jugged hare').should_be(False)
    
@lancelot.verifiable
def truefalse_converter_behaviour():
    ''' TrueFalseConverter to_string() should be true/false; from_string()  
    should be True for any mixed case equivalent to true; False otherwise. '''
    spec = lancelot.Spec(TrueFalseConverter())
    spec.to_string(True).should_be('true')
    spec.to_string(False).should_be('false')
    spec.from_string('yes').should_be(False)
    spec.from_string('Yes').should_be(False)
    spec.from_string('True').should_be(True)
    spec.from_string('true').should_be(True)
    spec.from_string('no').should_be(False)
    spec.from_string('No').should_be(False)
    spec.from_string('false').should_be(False)
    spec.from_string('False').should_be(False)
    spec.from_string('jugged hare').should_be(False)

@lancelot.verifiable
def from_constructor_conversion():
    ''' FromConstructorConverter converts using a type constructor, which
    is handy for int and float conversion '''
    spec = lancelot.Spec(FromConstructorConverter(int))
    spec.to_string(1).should_be('1')
    spec.to_string(2).should_be('2')
    spec.from_string('2').should_be(2)
    spec.from_string('1').should_be(1)
    
    spec = lancelot.Spec(FromConstructorConverter(float))
    spec.to_string(3.141).should_be('3.141')
    spec.from_string('3.141').should_be(3.141)

@lancelot.verifiable
def date_converter_behaviour():
    ''' DateConverter should convert to/from datetime.date type using 
    iso-standard format (4digityear-2digitmonth-2digitday)'''
    spec = lancelot.Spec(DateConverter())
    spec.to_string(datetime.date(2009, 1, 31)).should_be('2009-01-31')
    spec.from_string('2009-01-31').should_be(datetime.date(2009, 1, 31))
    
@lancelot.verifiable
def time_converter_behaviour():
    ''' TimeConverter should convert to/from datetime.date type using
    iso-standard format (2digithour:2digitminute:2digitsecond - with or without
    an additional optional .6digitmillis)'''
    spec = lancelot.Spec(TimeConverter())
    spec.to_string(datetime.time(1, 2, 3)).should_be('01:02:03')
    spec.to_string(datetime.time(1, 2, 3, 4)).should_be('01:02:03.000004')
    spec.from_string('01:02:03').should_be(datetime.time(1, 2, 3))
    spec.from_string('01:02:03.000004').should_be(datetime.time(1, 2, 3, 4))
    
@lancelot.verifiable
def datetime_converter_behaviour():
    ''' DatetimeConverter should convert to/from datetime.datetime type using
    combination of iso-standard formats ("dateformat<space>timeformat")'''
    spec = lancelot.Spec(DatetimeConverter())
    date_part, time_part = '2009-02-28', '21:54:32.987654'
    datetime_value = datetime.datetime(2009, 2, 28, 21, 54, 32, 987654)
    spec.to_string(datetime_value).should_be(
        '2009-02-28 21:54:32.987654')
    spec.from_string('2009-02-28 21:54:32.987654').should_be(
        datetime.datetime.combine(DateConverter().from_string(date_part),
                                  TimeConverter().from_string(time_part))
        )

class IterableConverterBehaviour(object):
    ''' Group of related specs for conversion of iterable types '''
    
    @lancelot.verifiable
    def to_string_converts_each_item(self):
        ''' to_string() should convert each item using a type-specific 
        converter for that item'''
        a_list = [1, datetime.date(2009, 5, 5), True]
        list_of_lists = [[1, 2], [True, False]]
        spec = lancelot.Spec(IterableConverter())
        spec.to_string(a_list).should_be(['1', '2009-05-05', 'true'])
        spec.to_string(list_of_lists).should_be([['1', '2'], ['true', 'false']])

lancelot.grouping(IterableConverterBehaviour)
    
class ASystemUnderTest(object):
    ''' Dummy class with setter and result methods that can be decorated '''
    def set_afloat(self, float_value):
        ''' setter method to be decorated '''
        self.float_value = float_value
    def multiply(self, an_int, a_float):
        ''' another setter method to be decorated '''
        return a_float * an_int
    def add(self, one_int, another_int):
        ''' result method to be decorated '''
        return one_int + another_int

class ConvertArgBehaviour(object):
    ''' Group of related specs for convert_arg() behaviour.
    convert_arg() is a function decorator that should convert  
    args supplied to the function into the required python type'''

    @lancelot.verifiable
    def returns_callable_to_type(self):
        ''' decorator for 'to_type' should return a callable that takes 2 
        or more args. Invoking that callable should convert each arg.'''
        decorated_fn = convert_arg(to_type=float)(ASystemUnderTest.set_afloat)
        
        spec = lancelot.Spec(decorated_fn)
        spec.__call__('1.99').should_raise(TypeError) # only 1 arg
        
        sut = ASystemUnderTest()
        spec.__call__(sut, '1.99').should_not_raise(TypeError)
        
        spec.when(spec.__call__(sut, '2.718282'))
        spec.then(lambda: sut.float_value).should_be(2.718282)

        decorated_fn = convert_arg(to_type=int)(ASystemUnderTest.add)
        spec = lancelot.Spec(decorated_fn)
        spec.__call__(sut, '1', '2').should_be(3)
        
    @lancelot.verifiable
    def returns_callable_using(self):
        ''' decorator for 'using' should return a callable that takes 2 
        or more args. Invoking that callable should convert each arg.'''
        # Ensure that type-standard converters are not used!
        register_converter(float, Converter())
        register_converter(int, Converter())
        
        # Check that standard converters are not being used 
        decorated_fn = convert_arg(to_type=float)(ASystemUnderTest.set_afloat)
        spec = lancelot.Spec(decorated_fn)
        spec.__call__(None, '1.99').should_raise(NotImplementedError)
        
        # Now proceed with our specific "using" float converter...
        cnvt = FromConstructorConverter(float)
        decorated_fn = convert_arg(using=cnvt)(ASystemUnderTest.set_afloat)
        
        spec = lancelot.Spec(decorated_fn)
        spec.__call__('1.99').should_raise(TypeError) # only 1 arg
        
        sut = ASystemUnderTest()
        spec.__call__(sut, '1.99').should_not_raise(TypeError)
        
        spec.when(spec.__call__(sut, '2.718282'))
        spec.then(lambda: sut.float_value).should_be(2.718282)

        # Check that standard converters are not being used 
        decorated_fn = convert_arg(to_type=int)(ASystemUnderTest.add)        
        spec = lancelot.Spec(decorated_fn)
        spec.__call__(sut, '1', '2').should_raise(NotImplementedError)
        
        # Now proceed with our specific "using" float converter...
        cnvt = FromConstructorConverter(int)
        decorated_fn = convert_arg(using=cnvt)(ASystemUnderTest.add)
        spec = lancelot.Spec(decorated_fn)
        spec.__call__(sut, '1', '2').should_be(3)

        # Reset type-standard converters
        register_converter(float, FromConstructorConverter(float))
        register_converter(int, FromConstructorConverter(int))

    @lancelot.verifiable
    def handles_multiple_arg_types(self):
        ''' The decorator should handle conversion of multiple args of
        multiple types '''
        multiply = ASystemUnderTest.multiply
        sut = ASystemUnderTest()
        decorated_fn = convert_arg(to_type=(int, float))(multiply)
        spec = lancelot.Spec(decorated_fn)
        spec.__call__(sut, '4', '1.2').should_be(FloatValue(4.8))

        converters = (FromConstructorConverter(int), 
                      FromConstructorConverter(float))
        decorated_fn = convert_arg(using=converters)(multiply)
        spec = lancelot.Spec(decorated_fn)
        spec.__call__(sut, '3', '1.1').should_be(FloatValue(3.3))
                
    @lancelot.verifiable
    def fails_without_type_converter(self):
        ''' decorator should fail for to_type without a registered converter'''
        spec = lancelot.Spec(convert_arg(to_type=ASystemUnderTest))
        spec.__call__(lambda: None).should_raise(KeyError)

lancelot.grouping(ConvertArgBehaviour)

@lancelot.verifiable
def convert_result_behaviour():
    ''' convert_result() should decorate a method so that its return value
    is converted to a string using the supplied converter. If no converter
    is specified  then a TypeError should be raised'''
    converter = FromConstructorConverter(int)
    decorated_fn = convert_result(using=converter)(ASystemUnderTest.add)
    sut = ASystemUnderTest()
    spec = lancelot.Spec(decorated_fn)
    spec.__call__(sut, 1, 3).should_be('4')
    spec.__call__(sut, 21, 1).should_be('22')

    spec = lancelot.Spec(convert_result)
    spec.__call__(using=None).should_raise(TypeError)
    
@lancelot.verifiable
def tabletable_constant_values():
    ''' Check TableTable constants for fitnesse cell-by-cell results '''
    spec = lancelot.Spec(TableTableConstants)
    spec.cell_no_change().should_be('')
    spec.cell_correct().should_be('pass')
    spec.cell_incorrect(23).should_be('23')
    spec.cell_incorrect(None).should_be('None')
    spec.cell_error('Erk').should_be('error:Erk')
    spec.cell_error(-1).should_be('error:-1')
    
if __name__ == '__main__':
    lancelot.verify()
