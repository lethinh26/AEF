export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  const apiBaseUrl = process.env.AEO_API_INTERNAL_URL ?? "http://127.0.0.1:8100";

  try {
    const response = await fetch(new URL("/health/live", apiBaseUrl), {
      cache: "no-store",
      signal: AbortSignal.timeout(3_000),
    });

    return Response.json(await response.json(), { status: response.status });
  } catch {
    return Response.json({ status: "unavailable" }, { status: 503 });
  }
}
