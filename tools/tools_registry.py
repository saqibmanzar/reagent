from tools.tools_schema import ToolSchema
from tools.calculator import calculator_tool

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

   )
}