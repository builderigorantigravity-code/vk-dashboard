import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const queuePath = path.join(process.cwd(), 'news_queue.json');
    if (fs.existsSync(queuePath)) {
      const data = fs.readFileSync(queuePath, 'utf8');
      return NextResponse.json(JSON.parse(data).slice(0, 10));
    }
    return NextResponse.json([]);
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
