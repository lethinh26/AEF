export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST() {
  const apiBaseUrl = process.env.AEO_API_INTERNAL_URL ?? "http://127.0.0.1:8100";
  try {
    const response = await fetch(new URL("/v1/opportunities/recompute", apiBaseUrl), {
      method: "POST",
      cache: "no-store",
      signal: AbortSignal.timeout(10_000),
    });
    return Response.json(await response.json(), { status: response.status });
  } catch {
    return Response.json({ detail: "AEO API is unavailable." }, { status: 503 });
  }
}
