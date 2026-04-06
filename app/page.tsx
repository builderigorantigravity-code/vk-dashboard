'use client';

import React, { useState, useEffect } from 'react';
import { 
  Users, Eye, ThumbsUp, MessageSquare, 
  RefreshCcw, Plus, Brain, TrendingUp 
} from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [news, setNews] = useState([]);

  // Fetch initial data
  useEffect(() => {
    // In a real Vercel app, these would be fetch('/api/stats')
    // For now, we use our local API if the server is running
    refreshData();
  }, []);

  const refreshData = async () => {
    try {
      const sRes = await fetch('/api/vk/stats');
      const sData = await sRes.json();
      setStats(sData);

      const nRes = await fetch('/api/news');
      const nData = await nRes.json();
      setNews(nData);
    } catch (e) {
      console.log('API Error:', e);
    }
  };

  return (
    <main className="container mx-auto p-8 max-w-7xl">
      <header className="flex justify-between items-center mb-12">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-accent-blue to-accent-purple bg-clip-text text-transparent">
            Antigravity Manager
          </h1>
          <p className="text-gray-400 mt-2">Управление вашим VK-сообществом</p>
        </div>
        <div className="flex gap-4">
          <button onClick={refreshData} className="p-3 glass hover:bg-white/10 transition">
            <RefreshCcw className="w-5 h-5" />
          </button>
          <button className="bg-gradient-to-r from-accent-purple to-accent-purpleDark px-6 py-3 rounded-xl font-bold flex items-center gap-2">
            <Plus className="w-5 h-5" /> Создать пост
          </button>
        </div>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <StatCard icon={<Users/>} label="Подписчики" value={stats?.group_info?.members_count || '-'} />
        <StatCard icon={<Eye/>} label="Просмотры" value={stats?.posts?.reduce((a,b)=>a+b.views,0) || '-'} color="text-blue-400" />
        <StatCard icon={<ThumbsUp/>} label="Лайки" value={stats?.posts?.reduce((a,b)=>a+b.likes,0) || '-'} color="text-pink-500" />
        <StatCard icon={<MessageSquare/>} label="Комменты" value={stats?.posts?.reduce((a,b)=>a+b.comments,0) || '-'} color="text-green-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Posts Table */}
        <div className="lg:col-span-2 glass p-8">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <TrendingUp className="text-accent-purple" /> Последние публикации
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/5 text-gray-500 uppercase text-xs">
                  <th className="pb-4">Контент</th>
                  <th className="pb-4">Лайки</th>
                  <th className="pb-4">Охват</th>
                </tr>
              </thead>
              <tbody>
                {stats?.posts?.map((post) => (
                  <tr key={post.id} className="border-b border-white/5 last:border-0">
                    <td className="py-4 pr-4">
                      <p className="text-sm line-clamp-2">{post.text}</p>
                    </td>
                    <td className="py-4">❤️ {post.likes}</td>
                    <td className="py-4">👁️ {post.views}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* News Column */}
        <div className="glass p-8">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Brain className="text-accent-blue" /> Идеи от ИИ
          </h2>
          <div className="space-y-6">
            {news.slice(0, 4).map((item, idx) => (
              <div key={idx} className="p-4 bg-white/5 rounded-xl border border-white/5 hover:border-accent-blue/30 transition cursor-pointer">
                <h3 className="font-bold text-sm mb-2">{item.title}</h3>
                <div className="flex justify-between items-center text-xs text-gray-500">
                  <span>Habr</span>
                  <button className="text-accent-blue font-bold">Сгенерировать &rarr;</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}

function StatCard({ icon, label, value, color }) {
  return (
    <div className="glass p-6">
      <div className={`p-3 rounded-lg bg-white/5 w-fit mb-4 ${color}`}>
        {React.cloneElement(icon, { className: 'w-6 h-6' })}
      </div>
      <h3 className="text-gray-400 text-sm">{label}</h3>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </div>
  );
}
