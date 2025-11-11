import sys
import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from decouple import config
from database.video_table import VideoTableService
load_dotenv()
# ------------------------------------------------------------
# Initialize MCP Server and env variables
# ------------------------------------------------------------
mcp_host = str(config("MCP_HOST"))
mcp_port = int(config("MCP_PORT"))

mcp = FastMCP(
    "VideoMetadata",
    host=mcp_host,
    port=mcp_port
)


# ------------------------------------------------------------
# Tool: Update video metadata
# ------------------------------------------------------------
@mcp.tool()
def update_video_metadata(video_name: str, category: str, suitability: str) -> str:
    print(f"MCP Tool Data {video_name}, {category}, {suitability}")

    service = VideoTableService()
    success = service.update_video(video_name, category, suitability)

    if success:
        msg = f"Updated metadata for {video_name}"
    else:
        msg = f"Update failed or video not found for {video_name}"
    print(msg)
    return msg


# ------------------------------------------------------------
# Run MCP server
# ------------------------------------------------------------
if __name__ == "__main__":
    print("Starting VideoMetadata MCP Server...")
    mcp.run(transport="streamable-http")
