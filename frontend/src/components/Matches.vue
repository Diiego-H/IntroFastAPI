<template>
  <div id="app" class="m-0">
    <div class="bg-white d-flex justify-content-between px-5 py-4 border-bottom border-dark">
      <h1 class="title m-0">Partits</h1>
      <div class="user-info">
        <div v-if="logged" class="email-box">
          <i class="fas fa-user"></i> <!-- User icon -->
          <span>{{ email }}</span>
        </div>
        <div v-if="logged" class="money-box">
          <i class="fas fa-coins"></i> <!-- Money icon -->
          <span>{{ money }}€</span>
        </div>
        <button v-if="isShowingCart && logged" @click="closeCart" type="button" class="btn btn-outline-primary">
          Tanca Cistella
        </button>
        <button v-if="!isShowingCart && logged" @click="openCart" type="button" class="btn btn-outline-primary">
          Obre Cistella
        </button>
        <button v-if="logged" @click="logOut" type="button" class="btn btn-outline-success log-out">
          Log Out
        </button>
        <button v-else @click="logIn" type="button" class="btn btn-outline-success">
          Log In
        </button>
      </div>
    </div>

    <div v-if="isShowingCart" class="container">
      <div class="main-content p-5 justify-content-between align-items-center" style="background-color: #FBECE2;">
        <div class="bg-white p-5 justify-content-between align-items-center">
          <h2>Cistella</h2>
          <table v-if="orderMatches.length > 0" class="table table-sm">
            <thead>
              <tr>
                <th scope="col" class="col-1">Esport</th>
                <th scope="col" class="col-2">Competició</th>
                <th scope="col" class="col-4">Partit</th>
                <th scope="col">Quantitat</th>
                <th scope="col">Preu (&euro;)</th>
                <th scope="col">Total (&euro;)</th>
                <th scope="col" class="col-2"></th>
              </tr>
            </thead>
            <tbody>
              <order-match v-for="(match) in orderMatches" :key="match.id" v-bind="match"
                           @remove-from-cart="removeFromCart"
                           @update-quantity="updateQuantity"></order-match>
            </tbody>
          </table>
          <div v-else class="text-center empty-cart">
            <img src="@/assets/empty_cart.jpg" alt="Empty cart" class="empty-cart-image"/>
            <p class="mb-0">La Cistella Està Buida</p>
          </div>
          <div v-if="orderMatches.length > 0" class="mt-4">
            <h3>Preu Final: {{ totalPrice }}€</h3>
          </div>
          <div class="mt-4">
            <button type="button" @click="closeCart" class="btn btn-secondary">Enrere</button>
            <button v-if="orderMatches.length > 0" type="button" class="btn btn-success" @click="finalizePurchase">
              Finalitzar la Compra
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="container">
      <div class="main-content p-5 align-items-center" style="background-color: #FBECE2;">
        <div class="align-items-center">
          <!-- Create rows with flexbox -->
          <div class="match-row">
            <match class="match" v-for="match in matches" :key="match.id" :match="match"
                   :isInCart="isInCart(match.id)" :logged="logged" @add-to-cart="addToCart"></match>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MatchService from '../services/MatchService.js'
import MoneyService from '../services/MoneyService.js'
import OrderMatch from './OrderMatch.vue'
import Match from './Match.vue'

export default {
  components: { 'order-match': OrderMatch, 'match': Match },
  data () {
    return {
      orderMatches: [],
      matches: [],
      logged: false,
      isShowingCart: false,
      money: 0,
      email: '',
      token: '',
      // Initialize totalPrice
      totalPrice: 0
    }
  },
  methods: {
    logIn () {
      this.$router.push({ path: '/userLogin' })
    },
    logOut () {
      this.orderMatches = []
      this.logged = false
      this.isShowingCart = false
      this.$router.push({ path: '/' })
      localStorage.clear()
    },
    openCart () {
      this.isShowingCart = true
    },
    closeCart () {
      this.isShowingCart = false
    },
    addToCart (match) {
      // Check if the match is already in the cart
      if (!this.isInCart(match.id)) {
        // Initialize quantity if it's a new item
        this.$set(match, 'quantity', 1)
        this.orderMatches.push(match)
        // Recalculate total price
        this.calculateTotalPrice()
      }
    },
    removeFromCart (match) {
      this.orderMatches = this.orderMatches.filter(orderMatch => orderMatch.id !== match.id)
      // Recalculate total price
      this.calculateTotalPrice()
    },
    isInCart (id) {
      return this.orderMatches.some(orderMatch => orderMatch.id === id)
    },
    updateQuantity ({ id, quantity }) {
      const match = this.orderMatches.find(orderMatch => orderMatch.id === id)
      if (match) {
        match.quantity = quantity
        // Recalculate total price
        this.calculateTotalPrice()
      }
    },
    calculateTotalPrice () {
      this.totalPrice = this.orderMatches.reduce((sum, match) => sum + match.price * match.quantity, 0)
    },
    finalizePurchase () {
      const purchaseData = this.orderMatches.map(match => ({
        match_id: match.id,
        num_tickets: match.quantity
      }))

      this.token = localStorage.token
      MatchService.purchase(this.token, purchaseData)
        .then(response => {
          alert('Purchase successful!')
          this.orderMatches = []
          this.totalPrice = 0
          this.isShowingCart = false
          MatchService.getAll().then(response => {
            this.matches = response.matches
          })
          this.getMoney()
        })
        .catch(error => {
          // Extract and display the error message
          const errorMessage = error.response && error.response.data && error.response.data.detail
            ? error.response.data.detail
            : 'Purchase failed. Please try again.'
          alert(errorMessage)
          console.error(error)
        })
    },
    async validateToken () {
      try {
        await MatchService.testToken()
      } catch (error) {
        alert('Your session has expired, log in again.')
        this.logOut()
      }
    },
    getMoney () {
      // Get money in account
      MoneyService.getMoney(this.token).then(response => {
        this.money = parseFloat(response.money).toFixed(2)
      }).catch((error) => {
        console.error(error)
        // Shown when the token is invalid, session will expire
        this.money = 0
      })
    }
  },
  mounted () {
    // Get data from service
    MatchService.getAll().then(response => {
      this.matches = response.matches
    })
  },
  created () {
    // User authorization (using local storage)
    this.logged = localStorage.logged === 'true'
    if (localStorage.token) {
      this.token = localStorage.token
      this.getMoney()
    }
    if (localStorage.email) {
      this.email = localStorage.email
    }
    if (this.logged) {
      this.validateToken()
    }
  }
}
</script>

<style>
.match-row {
  display: flex;
  flex-wrap: wrap;
  column-gap: 20px;
  row-gap: 40px;
  justify-content: space-between;
}

.match {
  width: 250px; /* Adjust width as needed */
}

.empty-cart {
  margin-top: 40px;
}

.empty-cart-image {
  width: 150px;
  height: auto;
  margin-bottom: 20px;
}

.user-info {
  display: flex;
  align-items: center;
}

.email-box, .money-box {
  font-weight: bold;
  margin-right: 30px;
  display: flex;
  align-items: center;
}

.email-box i, .money-box i {
  margin-right: 5px;
}

.money-box i {
  margin-right: 5px;
  color: #fcba03;
}

.log-out {
  margin-left: 10px;
}
</style>
