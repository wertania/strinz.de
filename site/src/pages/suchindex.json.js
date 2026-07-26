import { searchIndex } from "../lib/chronik.js";

export function GET() {
  return new Response(JSON.stringify(searchIndex()), {
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}
