import { NextResponse } from "next/server";
import { PREDEFINED_SCENARIOS } from "@/lib/ml-simulator";

export async function GET() {
  return NextResponse.json(PREDEFINED_SCENARIOS, { status: 200 });
}
