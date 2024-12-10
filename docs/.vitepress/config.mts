import { createRequire } from 'module'
import { defineConfig, type DefaultTheme } from 'vitepress'

const require = createRequire(import.meta.url)
// const pypitoml = require('../../pyproject.toml')

const pkg = require('vitepress/package.json')

const version = "v0.0.1.6-pw.2"

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "F2",
  description: "Fast 2 Every",
  base: "/f2/",
  lastUpdated: true,

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/f2/f2-logo-with-shadow-svg@0.25x.svg' }],
    ['link', { rel: 'icon', type: 'image/png', href: '/f2/f2-logo-with-shadow-mini.png' }],
    ['link', { rel: 'icon', type: 'image/x-icon', href: '/f2/f2-logo.ico' }],
    // google analytics
    [
      'script',{ async: "", src: "https://www.googletagmanager.com/gtag/js?id=G-H7N87QED9C",
      },
    ],
    [
      'script',
      {},
      `window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-H7N87QED9C');`,
    ],
  ],
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    logo: { src: '/f2-logo-with-shadow-svg@1.0x.svg', width: 24, height: 24 },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Johnserf-Seed/f2' },
      { icon: 'discord', link: 'https://discord.gg/3PhtPmgHf8' },
    ],
    algolia: {
      appId: 'KKYI8Z7LEP',
      apiKey: '8f27043df972a4e8eb009a3195f2042b',
      indexName: 'f2'
    },
    footer: {
      message: 'Released under the Apache-2.0 license.',
      copyright: 'Copyright © 2023-present Johnserf Seed'
    },
    editLink: {
      pattern: 'https://github.com/Johnserf-Seed/f2/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    }
  },

  locales: {
    root: {
      label: '简体中文',
      lang: 'zh',
      themeConfig: {
        nav: cn_nav(),
        sidebar: {
          '/':[
            {
              text: '快速入门',
              items: [
                {text: '安装', link: '/install'},
                {text: '快速使用', link: '/quick-start'},
                {text: '配置文件', link: '/site-config'},
                {text: '命令行', link: '/cli'},
                {text: '进阶用法', link: '/advance-guide'},
              ]
            },
          ],
          '/guide/': [
            {
              text: '什么是F2',
              items: [
                {text: '开发者必看', link: '/guide/what-is-f2'}
              ]
            },
            {
              text: '开发者指南',
              items: [
                {text: '使用示例', link: '/guide/api-examples'}
              ]
            },
            {
              text: '开发者接口',
              items: [
                {text: 'Bark', link: '/guide/apps/bark/index'},
                {text: 'DouYin', link: '/guide/apps/douyin/index'},
                {text: 'TikTok', link: '/guide/apps/tiktok/index'},
                {text: 'Twitter', link: '/guide/apps/twitter/index'},
                {text: 'WeiBo', link: '/guide/apps/weibo/index'},
              ]
            },
            {
              text: '命令行指引',
              items: [
                {text: 'Bark', link: '/guide/apps/bark/cli'},
                {text: 'DouyYin', link: '/guide/apps/douyin/cli'},
                {text: 'TikTok', link: '/guide/apps/tiktok/cli'},
                {text: 'Twitter', link: '/guide/apps/twitter/cli'},
                {text: 'WeiBo', link: '/guide/apps/weibo/cli'},
              ]
            }

          ],
          '/question-answer/': [
            {
              text: 'QA',
              items: [
                {text: 'Issue里经常反馈的问题', link: '/question-answer/qa'}
              ]
            },
          ]
        }
      }
    },

    en: {
      label: 'English',
      lang: 'en',
      themeConfig: {
        nav: en_nav(),
        sidebar: {
          '/':[
            {
              text: 'Quick Start',
              items: [
                {text: 'Install', link: '/en/install'},
                {text: 'Quick Start', link: '/en/quick-start'},
                {text: 'Advance Guide', link: '/en/advance-guide'},
              ]
            },
          ],
          '/guide/': [
            {
              text: 'Guide',
              items: [
                {text: 'API Examples', link: '/api-examples'}
              ]
            }
          ],
        }
      },
    }
  },
})

function cn_nav(): DefaultTheme.NavItem[] {
  return [
    {
      text: '指南',
      link: '/guide/what-is-f2',
      activeMatch: '/guide/'
    },
    {
      text: 'QA',
      link: '/question-answer/qa',
      activeMatch: '/question-answer/'
    },
    {
      //text: pkg.version,
      text: version,
      items: [
        {
          text: '更新日志',
          link: 'https://github.com/Johnserf-Seed/f2/blob/main/CHANGELOG.md'
        },
        {
          text: '贡献指南',
          link: 'https://github.com/Johnserf-Seed/f2/blob/main/.github/CONTRIBUTING.md'
        }
      ]
    }
  ]
}

function en_nav(): DefaultTheme.NavItem[] {
  return [
    {
      text: 'guide',
      link: '/en/guide/what-is-f2',
      activeMatch: '/guide/'
    },
    {
      //text: pkg.version,
      text: version,
      items: [
        {
          text: 'Changelog',
          link: 'https://github.com/Johnserf-Seed/f2/blob/main/CHANGELOG.md'
        },
        {
          text: 'Contributing',
          link: 'https://github.com/Johnserf-Seed/f2/blob/main/.github/CONTRIBUTING.md'
        }
      ]
    }
  ]
}
