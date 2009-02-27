'''
BDD-style Lancelot specifications for the behaviour of the core library classes
'''

import lancelot
from lancelot.comparators import Type
from waferslim.protocol import pack, unpack, UnpackingError, instruction_for, \
                               Results, Instructions, RequestResponder
from waferslim.execution import ExecutionContext, InstructionException, \
                                Make, Import, Call, CallAndAssign 

SAMPLE_DATA = [
               ([],                 '[000000:]'),
               (['hello'],          '[000001:000005:hello:]'),
               (['hello','world'],  '[000002:000005:hello:000005:world:]'),
               ([['element']],      '[000001:000024:[000001:000007:element:]:]')
              ]

class PackBehaviour(object):
    ''' Group of specs for pack() behaviour '''
    
    @lancelot.verifiable
    def items_length_item_format(self):
        ''' Encoding as described in fitnesse.slim.ListSerializer Javadoc:
        Format:  [iiiiii:llllll:item...]
        All lists (including lists within lists) begin with [ and end with ].  
        After the [ is the 6 digit number of items in the list followed by a :.
        Then comes each item which is composed of a 6 digit length a : and 
        then the value of the item followed by a :. '''
        spec = lancelot.Spec(pack)
        for unpacked, packed in SAMPLE_DATA:
            spec.pack(unpacked).should_be(packed)
            
    @lancelot.verifiable
    def pack_non_strings(self):
        ''' Use str() co-ercion for encoding non-string values, except for
        None which encodes as "null" ''' 
        spec = lancelot.Spec(pack)
        spec.pack([1]).should_be('[000001:000001:1:]')
        spec.pack([None]).should_be('[000001:000004:null:]') #TODO: check this?!

class UnpackBehaviour(object):
    ''' Group of specs for unpack() behaviour '''
    
    @lancelot.verifiable
    def unpack_strings_only(self):
        ''' Unpacking a non-string should raise an error ''' 
        spec = lancelot.Spec(unpack)
        spec.unpack(None).should_raise(TypeError('None is not a string'))
        spec.unpack(1).should_raise(TypeError('1 is not a string'))
        spec.unpack([]).should_raise(TypeError('[] is not a string'))
        
    @lancelot.verifiable
    def require_square_brackets(self):
        ''' Unpacking a string without a leading square bracket, 
        or a string without an ending square bracket should raise an error ''' 
        spec = lancelot.Spec(unpack)
        spec.unpack('').should_raise(
            UnpackingError("'' has no leading '['"))
        spec.unpack('[hello').should_raise(
            UnpackingError("'[hello' has no trailing ']'"))
        spec.unpack('hello]').should_raise(
            UnpackingError("'hello]' has no leading '['"))
        
    @lancelot.verifiable
    def items_length_item_format(self):
        ''' Unpacking should reverse the encoding process '''
        spec = lancelot.Spec(unpack)
        for unpacked, packed in SAMPLE_DATA:
            spec.unpack(packed).should_be(unpacked)

@lancelot.verifiable
def request_responder_behaviour():
    ''' RequestResponder should send an ACK then recv a message 
    header and message contents: then EITHER send a response and loop back 
    to recv; OR if the message content is a "bye" then terminate '''
    request = lancelot.MockSpec(name='request')
    instructions = lancelot.MockSpec(name='instructions')
    spec = lancelot.Spec(RequestResponder())
    spec.respond_to(request, instructions=lambda data: instructions)
    spec.should_collaborate_with(
        request.send('Slim -- V0.0\n'.encode('utf-8')).will_return(2),
        request.recv(7).will_return('000009:'.encode('utf-8')),
        request.recv(9).will_return('[000000:]'.encode('utf-8')),
        instructions.execute(Type(ExecutionContext), Type(Results())),
        request.send('000009:[000000:]'.encode('utf-8')).will_return(4),
        request.recv(7).will_return('000003:'.encode('utf-8')),
        request.recv(3).will_return('bye'.encode('utf-8')),
        and_result=(7+9+7+3, 2+4))
    
    request = lancelot.MockSpec(name='request')
    instructions = lancelot.MockSpec(name='instructions')
    spec = lancelot.Spec(RequestResponder())
    spec.respond_to(request, instructions=lambda data: instructions)
    spec.should_collaborate_with(
        request.send('Slim -- V0.0\n'.encode('utf-8')).will_return(2),
        request.recv(7).will_return('000009:'.encode('utf-8')),
        request.recv(9).will_return('[000000:]'.encode('utf-8')),
        instructions.execute(Type(ExecutionContext), Type(Results())),
        request.send('000009:[000000:]'.encode('utf-8')).will_return(4),
        request.recv(7).will_return('000009:'.encode('utf-8')),
        request.recv(9).will_return('[000000:]'.encode('utf-8')),
        instructions.execute(Type(ExecutionContext), Type(Results())),
        request.send('000009:[000000:]'.encode('utf-8')).will_return(8),
        request.recv(7).will_return('000003:'.encode('utf-8')),
        request.recv(3).will_return('bye'.encode('utf-8')),
        and_result=(7+9+7+9+7+3, 2+4+8))
    
@lancelot.verifiable
def instruction_for_behaviour():
    ''' instruction_for should return instantiate the correct type of 
    instruction, based on the name given in the list passed to it ''' 
    spec = lancelot.Spec(instruction_for)
    known_instructions = {'make':Type(Make),
                          'import':Type(Import),
                          'call':Type(Call),
                          'callAndAssign':Type(CallAndAssign)}
    for name, instruction in known_instructions.items():
        spec.instruction_for(['id', name, []]).should_be(instruction)

@lancelot.verifiable
def instructions_behaviour():
    ''' Instructions should collaborate with instruction_for to instantiate
    a list of instructions, which execute() loops through '''
    mock_fn = lancelot.MockSpec(name='mock_fn')
    mock_make = lancelot.MockSpec(name='mock_make')
    mock_call = lancelot.MockSpec(name='mock_call')
    a_list = [
              ['id_0', 'make', 'instance', 'fixture', 'argument'],
              ['id_1', 'call', 'instance', 'f', '3']
             ]
    instructions = Instructions(a_list, 
                                lambda item: mock_fn.instruction_for(item))
    spec = lancelot.Spec(instructions)
    ctx = ExecutionContext()
    results = Results() 
    spec.execute(ctx, results).should_collaborate_with(
            mock_fn.instruction_for(a_list[0]).will_return(mock_make),
            mock_make.execute(ctx, results),
            mock_fn.instruction_for(a_list[1]).will_return(mock_call),
            mock_call.execute(ctx, results)
        )

class ResultsBehaviour(object):
    ''' Group of related specs for Results behaviour '''
    
    @lancelot.verifiable
    def completed_ok(self):
        ''' completed_ok() should add to results list. 
        Results list should be accessible through collection() '''
        instruction = lancelot.MockSpec(name='instruction')
        spec = lancelot.Spec(Results())
        spec.completed(instruction).should_collaborate_with(
            instruction.instruction_id().will_return('a')
            )
        spec.collection().should_be([['a', 'OK']])

    @lancelot.verifiable
    def raised(self):
        ''' raised() should add a translated error message to results list. 
        Results list should be accessible through collection() '''
        translated_msg = '__EXCEPTION__: ' \
            + 'message:<<MALFORMED_INSTRUCTION bucket>>'
        instruction = lancelot.MockSpec(name='instruction')
        spec = lancelot.Spec(Results())
        spec.raised(instruction, InstructionException('bucket'))
        spec.should_collaborate_with(
            instruction.instruction_id().will_return('b')
            )
        spec.collection().should_be([['b', translated_msg]])
        
    @lancelot.verifiable
    def completed_with_result(self):
        ''' completed() should add to results list. 
        Results list should be accessible through collection() '''
        instruction = lancelot.MockSpec(name='instruction')
        result = lancelot.MockSpec(name='result')
        spec = lancelot.Spec(Results())
        spec.completed(instruction, result=result).should_collaborate_with(
            instruction.instruction_id().will_return('b')
            )
        spec.collection().should_be([['b', str(result)]])
        
    @lancelot.verifiable
    def completed_with_None(self):
        ''' completed() should add to results list. 
        Results list should be accessible through collection() '''
        instruction = lancelot.MockSpec(name='instruction')
        spec = lancelot.Spec(Results())
        spec.completed(instruction, result=None).should_collaborate_with(
            instruction.instruction_id().will_return('c')
            )
        spec.collection().should_be([['c', '/__VOID__/']])

lancelot.grouping(PackBehaviour)
lancelot.grouping(UnpackBehaviour)
lancelot.grouping(ResultsBehaviour)

if __name__ == '__main__':
    lancelot.verify()