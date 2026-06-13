import type { Master } from '../lib/api';

interface MasterCardProps {
  master: Master;
  onClick: () => void;
}

export function MasterCard({ master, onClick }: MasterCardProps) {
  return (
    <div className="master-card" onClick={onClick}>
      <div className="master-card-content">
        {/* 头像 */}
        <div className="text-6xl mb-4 text-center">{master.emoji}</div>

        {/* 名字和头衔 */}
        <h3 className="text-xl font-bold text-center mb-1">{master.name}</h3>
        <p className="text-sm text-[var(--text-secondary)] text-center mb-3">
          {master.title}
        </p>

        {/* 哲学 */}
        <p className="text-xs text-[var(--text-secondary)] text-center mb-4 leading-relaxed">
          {master.philosophy}
        </p>

        {/* 风险等级 */}
        <div className="flex items-center justify-center gap-2">
          <span className="text-xs text-[var(--text-secondary)]">风险</span>
          <span className="risk-stars">
            {'⭐'.repeat(master.risk_level)}
          </span>
        </div>

        {/* 随机语录（悬停显示） */}
        <div className="mt-4 pt-4 border-t border-[var(--border)] opacity-0 group-hover:opacity-100 transition-opacity">
          <p className="text-xs italic text-[var(--text-secondary)] text-center">
            "{master.quotes[0]}"
          </p>
        </div>
      </div>
    </div>
  );
}
