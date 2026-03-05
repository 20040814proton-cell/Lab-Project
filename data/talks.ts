export interface Talk {
  date: string
  title: string
  description?: string
  series?: string
  lang?: string
  presentations: Presentation[]
}

export interface Presentation {
  date: string
  location: string
  conference: string
  conferenceUrl?: string
  recording?: string
  pdf?: string
  spa?: string
  transcript?: string
  lang?: string
}

export const talks: Talk[] = [
  {
    title: '每周学术分享会',
    date: '2025-01-05',
    description: '本周由张三分享最新的 CVPR 论文。',
    lang: 'zh',
    presentations: [
      {
        date: '2025-01-05',
        location: 'Laboratory Meeting Room',
        conference: 'Weekly Seminar',
        lang: 'zh',
      },
    ],
  },
]
