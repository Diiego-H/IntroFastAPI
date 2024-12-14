import http from '../http-common.js'

class RegisterService {
  registerUser (email, password) {
    return http.post('/api/v1/account/', {'email': email, 'password': password})
      .then((res) => {
        return res.data
      })
  }
}

export default new RegisterService()
