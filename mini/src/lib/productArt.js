const PALETTES = [
  ['#fff7ed', '#fed7aa', '#fb923c'],
  ['#fef2f2', '#fecaca', '#f87171'],
  ['#f0fdf4', '#bbf7d0', '#4ade80'],
  ['#eff6ff', '#bfdbfe', '#60a5fa'],
  ['#fdf4ff', '#f5d0fe', '#e879f9'],
]

const ICONS = {
  草莓: '🍓',
  鸡蛋: '🥚',
  豆浆: '🥛',
  青菜: '🥬',
  蔬菜: '🥬',
  牛奶: '🥛',
  面包: '🍞',
  米: '🍚',
  肉: '🥩',
  鱼: '🐟',
  果: '🍎',
}

export function productEmoji(name = '') {
  for (const [key, icon] of Object.entries(ICONS)) {
    if (name.includes(key)) return icon
  }
  return '🛒'
}

export function productGradient(id = 1) {
  const p = PALETTES[(id - 1) % PALETTES.length]
  return `linear-gradient(145deg, ${p[0]} 0%, ${p[1]} 55%, ${p[2]} 100%)`
}
