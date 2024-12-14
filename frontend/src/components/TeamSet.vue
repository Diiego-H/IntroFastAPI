<template>
  <div class="card-deck">
    <team v-for="(team) in data" :key="team.id" v-bind="team"></team>
  </div>
</template>

<script>
import Team from './Team.vue'
import TeamService from '../services/TeamService.js'

export default {
  name: 'TeamSet',
  components: { 'team': Team },
  data () {
    return {
      data: [],
      count: 0
    }
  },
  mounted () {
    // Get data from service
    TeamService.getAll().then(response => {
      this.data = response.data
      this.count = response.count
    })
  }
}
</script>
