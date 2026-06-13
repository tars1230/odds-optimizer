import { useEffect } from 'react';

/**
 * 根据时间自动切换深/浅色主题
 * 浅色: 08:00 - 18:00
 * 深色: 18:00 - 08:00
 */
export function useAutoTheme() {
  useEffect(() => {
    const updateTheme = () => {
      const hour = new Date().getHours();
      const isLight = hour >= 8 && hour < 18;

      if (isLight) {
        document.documentElement.classList.add('light-theme');
      } else {
        document.documentElement.classList.remove('light-theme');
      }
    };

    // 初始化
    updateTheme();

    // 每分钟检查一次（避免错过切换时间）
    const interval = setInterval(updateTheme, 60000);

    return () => clearInterval(interval);
  }, []);
}

/**
 * 获取当前主题图标
 */
export function getThemeIcon(): string {
  const hour = new Date().getHours();
  if (hour >= 6 && hour < 12) return '🌅'; // 早晨
  if (hour >= 12 && hour < 18) return '☀️'; // 下午
  if (hour >= 18 && hour < 21) return '🌆'; // 傍晚
  return '🌙'; // 夜晚
}
