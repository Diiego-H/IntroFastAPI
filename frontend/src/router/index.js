import Vue from 'vue'
import Router from 'vue-router'
import Matches from '@/components/Matches'
import TeamSet from '@/components/TeamSet'
import Login from '@/components/Login'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Matches',
      component: Matches
    },
    {
      path: '/teams',
      name: 'TeamSet',
      component: TeamSet
    },
    {
      path: '/userlogin',
      name: 'Login',
      component: Login
    }
  ]
})
