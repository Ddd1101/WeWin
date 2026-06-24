package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class LoginResponse(
    val token: String,
    val user: UserInfo
)

@Serializable
data class UserInfo(
    val id: Int,
    val username: String,
    val user_type: String? = null,
    val email: String? = null,
    val phone: String? = null,
    val real_name: String? = null,
    val company_id: Int? = null,
    val company_name: String? = null
)
