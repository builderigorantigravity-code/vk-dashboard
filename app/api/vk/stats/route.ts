import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // В реальном Vercel токены лучше хранить в Environment Variables
    // Но мы для начала считаем их из ваших файлов
    const tokenPath = path.join(process.cwd(), '.openclaw', 'Keys', 'vk_group_token.txt');
    const token = fs.readFileSync(tokenPath, 'utf8').trim().replace('VK_TOKEN=', '');
    const groupId = 236370925;

    const res = await fetch(`https://api.vk.com/method/groups.getById?group_id=${groupId}&fields=members_count,status&access_token=${token}&v=5.131`);
    const data = await res.json();

    const wallRes = await fetch(`https://api.vk.com/method/wall.get?owner_id=-${groupId}&count=10&access_token=${token}&v=5.131`);
    const wallData = await wallRes.json();

    const stats = {
      group_info: {
        name: data.response[0].name,
        members_count: data.response[0].members_count,
      },
      posts: wallData.response.items.map(item => ({
        id: item.id,
        text: item.text,
        likes: item.likes.count,
        views: item.views?.count || 0,
        comments: item.comments.count,
      }))
    };

    return NextResponse.json(stats);
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
