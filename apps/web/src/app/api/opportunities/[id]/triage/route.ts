export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST(request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  const apiBaseUrl = process.env.AEO_API_INTERNAL_URL ?? "http://127.0.0.1:8100";
  const idempotencyKey = request.headers.get("Idempotency-Key") ?? crypto.randomUUID();
  try {
    const body = await request.json();
    const response = await fetch(
      new URL(`/v1/opportunities/${encodeURIComponent(id)}/triage`, apiBaseUrl),
      {
        method: "POST",
        headers: { "Content-Type": "application/json", "Idempotency-Key": idempotencyKey },
        body: JSON.stringify(body),
        cache: "no-store",
        signal: AbortSignal.timeout(10_000),
      },
    );
    return Response.json(await response.json(), { status: response.status });
  } catch {
    return Response.json({ detail: "AEO API is unavailable." }, { status: 503 });
  }
}
