#!/usr/bin/env python3
"""
VibeCraft MCP Server - HTTP/SSE Wrapper
Adds HTTP/SSE transport to the original server keeping all tools intact
"""

import asyncio
import sys
import argparse
import logging
from pathlib import Path

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the original server app and module
from vibecraft import server as vibecraft_server
from vibecraft.server import app
from vibecraft.config import load_config
from vibecraft.rcon_manager import RCONManager

# Try to import SSE transport
try:
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import Response
    import uvicorn
    SSE_AVAILABLE = True
except ImportError:
    SSE_AVAILABLE = False
    print("❌ SSE transport not available!")
    print("\nInstall required packages:")
    print("  pip install sse-starlette starlette uvicorn")
    sys.exit(1)


async def run_http_server(host: str = "127.0.0.1", port: int = 8765):
    """Run the original VibeCraft server with HTTP/SSE transport"""

    print("\n" + "="*60)
    print("🎮 VibeCraft MCP Server - HTTP/SSE Mode")
    print("   All 45 tools available")
    print("="*60)

    # Load configuration
    config = load_config()
    config.enable_command_logging = True

    # Initialize RCON
    rcon = RCONManager(config)

    # Set the globals in the vibecraft.server module so call_tool can access them
    vibecraft_server.config = config
    vibecraft_server.rcon = rcon

    # Test connection
    print(f"\n📡 RCON Host: {config.rcon_host}:{config.rcon_port}")
    print("Testing RCON connection...")

    try:
        result = rcon.execute_command("list")
        print(f"✅ RCON connected: {result}")
    except Exception as e:
        print(f"❌ RCON connection failed: {e}")
        print("\nMake sure:")
        print("  1. Minecraft server is running")
        print("  2. RCON is enabled in server.properties")
        print("  3. RCON password matches")
        sys.exit(1)

    # Check WorldEdit
    try:
        result = rcon.execute_command("version WorldEdit")
        if "WorldEdit" in result:
            import re
            match = re.search(r"(\d+\.\d+\.\d+)", result)
            if match:
                print(f"✅ WorldEdit {match.group(1)} detected")
    except:
        print("⚠️  WorldEdit not detected")

    # Wrap the list_tools handler to log what it returns
    logger.info("="*60)
    logger.info("WRAPPING list_tools TO LOG RESPONSE")
    logger.info("="*60)

    # Get the original list_tools handler
    import inspect

    # Find the original list_tools function
    original_list_tools = None
    for name, obj in inspect.getmembers(vibecraft_server):
        if name == 'list_tools' and inspect.iscoroutinefunction(obj):
            original_list_tools = obj
            break

    if original_list_tools:
        logger.info(f"✅ Found original list_tools function")

        # Create a wrapper that logs the result
        async def logged_list_tools():
            tools = await original_list_tools()
            logger.info("="*60)
            logger.info(f"🔧 list_tools() returned {len(tools)} tools:")
            for i, tool in enumerate(tools, 1):
                logger.info(f"  {i}. {tool.name}")
            logger.info("="*60)
            return tools

        # Test calling the function directly
        try:
            test_tools = await original_list_tools()
            logger.info(f"✅ Direct call to list_tools() returned {len(test_tools)} tools")
            logger.info(f"📋 Tool names:")
            for i, tool in enumerate(test_tools, 1):
                logger.info(f"  {i}. {tool.name}")
        except Exception as e:
            logger.error(f"❌ Error calling list_tools directly: {e}")
    else:
        logger.warning("❌ Could not find original list_tools function")

    logger.info("="*60)

    print("\n" + "="*60)
    print("🚀 HTTP/SSE Server Ready!")
    print("="*60)
    print(f"\n📡 Server URL: http://{host}:{port}/sse")
    print("\nAdd to Claude Code:")
    print(f"  claude mcp add --transport sse vibecraft-shared http://{host}:{port}/sse")
    print("\n👀 You'll see all MCP communication here!")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")

    # Create SSE transport
    sse = SseServerTransport("/messages")

    async def handle_sse(request):
        """Handle SSE connections"""
        logger.info("="*60)
        logger.info(f"📡 SSE connection established from {request.client}")
        logger.info("="*60)

        # Log before running app
        if hasattr(app, '_tool_handlers'):
            logger.info(f"🔧 App has {len(app._tool_handlers)} tool handlers registered")

        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send
        ) as streams:
            logger.info("🚀 Running app.run() with streams...")
            await app.run(
                streams[0], streams[1],
                app.create_initialization_options()
            )
            logger.info("✅ app.run() completed")

    async def handle_messages(request):
        """Handle message endpoint"""
        logger.info("📨 Handling POST message request")

        # Get the body to log it
        body = await request.body()
        logger.debug(f"Request body: {body[:500]}...")  # First 500 chars

        # We need to create a new receive that returns the body we just read
        async def new_receive():
            return {"type": "http.request", "body": body}

        # handle_post_message sends its own response via request._send
        await sse.handle_post_message(request.scope, new_receive, request._send)

        # Return 202 Accepted to indicate message was received
        return Response(status_code=202)

    async def handle_root(request):
        """Root endpoint for discovery"""
        from starlette.responses import JSONResponse
        return JSONResponse({
            "name": "vibecraft",
            "version": "1.0.0",
            "transport": "sse"
        })

    # Create Starlette app
    starlette_app = Starlette(
        routes=[
            Route("/", handle_root, methods=["GET"]),
            Route("/sse", handle_sse, methods=["GET"]),
            Route("/messages", handle_messages, methods=["POST"]),
        ]
    )

    # Run server
    config = uvicorn.Config(
        starlette_app,
        host=host,
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VibeCraft HTTP/SSE Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8765, help="Port to run on")
    args = parser.parse_args()

    try:
        asyncio.run(run_http_server(args.host, args.port))
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)