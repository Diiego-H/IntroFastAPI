import http from '../http-form-urlencoded'

class AuthService {
  getToken (email, password) {
    const parameters = 'username=' + email + '&password=' + password
    return http.post('/api/v1/login/access-token', parameters)
      .then((res) => {
        return res.data
      })
  }
}

export default new AuthService()
