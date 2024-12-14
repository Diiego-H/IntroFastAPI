<template>
  <div class="bg-white">
    <img v-if="match.competition.sport === 'Football'" src="@/assets/football.png" style="max-width: 100%"/>
    <img v-else-if="match.competition.sport === 'Volleyball'" src="@/assets/volleyball.jpg"
         style="max-width: 100%"/>
    <img v-else-if="match.competition.sport === 'Basketball'" src="@/assets/basketball.jpg"
         style="max-width: 100%"/>
    <img v-else-if="match.competition.sport === 'Futsal'" src="@/assets/futsal.png" style="max-width: 100%"/>
    <div class="bg-white" style="padding: 10px">
      <h5 style="font-size: 1.5em">{{match.competition.sport}} - {{match.competition.category}}</h5>
      <p style="margin-bottom: 5px">{{match.competition.name}}</p>
      <p style="margin-bottom: 5px">
        <strong>{{match.local.name}}</strong> ({{match.local.country}}) vs
        <strong>{{match.visitor.name}}</strong> ({{match.visitor.country}})
      </p>
      <p style="margin-bottom: 5px">{{match.date}}</p>
      <p style="margin-bottom: 5px">{{match.price}}€</p>
      <p style="margin-bottom: 5px">Entrades disponibles: {{match.tickets}}</p>
      <button v-if="logged" type="button" class="btn btn-sm btn-success" style="margin-top: 10px" @click="addToCart"
              :disabled="isInCart || match.tickets == 0">
        Afegeix a la Cistella
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Match',
  props: ['match', 'isInCart', 'logged'],
  methods: {
    addToCart () {
      this.$emit('add-to-cart', this.match)
    }
  }
}
</script>
