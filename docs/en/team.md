---
layout: page
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
    title: 'Creator',
    links: [
      { icon: 'github', link: 'https://github.com/Johnserf-Seed', ariaLabel: 'GitHub' },
      { icon: 'discord', link: 'https://discord.gg/3PhtPmgHf8', ariaLabel: 'Discord' },
    ],
    sponsor: "https://patreon.com/F2_pypi",
    actionText: ""
  },
]

const contributors = [
  {
    avatar: 'https://avatars.githubusercontent.com/in/29110',
    name: 'dependabot[bot]',
    title: 'Contributor',
    links: [
      { icon: 'github', link: 'https://github.com/apps/dependabot', ariaLabel: 'GitHub Dependa Bot' },
    ]
  },
  {
    avatar: 'https://avatars.githubusercontent.com/in/57789',
    name: 'github-advanced-security[bot]',
    title: 'Contributor',
    links: [
      { icon: 'github', link: 'https://github.com/apps/github-advanced-security', ariaLabel: 'Github Advanced Security' },
    ]
  },
  {
    avatar: 'https://avatars.githubusercontent.com/u/28860556',
    name: 'LRTFK',
    title: 'Contributor',
    links: [
      { icon: 'github', link: 'https://github.com/LRTFK', ariaLabel: 'GitHub LRTFK' },
    ]
  },
]

const sponsors = [
  {
    avatar: 'https://avatars.githubusercontent.com/u/119824398',
    name: 'TikHub',
    title: 'Sponsor',
    links: [
      { icon: 'github', link: 'https://github.com/TikHub', ariaLabel: 'GitHub TikHub' },
    ]
  },
]

</script>

<VPTeamPage>
  <VPTeamPageTitle>
    <template #title>
      Our Team
    </template>
    <template #lead>
      The development of F2 is guided by an self team, some of whom to be featured below.
    </template>
  </VPTeamPageTitle>
  <VPTeamMembers size="medium" :members="coreMembers" />

  <VPTeamPageSection>
    <template #title>Contributors</template>
    <template #lead>
      Below are some of the people who have contributed to the development of F2.
    </template>
    <template #members>
      <VPTeamMembers size="small" :members="contributors" />
    </template>
  </VPTeamPageSection>

  <VPTeamPageSection>
    <template #title>Sponsors</template>
    <template #lead>
      These are the people who have sponsored the development of F2.
    </template>
    <template #members>
      <VPTeamMembers size="small" :members="sponsors" />
    </template>
  </VPTeamPageSection>
</VPTeamPage>