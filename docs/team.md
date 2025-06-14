---
layout: page
title: 认识我们的团队
description: F2 的开发由一个自我团队指导。
sidebar: false
---
<script setup>
import {
  VPTeamPage,
  VPTeamPageTitle,
  VPTeamMembers,
  VPTeamPageSection,
} from 'vitepress/theme'

const coreMembers = [
  {
    avatar: 'https://avatars.githubusercontent.com/u/40727745',
    name: 'JohnserfSeed',
    title: '主创者',
    links: [
      { icon: 'github', link: 'https://github.com/Johnserf-Seed', ariaLabel: 'GitHub' },
      { icon: 'discord', link: 'https://discord.gg/3PhtPmgHf8', ariaLabel: 'Discord' },
    ],
    sponsor: "https://patreon.com/F2_pypi",
    actionText: "赞助"
  },
]

const partners = [
  {
    avatar: 'https://avatars.githubusercontent.com/in/29110',
    name: 'dependabot[bot]',
    title: '贡献者',
    links: [
      { icon: 'github', link: 'https://github.com/apps/dependabot', ariaLabel: 'GitHub Dependa Bot' },
    ]
  },
  {
    avatar: 'https://avatars.githubusercontent.com/in/57789',
    name: 'github-advanced-security[bot]',
    title: '贡献者',
    links: [
      { icon: 'github', link: 'https://github.com/apps/github-advanced-security', ariaLabel: 'Github Advanced Security' },
    ]
  },
  {
    avatar: 'https://avatars.githubusercontent.com/u/28860556',
    name: 'LRTFK',
    title: '贡献者',
    links: [
      { icon: 'github', link: 'https://github.com/LRTFK', ariaLabel: 'GitHub LRTFK' },
    ]
  },
  {
    avatar: 'https://avatars.githubusercontent.com/in/1144995',
    name: 'Codex',
    title: '贡献者',
    links: [
      { icon: 'github', link: 'https://github.com/apps/chatgpt-connector', ariaLabel: 'GitHub ChatGPT Connector' },
    ]
  },
]

const sponsors = [
  {
    avatar: 'https://avatars.githubusercontent.com/u/119824398',
    name: 'TikHub',
    title: '赞助者',
    links: [
      { icon: 'github', link: 'https://github.com/TikHub', ariaLabel: 'GitHub TikHub' },
    ]
  },
]

</script>

<VPTeamPage>
  <VPTeamPageTitle>
    <template #title>
      开发团队
    </template>
    <template #lead>
      F2 的开发由一个自我团队指导，其中一些人将在下文中介绍。
    </template>
  </VPTeamPageTitle>
  <VPTeamMembers size="medium" :members="coreMembers" />

  <VPTeamPageSection>
    <template #title>贡献者</template>
    <template #lead>
      以下是为 F2 的发展做出贡献的贡献者。
    </template>
    <template #members>
      <VPTeamMembers size="small" :members="partners" />
    </template>
  </VPTeamPageSection>

  <VPTeamPageSection>
    <template #title>赞助者</template>
    <template #lead>
      以下是为 F2 的发展做出贡献的赞助者。
    </template>
    <template #members>
      <VPTeamMembers size="small" :members="sponsors" />
    </template>
   </VPTeamPageSection>
</VPTeamPage>
