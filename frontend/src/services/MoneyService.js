import http from '../http-common'

class MoneyService {
  getMoney (token) {
    return http.get('/api/v1/account/money/',
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
}

export default new MoneyService()
