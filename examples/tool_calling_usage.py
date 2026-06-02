"""Tool calling and structured output example for langchain-iointelligence.

Run with IO_API_KEY / IO_API_URL set in your environment or .env file.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from langchain_iointelligence import IOIntelligenceChatModel

load_dotenv()

MODEL = "meta-llama/Llama-3.3-70B-Instruct"


@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    # Pretend backend lookup.
    return f"It's 22C and sunny in {location}."


def tool_calling_demo():
    print("🛠️  Tool calling")
    print("=" * 50)
    chat = IOIntelligenceChatModel(model=MODEL)
    llm_with_tools = chat.bind_tools([get_weather])

    messages = [HumanMessage(content="What's the weather in Tokyo?")]
    ai_msg = llm_with_tools.invoke(messages)
    print("tool_calls:", ai_msg.tool_calls)

    # Execute the requested tool(s) and feed results back for a final answer.
    messages.append(ai_msg)
    for call in ai_msg.tool_calls:
        result = get_weather.invoke(call["args"])
        messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

    final = llm_with_tools.invoke(messages)
    print("final answer:", final.content)


class Person(BaseModel):
    """A person extracted from text."""

    name: str = Field(..., description="Full name")
    age: int = Field(..., description="Age in years")


def structured_output_demo():
    print("\n🧱 Structured output")
    print("=" * 50)
    chat = IOIntelligenceChatModel(model=MODEL)
    structured = chat.with_structured_output(Person)  # method="function_calling"

    person = structured.invoke("Jane Doe is 32 years old and lives in Osaka.")
    print("parsed:", person)

    # Alternative methods:
    #   chat.with_structured_output(Person, method="json_schema")
    #   chat.with_structured_output(Person, method="json_mode")
    #   chat.with_structured_output(Person, include_raw=True)


def main():
    try:
        tool_calling_demo()
        structured_output_demo()
    except Exception as e:  # noqa: BLE001
        print(f"❌ Error: {e}")
        print("Make sure IO_API_KEY and IO_API_URL are set in your .env file")


if __name__ == "__main__":
    main()
