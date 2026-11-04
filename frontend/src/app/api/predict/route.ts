import { NextRequest, NextResponse } from "next/server";
import { spawn } from "node:child_process";
import path from "node:path";

function runPythonInference(payload: Record<string, unknown>): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.resolve(process.cwd(), "..", "ml", "predict_service.py");
    const py = spawn("python", [scriptPath]);

    let stdoutData = "";
    let stderrData = "";

    py.stdout.on("data", (data) => {
      stdoutData += data.toString();
    });

    py.stderr.on("data", (data) => {
      stderrData += data.toString();
    });

    py.on("close", (code) => {
      if (code !== 0) {
        return reject(new Error(`Python exit code ${code}: ${stderrData}`));
      }
      try {
        const json = JSON.parse(stdoutData.trim());
        resolve(json);
      } catch (err) {
        reject(new Error(`Failed to parse python output: ${stdoutData}`));
      }
    });

    py.on("error", (err) => {
      reject(err);
    });

    py.stdin.write(JSON.stringify(payload));
    py.stdin.end();
  });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    const timestamp = body.Timestamp || new Date().toISOString();
    const fromBank = body.From_Bank || "010";
    const fromAccount = String(body.From_Account || "").trim();
    const toBank = body.To_Bank || "010";
    const toAccount = String(body.To_Account || "").trim();
    const amountReceived = Number(body.Amount_Received ?? 0);
    const currency = body.Receiving_Currency || "US Dollar";
    const paymentFormat = body.Payment_Format || "Cheque";

    if (!fromAccount || !toAccount || isNaN(amountReceived)) {
      return NextResponse.json(
        { 
          error: "From_Account, To_Account, and numeric Amount_Received are required." 
        },
        { status: 400 }
      );
    }

    const payload = {
      Timestamp: timestamp,
      From_Bank: fromBank,
      From_Account: fromAccount,
      To_Bank: toBank,
      To_Account: toAccount,
      Amount_Received: amountReceived,
      Receiving_Currency: currency,
      Payment_Format: paymentFormat
    };

    // Run 100% Real Python ML Inference Service via stdin
    const mlResult = await runPythonInference(payload);
    return NextResponse.json(mlResult, { status: 200 });

  } catch (error) {
    const message = error instanceof Error ? error.message : "Inference pipeline failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
