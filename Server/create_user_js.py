content = '''import storage from 'store'
import expirePlugin from 'store/plugins/expire'
import { login, getInfo, logout } from '@/api/accounts'
import { ACCESS_TOKEN } from '@/store/mutation-types'
import { welcome } from '@/utils/util'

storage.addPlugin(expirePlugin)
const user = {
  state: {
    token: '',
    name: '',
    welcome: '',
    avatar: '',
    roles: [],
    info: {},
    userType: ''
  },

  mutations: {
    SET_TOKEN: (state, token) => {
      state.token = token
    },
    SET_NAME: (state, { name, welcome }) => {
      state.name = name
      state.welcome = welcome
    },
    SET_AVATAR: (state, avatar) => {
      state.avatar = avatar
    },
    SET_ROLES: (state, roles) => {
      state.roles = roles
    },
    SET_INFO: (state, info) => {
      state.info = info
    },
    SET_USER_TYPE: (state, userType) => {
      state.userType = userType
    }
  },

  actions: {
    Login ({ commit }, userInfo) {
      return new Promise((resolve, reject) => {
        login(userInfo).then(response => {
          const result = response
          storage.set(ACCESS_TOKEN, 'session', new Date().getTime() + 7 * 24 * 60 * 60 * 1000)
          commit('SET_TOKEN', 'session')
          commit('SET_INFO', result)
          commit('SET_NAME', { name: result.username || result.first_name, welcome: welcome() })
          commit('SET_AVATAR', result.avatar || '')
          commit('SET_USER_TYPE', result.user_type)
          commit('SET_ROLES', [result.user_type])
          resolve(result)
        }).catch(error => {
          reject(error)
        })
      })
    },

    GetInfo ({ commit }) {
      return new Promise((resolve, reject) => {
        getInfo().then(response => {
          const result = response
          commit('SET_INFO', result)
          commit('SET_NAME', { name: result.username || result.first_name, welcome: welcome() })
          commit('SET_AVATAR', result.avatar || '')
          commit('SET_USER_TYPE', result.user_type)
          commit('SET_ROLES', [result.user_type])
          resolve(result)
        }).catch(error => {
          reject(error)
        })
      })
    },

    Logout ({ commit, state }) {
      return new Promise((resolve) => {
        logout().then(() => {
          commit('SET_TOKEN', '')
          commit('SET_ROLES', [])
          commit('SET_INFO', {})
          storage.remove(ACCESS_TOKEN)
          resolve()
        }).catch((err) => {
          console.log('logout fail:', err)
        }).finally(() => {
        })
      })
    }

  }
}

export default user
'''

with open(r'd:\workplace_shop\WeWin\Page\src\store\modules\user.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("user.js file created successfully!")
