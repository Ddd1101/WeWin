package com.wewin.app.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class UserBriefDto(
    val id: Int,
    val username: String = "",
    @SerialName("user_type") val userType: String = "",
    @SerialName("user_type_display") val userTypeDisplay: String = "",
    val email: String = "",
    val phone: String = "",
    @SerialName("real_name") val realName: String = "",
    @SerialName("company_id") val companyId: Int? = null,
    @SerialName("company_name") val companyName: String = "",
    @SerialName("is_active") val isActive: Boolean = true
)

@Serializable
data class UserListResponse(
    val users: List<UserBriefDto> = emptyList()
)
