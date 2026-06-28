/**
 * Codegen runner for the UI's OpenAPI types.
 *
 * Workflow:
 *   1. Start the FastAPI server:    uv run courtside-data serve
 *   2. Run this script:             npx tsx ui/scripts/generate-api-types.ts
 *
 * Run via `npx tsx` (the project doesn't pin `"type": "module"`).
 */
import { execSync } from "node:child_process";

const SERVER_URL = "http://127.0.0.1:8765";
const OUTPUT = "src/lib/openapi-types.ts";

console.log(`Ensure courtside-data server is running on ${SERVER_URL} (uv run courtside-data serve)`);

try {
  execSync(`npx --yes openapi-typescript ${SERVER_URL}/openapi.json -o ${OUTPUT}`, { stdio: "inherit" });
  console.log(`Wrote ${OUTPUT} from ${SERVER_URL}/openapi.json`);
  process.exit(0);
} catch (error) {
  console.error(`openapi-typescript failed: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
}
