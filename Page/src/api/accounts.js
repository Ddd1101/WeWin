import request from '@/utils/request'

const accountsApi = {
  Login: '/api/accounts/users/login/',
  Logout: '/api/accounts/users/logout/',
  Register: '/api/accounts/users/register/',
  UserInfo: '/api/accounts/users/me/',
  UpdateUserInfo: '/api/accounts/users/update_me/',
  UserList: '/api/accounts/users/',
  EnterpriseList: '/api/accounts/enterprises/'
}

export function login (parameter) {
  return request({
    url: accountsApi.Login,
    method: 'post',
    data: parameter
  })
}

export function logout () {
  return request({
    url: accountsApi.Logout,
    method: 'post'
  })
}

export function register (parameter) {
  return request({
    url: accountsApi.Register,
    method: 'post',
    data: parameter
  })
}

export function getInfo () {
  return request({
    url: accountsApi.UserInfo,
    method: 'get'
  })
}

export function updateInfo (parameter) {
  return request({
    url: accountsApi.UpdateUserInfo,
    method: 'patch',
    data: parameter
  })
}

export function getUserList (parameter) {
  return request({
    url: accountsApi.UserList,
    method: 'get',
    params: parameter
  })
}

export function getUserDetail (id) {
  return request({
    url: `${accountsApi.UserList}${id}/`,
    method: 'get'
  })
}

export function createUser (parameter) {
  return request({
    url: accountsApi.UserList,
    method: 'post',
    data: parameter
  })
}

export function updateUser (id, parameter) {
  return request({
    url: `${accountsApi.UserList}${id}/`,
    method: 'put',
    data: parameter
  })
}

export function deleteUser (id) {
  return request({
    url: `${accountsApi.UserList}${id}/`,
    method: 'delete'
  })
}

export function getEnterpriseList (parameter) {
  return request({
    url: accountsApi.EnterpriseList,
    method: 'get',
    params: parameter
  })
}

export function getEnterpriseDetail (id) {
  return request({
    url: `${accountsApi.EnterpriseList}${id}/`,
    method: 'get'
  })
}

export function createEnterprise (parameter) {
  return request({
    url: accountsApi.EnterpriseList,
    method: 'post',
    data: parameter
  })
}

export function updateEnterprise (id, parameter) {
  return request({
    url: `${accountsApi.EnterpriseList}${id}/`,
    method: 'put',
    data: parameter
  })
}

export function deleteEnterprise (id) {
  return request({
    url: `${accountsApi.EnterpriseList}${id}/`,
    method: 'delete'
  })
}
