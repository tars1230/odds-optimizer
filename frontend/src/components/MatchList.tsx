import type { Match } from '../lib/api';

interface MatchListProps {
  matches: Match[];
  loading: boolean;
}

export function MatchList({ matches, loading }: MatchListProps) {
  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-gray-200 rounded-lg" />
        ))}
      </div>
    );
  }

  if (matches.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        暂无比赛数据，请点击刷新
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {matches.map((match) => (
        <div
          key={match.id}
          className="bg-white rounded-lg shadow p-4 border border-gray-100"
        >
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
              {match.league}
            </span>
            <span className="text-xs text-gray-400">
              {new Date(match.match_time).toLocaleString('zh-CN')}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <div className="font-medium">{match.home_team}</div>
            <div className="text-gray-400 text-sm">vs</div>
            <div className="font-medium">{match.away_team}</div>
          </div>
          <div className="flex gap-2 mt-3">
            {Object.entries(match.odds).map(([key, value]) => (
              <div
                key={key}
                className="flex-1 text-center bg-blue-50 rounded py-1"
              >
                <div className="text-xs text-gray-500">
                  {key === 'home' ? '主胜' : key === 'draw' ? '平' : '客胜'}
                </div>
                <div className="font-mono font-bold text-blue-600">
                  {value.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
