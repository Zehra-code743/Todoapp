"""
MCP Server initialization for Phase III AI Chatbot

Initializes the Model Context Protocol server and registers all MCP tools.
Tools will be registered here as they are implemented in the tools/ directory.
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from config.logging import logger
from mcp_tools.tools.add_task import add_task, ADD_TASK_SCHEMA


# Initialize MCP server
mcp_server = Server("todo-mcp-server")


async def initialize_mcp_server():
    """
    Initialize MCP server and register all tools.

    Tools registered:
    - add_task (US1) ✓

    Tools to be registered:
    - list_tasks (US2)
    - complete_task (US3)
    - update_task (US4)
    - delete_task (US5)
    """
    logger.info("mcp_server_initializing", server_name="todo-mcp-server")

    # Register add_task tool
    @mcp_server.tool(schema=ADD_TASK_SCHEMA)
    async def add_task_handler(**kwargs):
        """Handler for add_task MCP tool"""
        return await add_task(**kwargs)

    logger.info("mcp_server_initialized",
                server_name="todo-mcp-server",
                tools_registered=1,
                tools=["add_task"])

    return mcp_server


async def run_mcp_server():
    """
    Run MCP server using stdio transport.

    This is called when running the MCP server as a standalone process
    for development/testing.
    """
    logger.info("mcp_server_starting", transport="stdio")

    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_mcp_server())
