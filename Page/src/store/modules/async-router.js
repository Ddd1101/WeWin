/**
 * 使用静态路由配置
 */
import { constantRouterMap, asyncRouterMap } from '@/config/router.config'

const permission = {
  state: {
    routers: constantRouterMap,
    addRouters: []
  },
  mutations: {
    SET_ROUTERS: (state, routers) => {
      state.addRouters = routers
      state.routers = constantRouterMap.concat(routers)
    }
  },
  actions: {
    GenerateRoutes ({ commit }, data) {
      return new Promise((resolve) => {
        const accessedRouters = asyncRouterMap
        commit('SET_ROUTERS', accessedRouters)
        resolve()
      })
    }
  }
}

export default permission
