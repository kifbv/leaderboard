import { NextResponse } from "next/server";

/**
 * Returns the configured ADMIN_SECRET, or null if not set.
 */
export function getAdminSecret(): string | null {
  return process.env.ADMIN_SECRET ?? null;
}

/**
 * Validates that the given secret matches ADMIN_SECRET.
 * Returns a 404 NextResponse if invalid/unset, or null if valid.
 * Admin routes return 404 (not 403) to avoid revealing that the path exists.
 */
export function validateAdminSecret(secret: string): NextResponse | null {
  const adminSecret = getAdminSecret();
  if (!adminSecret || secret !== adminSecret) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
  return null;
}
