export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST(request: Request) {
  const apiBaseUrl = process.env.AEO_API_INTERNAL_URL ?? "http://127.0.0.1:8100";
  const idempotencyKey = request.headers.get("Idempotency-Key") ?? crypto.randomUUID();
  try {
    const response = await fetch(new URL("/v1/opportunities/recompute", apiBaseUrl), {
      method: "POST",
      headers: { "Idempotency-Key": idempotencyKey },
      cache: "no-store",
      signal: AbortSignal.timeout(10_000),
    });
    return Response.json(await response.json(), { status: response.status });
  } catch {
    return Response.json({ detail: "AEO API is unavailable." }, { status: 503 });
  }
}
