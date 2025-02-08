import { createRequire } from 'module'
import { defineConfig, type DefaultTheme } from 'vitepress'

const require = createRequire(import.meta.url)

const pkg = require('../package.json')

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "F2",
  description: "Fast 2 Every",
  base: "/",
  lastUpdated: true,
  cleanUrls: true,

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/f2-logo-with-shadow-svg@0.25x.svg' }],
    ['link', { rel: 'icon', type: 'image/png', href: '/f2-logo-with-shadow-mini.png' }],
    ['link', { rel: 'icon', type: 'image/x-icon', href: '/f2-logo.ico' }],
    // google analytics
    ['script', { async: '', src: 'https://www.googletagmanager.com/gtag/js?id=G-H7N87QED9C' }],
    [
      'script',
      {},
      `window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-H7N87QED9C');`,
    ],
    ['link', { rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/firacode@6.2.0/distr/fira_code.css' }],
  ],
  markdown: {
    // lineNumbers: true
  },
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    logo: { src: '/f2-logo-with-shadow-svg@1.0x.svg', width: 24, height: 24 },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Johnserf-Seed/f2', ariaLabel: 'GitHub' },
      { icon: 'discord', link: 'https://discord.gg/3PhtPmgHf8', ariaLabel: 'Discord' },
      { icon: 'gmail', link: 'mailto:support@f2.wiki', ariaLabel: 'Email' },
    ],
    algolia: {
      appId: '30ELZ9F504',
      apiKey: 'f252ef8a7175f8801c302df716c7e06d',
      indexName: 'f2'
    },
    footer: {
      message: 'Released under the Apache-2.0 license.',
      copyright: 'Copyright © 2023-present Johnserf Seed'
    },
    editLink: {
      pattern: 'https://github.com/Johnserf-Seed/f2/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    },
  },

  locales: {
    root: {
      label: '简体中文',
      lang: 'zh',
      themeConfig: {
        nav: cn_nav(),
        sidebar: {
          '/': [
            {
              text: '快速入门',
              items: [
                { text: '安装', link: '/install' },
                { text: '快速使用', link: '/quick-start' },
                { text: '配置文件', link: '/site-config' },
                { text: '命令行', link: '/cli' },
                { text: '进阶用法', link: '/advance-guide' },
              ],
            },
            {
              text: 'FAQ',
              items: [
                { text: '高频问题', link: '/faq' },
              ],
            },
          ],
          '/guide/': [
            {
              text: '什么是F2',
              items: [{ text: '开发者必看', link: '/guide/what-is-f2' }],
            },
            {
              text: 'API示例',
              items: [{ text: '使用示例', link: '/guide/api-examples' }],
            },
            {
              text: '开发者接口',
              items: [
                { text: 'Bark', link: '/guide/apps/bark/overview' },
                { text: 'DouYin', link: '/guide/apps/douyin/overview' },
                { text: 'TikTok', link: '/guide/apps/tiktok/overview' },
                { text: 'Twitter', link: '/guide/apps/twitter/overview' },
                { text: 'WeiBo', link: '/guide/apps/weibo/overview' },
              ],
            },
            {
              text: '命令行指引',
              items: [
                { text: 'Bark', link: '/guide/apps/bark/cli' },
                { text: 'DouyYin', link: '/guide/apps/douyin/cli' },
                { text: 'TikTok', link: '/guide/apps/tiktok/cli' },
                { text: 'Twitter', link: '/guide/apps/twitter/cli' },
                { text: 'WeiBo', link: '/guide/apps/weibo/cli' },
              ],
            },
          ],
        },
      },
    },

    en: {
      label: 'English',
      lang: 'en',
      themeConfig: {
        nav: en_nav(),
        sidebar: {
          '/en/': [
            {
              text: 'Quick Start',
              items: [
                { text: 'Install', link: '/en/install' },
                { text: 'Quick Start', link: '/en/quick-start' },
                { text: 'Site Config', link: '/en/site-config' },
                { text: 'CLI', link: '/en/cli' },
                { text: 'Advance Guide', link: '/en/advance-guide' },
              ],
            },
            {
              text: 'FAQ',
              items: [
                { text: 'Frequently Asked Questions', link: '/en/faq' },
              ],
            },
          ],
          '/en/guide/': [
            {
              text: 'What is F2',
              items: [{ text: 'For Developers', link: '/en/guide/what-is-f2' }],
            },
            {
              text: 'API Examples',
              items: [{ text: 'API Examples', link: '/en/guide/api-examples' }],
            },
            {
              text: 'Developer API',
              items: [
                { text: 'Bark', link: '/en/guide/apps/bark/index' },
                { text: 'DouYin', link: '/en/guide/apps/douyin/overview' },
                { text: 'TikTok', link: '/en/guide/apps/tiktok/overview' },
                { text: 'Twitter', link: '/en/guide/apps/twitter/overview' },
                { text: 'WeiBo', link: '/en/guide/apps/weibo/overview' },
              ],
            },
            {
              text: 'CLI Guide',
              items: [
                { text: 'Bark', link: '/en/guide/apps/bark/cli' },
                { text: 'DouyYin', link: '/en/guide/apps/douyin/cli' },
                { text: 'TikTok', link: '/en/guide/apps/tiktok/cli' },
                { text: 'Twitter', link: '/en/guide/apps/twitter/cli' },
                { text: 'WeiBo', link: '/en/guide/apps/weibo/cli' },
              ],
            },
          ],
        },
      },
    },
  },
})

function cn_nav(): DefaultTheme.NavItem[] {
  return [
    {
      text: '开发者接口',
      items: [
        { text: 'Bark', link: '/guide/apps/bark/overview', activeMatch: '/bark/overview' },
        { text: 'DouYin', link: '/guide/apps/douyin/overview', activeMatch: '/douyin/overview' },
        { text: 'TikTok', link: '/guide/apps/tiktok/overview', activeMatch: '/tiktok/overview' },
        { text: 'Twitter', link: '/guide/apps/twitter/overview', activeMatch: '/twitter/overview' },
        { text: 'WeiBo', link: '/guide/apps/weibo/overview', activeMatch: '/weibo/overview' },
      ],
    },
    {
      text: '命令行指引',
      items: [
        { text: 'Bark', link: '/guide/apps/bark/cli', activeMatch: '/bark/cli' },
        { text: 'DouYin', link: '/guide/apps/douyin/cli', activeMatch: '/douyin/cli' },
        { text: 'TikTok', link: '/guide/apps/tiktok/cli', activeMatch: '/tiktok/cli' },
        { text: 'Twitter', link: '/guide/apps/twitter/cli', activeMatch: '/twitter/cli' },
        { text: 'WeiBo', link: '/guide/apps/weibo/cli', activeMatch: '/weibo/cli' },
      ],
    },
    {
      text: '团队',
      link: '/team',
      activeMatch: '/team'
    },
    {
      text: 'FAQ',
      link: '/faq',
      activeMatch: '/faq'
    },
    {
      text: pkg.f2_version,
      items: [
        {
          text: '更新日志',
          link: 'https://github.com/Johnserf-Seed/f2/blob/main/CHANGELOG.md'
        },
        {
          text: '贡献指南',
          link: 'https://github.com/Johnserf-Seed/f2/blob/main/CONTRIBUTING.md'
        }
      ]
    },
  ]
}

function en_nav(): DefaultTheme.NavItem[] {
  return [
    {
      text: 'Developer API',
      items: [
        { text: 'Bark', link: '/en/guide/apps/bark/index', activeMatch: '/bark/index' },
        { text: 'DouYin', link: '/en/guide/apps/douyin/overview', activeMatch: '/douyin/overview' },
        { text: 'TikTok', link: '/en/guide/apps/tiktok/overview', activeMatch: '/tiktok/overview' },
        { text: 'Twitter', link: '/en/guide/apps/twitter/overview', activeMatch: '/twitter/overview' },
        { text: 'WeiBo', link: '/en/guide/apps/weibo/overview', activeMatch: '/weibo/overview' },
      ],
    },
    {
      text: 'CLI Guide',
      items: [
        { text: 'Bark', link: '/en/guide/apps/bark/cli', activeMatch: '/bark/cli' },
        { text: 'DouYin', link: '/en/guide/apps/douyin/cli', activeMatch: '/douyin/cli' },
        { text: 'TikTok', link: '/en/guide/apps/tiktok/cli', activeMatch: '/tiktok/cli' },
        { text: 'Twitter', link: '/en/guide/apps/twitter/cli', activeMatch: '/twitter/cli' },
        { text: 'WeiBo', link: '/en/guide/apps/weibo/cli', activeMatch: '/weibo/cli' },
      ],
    },
    {
      text: 'Team',
      link: '/en/team',
      activeMatch: '/en/team'
    },
    {
      text: 'FAQ',
      link: '/en/faq',
      activeMatch: '/en/faq'
    },
    {
      text: pkg.f2_version,
      items: [
        {
          text: 'Changelog',
          link: 'https://github.com/Johnserf-Seed/f2/blob/main/CHANGELOG.md'
        },
        {
          text: 'Contributing',
          link: 'https://github.com/Johnserf-Seed/f2/blob/main/CONTRIBUTING.md'
        }
      ]
    }
  ]
}
