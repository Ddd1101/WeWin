package com.wewin.app.ui.login

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.wewin.app.data.local.TokenStore
import com.wewin.app.data.remote.RetrofitClient
import com.wewin.app.data.remote.dto.ErrorResponse
import com.wewin.app.data.remote.dto.LoginRequest
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import java.io.IOException

data class LoginUiState(
    val username: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val error: String? = null,
    val loginSuccess: Boolean = false
)

class LoginViewModel(
    private val tokenStore: TokenStore
) : ViewModel() {

    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
    }

    fun updateUsername(value: String) {
        _uiState.update { it.copy(username = value, error = null) }
    }

    fun updatePassword(value: String) {
        _uiState.update { it.copy(password = value, error = null) }
    }

    fun login() {
        val current = _uiState.value
        if (current.isLoading) return
        _uiState.update { it.copy(isLoading = true, error = null) }
        viewModelScope.launch {
            try {
                val response = RetrofitClient.apiService.login(
                    LoginRequest(current.username, current.password)
                )
                if (response.isSuccessful) {
                    val body = response.body()
                    if (body != null) {
                        tokenStore.saveAuth(body.token, body.user)
                        _uiState.update { it.copy(isLoading = false, loginSuccess = true) }
                    } else {
                        _uiState.update { it.copy(isLoading = false, error = "登录响应为空") }
                    }
                } else {
                    val errorMsg = parseError(response.code(), response.errorBody()?.string())
                    _uiState.update { it.copy(isLoading = false, error = errorMsg) }
                }
            } catch (e: IOException) {
                _uiState.update { it.copy(isLoading = false, error = "网络连接失败，请检查网络") }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = "登录失败：${e.message ?: "未知错误"}"
                    )
                }
            }
        }
    }

    private fun parseError(code: Int, errorBody: String?): String {
        if (errorBody.isNullOrEmpty()) {
            return httpErrorMessage(code)
        }
        return try {
            val errorResponse = json.decodeFromString(ErrorResponse.serializer(), errorBody)
            errorResponse.error ?: "登录失败"
        } catch (e: Exception) {
            httpErrorMessage(code)
        }
    }

    private fun httpErrorMessage(code: Int): String {
        return when (code) {
            401 -> "用户名或密码错误"
            403 -> "没有访问权限"
            404 -> "接口不存在"
            in 500..599 -> "服务器错误，请稍后重试"
            else -> "登录失败（$code）"
        }
    }

    companion object {
        fun provideFactory(tokenStore: TokenStore): ViewModelProvider.Factory =
            viewModelFactory {
                initializer {
                    LoginViewModel(tokenStore)
                }
            }
    }
}
