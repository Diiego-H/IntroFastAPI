import http from '../http-common'

class MatchService {
  getAll () {
    return http.get('/api/v1/matches/')
      .then((res) => {
        return res.data
      })
  }

  purchase (token, purchaseData) {
    return http.post('/api/v1/orders/purchase/', { matches: purchaseData },
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )
      .then((res) => {
        return res.data
      })
  }

  testToken () {
    const token = localStorage.getItem('token')
    return http.post('/api/v1/login/test-token', {}, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }).then((res) => {
      return res.data
    })
  }
}

export default new MatchService()
