
import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import Layout from './Layout.vue'
import './styles/vars.css'


export default {
  extends: DefaultTheme,
  Layout: Layout,
}
