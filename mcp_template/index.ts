#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk";
import { StdioServerTransport } from "@modelcontextprotocol/sdk";
import type {
  CallToolRequest,
  ListToolsRequest,
  Tool,
} from "@modelcontextprotocol/sdk";
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";

// Define types for our server
type ToolInput = z.ZodObject<any>;

// Example tool schema
const ExampleToolSchema = z.object({
  input: z.string(),
});

// Server setup
const server = new Server(
  {
    name: "mcp-server-template",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  },
);

// Tool handlers
server.setRequestHandler<ListToolsRequest>("list_tools", async () => {
  return {
    tools: [
      {
        name: "example_tool",
        description: "An example tool demonstrating the basic structure.",
        inputSchema: zodToJsonSchema(ExampleToolSchema),
      },
    ],
  };
});

server.setRequestHandler<CallToolRequest>("call_tool", async (request) => {
  try {
    const { name, arguments: args } = request.params;

    switch (name) {
      case "example_tool": {
        const parsed = ExampleToolSchema.safeParse(args);
        if (!parsed.success) {
          throw new Error(`Invalid arguments: ${parsed.error}`);
        }
        return {
          content: [{ type: "text", text: `Received input: ${parsed.data.input}` }],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [{ type: "text", text: `Error: ${errorMessage}` }],
      isError: true,
    };
  }
});

// Start server
async function runServer() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP Server Template running on stdio");
}

runServer().catch((error) => {
  console.error("Fatal error running server:", error);
  process.exit(1);
});