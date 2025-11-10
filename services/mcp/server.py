import sys
import os
from mcp.server.fastmcp import FastMCP

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database.video_table import VideoTableService

# ------------------------------------------------------------
# Initialize MCP Server
# ------------------------------------------------------------
mcp = FastMCP("VideoMetadata")


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
