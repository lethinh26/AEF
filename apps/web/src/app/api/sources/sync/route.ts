export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST() {
  const apiBaseUrl = process.env.AEO_API_INTERNAL_URL ?? "http://127.0.0.1:8100";

  try {
    const response = await fetch(new URL("/v1/sources/github/sync", apiBaseUrl), {
      method: "POST",
      cache: "no-store",
      signal: AbortSignal.timeout(10_000),
    });
    const body = await response.json();
    return Response.json(body, { status: response.status });
  } catch {
    return Response.json(
      { detail: { code: "api_unavailable", message: "AEO API is unavailable." } },
      { status: 503 },
    );
  }
}
