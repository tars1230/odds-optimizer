import type { Match } from '../lib/api';

interface MatchListProps {
  matches: Match[];
  loading: boolean;
}

export function MatchList({ matches, loading }: MatchListProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="glass-strong rounded-2xl p-5 animate-shimmer">
            <div className="h-20" />
          </div>
        ))}
      </div>
    );
  }

  if (matches.length === 0) {
    return (
      <div className="glass-strong rounded-2xl p-12 text-center">
        <div className="text-4xl mb-3">⚽</div>
        <p className="text-[var(--text-secondary)]">暂无比赛数据</p>
        <p className="text-xs text-[var(--text-secondary)] mt-1">点击右上角刷新获取最新赔率</p>
      </div>
    );
  }

  // Group by date
  const grouped = matches.reduce((acc, m) => {
    const date = m.match_time.slice(0, 10);
    if (!acc[date]) acc[date] = [];
    acc[date].push(m);
    return acc;
  }, {} as Record<string, Match[]>);

  return (
    <div className="space-y-6 stagger">
      {Object.entries(grouped).map(([date, dateMatches]) => (
        <div key={date}>
          <div className="flex items-center gap-3 mb-3">
            <div className="h-px flex-1 bg-white/5" />
            <span className="text-xs font-medium text-[var(--text-secondary)] tracking-wider">
              {formatDate(date)}
            </span>
            <div className="h-px flex-1 bg-white/5" />
          </div>
          <div className="space-y-2">
            {dateMatches.map((match) => (
              <MatchRow key={match.id} match={match} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function MatchRow({ match }: { match: Match }) {
  const time = match.match_time.slice(11, 16);

  return (
    <div className="glass rounded-2xl p-4 sm:p-5 hover:bg-white/[0.04] transition-all duration-300 group cursor-default">
      <div className="flex items-center gap-4">
        {/* Time */}
        <div className="w-14 text-center shrink-0">
          <div className="text-xs text-[var(--text-secondary)] mb-0.5">{match.league}</div>
          <div className="text-sm font-bold tabular-nums">{time}</div>
        </div>

        {/* Teams */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-center gap-3">
            <span className="font-semibold text-right truncate">{match.home_team}</span>
            <span className="text-xs text-[var(--text-secondary)] font-medium px-2 py-0.5 rounded-md bg-white/5 shrink-0">VS</span>
            <span className="font-semibold text-left truncate">{match.away_team}</span>
          </div>
        </div>

        {/* Odds */}
        <div className="flex gap-1.5 shrink-0">
          {Object.entries(match.odds).map(([key, value]) => (
            <div
              key={key}
              className="w-14 sm:w-16 text-center py-2 rounded-xl bg-white/[0.03] border border-white/5 group-hover:border-indigo-500/20 transition-colors"
            >
              <div className="text-[10px] text-[var(--text-secondary)] mb-0.5">
                {key === 'home' ? '主' : key === 'draw' ? '平' : '客'}
              </div>
              <div className="text-xs sm:text-sm font-bold text-indigo-400 tabular-nums">
                {value.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00');
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  const month = d.getMonth() + 1;
  const day = d.getDate();
  return `${days[d.getDay()]} ${month}/${day}`;
}
