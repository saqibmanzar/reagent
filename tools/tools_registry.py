from tools.tools_schema import ToolSchema
from tools.calculator import calculator_tool
from tools.python_executor import execute_python

available_tools = {
   "calculator": ToolSchema(
       name="calculator",
       description="perform arithmetic calculations",
       input_schema={
           "type": "object",
           "properties": {
               "expression": {
                   "type": "string"
               }
           },
           "required": ["expression"]
       },
       function_reference=calculator_tool
   ),
   "python_executor": ToolSchema(
       name='python_executor',
       description='Executes arbitrary Python code and returns the output. Always use print() to output your final result. Use this when you need to run calculations, data processing, or any logic that requires code execution.',
       input_schema={
           "type": "object",
           "properties": {
               "code": {
                   "type": "string"
               }
           },
           "required": ["code"]
       },
       function_reference=execute_python
   )
}