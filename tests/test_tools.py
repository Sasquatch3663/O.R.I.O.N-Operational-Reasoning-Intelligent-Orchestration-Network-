from orion.tools import (
    BaseTool,
    ToolContext,
    ToolError,
    ToolRegistry,
)


class MockTool(BaseTool):

    def __init__(self):
        super().__init__(
            name="mock",
            description="Mock tool for testing.",
        )

    def execute(
        self,
        parameters,
        context,
    ):
        return {
            "success": True,
            "parameters": parameters,
            "source": context.source,
        }


def test_tool_creation():
    tool = MockTool()

    assert tool.name == "mock"
    assert tool.description == (
        "Mock tool for testing."
    )


def test_tool_metadata():
    tool = MockTool()

    metadata = tool.metadata()

    assert metadata["name"] == "mock"
    assert metadata["description"] == (
        "Mock tool for testing."
    )


def test_tool_execution():
    tool = MockTool()

    context = ToolContext(
        source="test"
    )

    result = tool.execute(
        {"value": 10},
        context,
    )

    assert result["success"] is True
    assert result["parameters"]["value"] == 10
    assert result["source"] == "test"


def test_tool_registry():
    registry = ToolRegistry()
    tool = MockTool()

    registry.register(tool)

    assert registry.count() == 1
    assert registry.has("mock")
    assert registry.get("mock") is tool
    assert "mock" in registry.names()


def test_tool_duplicate_registration():
    registry = ToolRegistry()
    tool = MockTool()

    registry.register(tool)

    try:
        registry.register(tool)
        assert False
    except ToolError:
        assert True


def test_tool_unregister():
    registry = ToolRegistry()
    tool = MockTool()

    registry.register(tool)
    registry.unregister("mock")

    assert registry.count() == 0
    assert not registry.has("mock")