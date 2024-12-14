<template>
  <div class="login-container">
    <button @click.prevent="back_matches" class="btn btn-secondary back-button">Back To Matches</button>
    <form class="login-form">
      <div class="form-group">
        <label for="inputEmail">Email</label>
        <input
          type="text"
          id="inputEmail"
          class="form-control"
          placeholder="Email"
          required
          autofocus
          v-model="email"
          @input="validateEmail"
        >
        <div v-if="emailError" class="error-message">{{ emailError }}</div>
      </div>
      <div class="form-group">
        <label for="inputPassword">Password</label>
        <div class="password-container">
          <input
            :type="passwordVisible ? 'text' : 'password'"
            id="inputPassword"
            class="form-control"
            placeholder="Password"
            required
            v-model="password"
          >
          <button
            type="button"
            class="toggle-password"
            @click="togglePasswordVisibility"
          >
            {{ passwordVisible ? 'Hide' : 'Show' }}
          </button>
        </div>
      </div>
      <div class="button-group">
        <button
          @click.prevent="login_user"
          class="btn btn-primary"
          :disabled="isButtonDisabled"
        >
          Sign In
        </button>
        <button
          @click.prevent="register_user"
          class="btn btn-success"
          :disabled="isButtonDisabled"
        >
          Create Account
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import AuthService from '../services/AuthService.js'
import RegisterService from '../services/RegisterService.js'

export default {
  name: 'Login',
  data () {
    return {
      email: null,
      password: null,
      emailError: null,
      passwordVisible: false
    }
  },
  methods: {
    validateEmail () {
      const emailPattern = /^[a-zA-Z0-9._@]+$/
      if (this.email && !emailPattern.test(this.email)) {
        this.emailError = 'Email must be alphanumeric and may contain @, _, and full stops.'
      } else {
        this.emailError = null
      }
    },
    togglePasswordVisibility () {
      this.passwordVisible = !this.passwordVisible
    },
    login_user () {
      // Si l'email és invàlid no fer res.
      if (this.emailError) {
        return
      }
      // Obtenció del token delegat al servei d'autenticació
      AuthService.getToken(this.email, this.password).then(response => {
        localStorage.logged = true
        localStorage.token = response.access_token
        localStorage.email = this.email
        this.$router.push({ path: '/' })
      }).catch((error) => {
        console.error(error)
        alert('Username or Password incorrect')
      })
    },
    register_user () {
      // Si l'email és invàlid no fer res.
      if (this.emailError) {
        return
      }
      // Creació del compte d'usuari delegat a un servei
      RegisterService.registerUser(this.email, this.password).then(response => {
        // Si s'ha creat el compte, loguegem l'usuari
        this.login_user()
      }).catch((error) => {
        console.error(error)
        alert('An account for this email already exists')
      })
    },
    back_matches () {
      this.$router.push({ path: '/' })
    }
  },
  computed: {
    isButtonDisabled () {
      return !this.email || this.emailError || !this.password
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  position: relative;
}

.back-button {
  position: absolute;
  top: 20px;
  left: 20px;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  background-color: #6c757d;
  color: #fff;
}

.login-form {
  width: 300px;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.form-group {
  margin-bottom: 20px;
}

.label {
  font-weight: bold;
}

.input-control {
  width: 100%;
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #ccc;
}

.button-group {
  display: flex;
  justify-content: space-between;
}

.btn {
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}

.btn-primary {
  background-color: #007bff;
  color: #fff;
}

.btn-success {
  background-color: #28a745;
  color: #fff;
}

.btn-secondary {
  background-color: #6c757d;
  color: #fff;
}

.error-message {
  color: red;
  font-size: 0.875em;
  margin-top: 5px;
}

.password-container {
  display: flex;
  align-items: center;
}

.toggle-password {
  margin-left: 10px;
  cursor: pointer;
  background: none;
  border: none;
  color: #007bff;
  padding: 0;
  font-size: 0.875em;
}
</style>
